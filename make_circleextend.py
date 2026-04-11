"""
Generate _circleextend.png for each _circle.png in modifiedlogo/.
Extends the logo's background color to fill the full circle.
Does NOT modify _circle files.
"""
from PIL import Image, ImageDraw
import numpy as np
from collections import Counter
import os

DIR = 'modifiedlogo'
SIZE = 256
cx, cy, r = SIZE // 2, SIZE // 2, SIZE // 2

Y_GRID, X_GRID = np.mgrid[0:SIZE, 0:SIZE]
INSIDE_CIRCLE = (X_GRID - cx) ** 2 + (Y_GRID - cy) ** 2 <= r ** 2

CIRCLE_MASK = Image.new('L', (SIZE, SIZE), 0)
ImageDraw.Draw(CIRCLE_MASK).ellipse([0, 0, SIZE - 1, SIZE - 1], fill=255)


def detect_bg_color(arr):
    """
    Detect background color from a _circle image.
    Returns (r,g,b) if a dominant solid bg is found, else None.
    Strategy: find the most common non-artifact-black opaque color inside
    the circle. If it dominates ≥50% of all non-black pixels, it's the bg.
    """
    opaque = INSIDE_CIRCLE & (arr[:, :, 3] > 200)
    pixels = arr[opaque, :3].astype(int)
    if len(pixels) == 0:
        return None

    is_near_black = (pixels[:, 0] < 15) & (pixels[:, 1] < 15) & (pixels[:, 2] < 15)
    non_black = pixels[~is_near_black]

    if len(non_black) < 0.03 * len(pixels):
        # Overwhelmingly black — real black background
        return (0, 0, 0)

    quantized = (non_black // 8) * 8
    counts = Counter(map(tuple, quantized.tolist()))
    top_color, top_cnt = counts.most_common(1)[0]

    is_near_white = all(c > 200 for c in top_color)
    threshold = 0.30 if is_near_white else 0.50

    if top_cnt / len(non_black) >= threshold:
        return tuple(int(c) for c in top_color)

    return None  # No clear solid background


def make_filled_circle(color_rgb):
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([0, 0, SIZE - 1, SIZE - 1], fill=(*color_rgb, 255))
    return img


def make_filled_circle_junasa():
    """Blue top half, yellow bottom half, clipped to circle."""
    arr = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    SPLIT_ROW = 126
    arr[INSIDE_CIRCLE & (Y_GRID < SPLIT_ROW)] = (0, 91, 190, 255)
    arr[INSIDE_CIRCLE & (Y_GRID >= SPLIT_ROW)] = (255, 214, 0, 255)
    return Image.fromarray(arr)


def deartifact(arr):
    """Replace (≈0,0,0,255) artifact pixels inside circle with transparent."""
    result = arr.copy()
    artifact = (
        INSIDE_CIRCLE
        & (arr[:, :, 0] < 15)
        & (arr[:, :, 1] < 15)
        & (arr[:, :, 2] < 15)
        & (arr[:, :, 3] > 200)
    )
    result[artifact] = [0, 0, 0, 0]
    return result


def process(filename):
    name = filename.replace('_circle.png', '')
    path = os.path.join(DIR, filename)
    circle_img = Image.open(path).convert('RGBA')
    arr = np.array(circle_img)

    if name == 'junasa':
        bg = make_filled_circle_junasa()
        result = Image.alpha_composite(bg, Image.fromarray(deartifact(arr)))
        result.save(os.path.join(DIR, f'{name}_circleextend.png'))
        print(f'  {name} [blue/yellow split]')
        return

    bg_color = detect_bg_color(arr)

    if bg_color is None:
        # No clear background — copy circle as-is
        circle_img.save(os.path.join(DIR, f'{name}_circleextend.png'))
        print(f'  {name} [no solid bg — copied]')
        return

    if bg_color == (0, 0, 0):
        # Genuine black background — copy circle as-is
        circle_img.save(os.path.join(DIR, f'{name}_circleextend.png'))
        print(f'  {name} [black bg — copied]')
        return

    bg = make_filled_circle(bg_color)
    clean = Image.fromarray(deartifact(arr))
    result = Image.alpha_composite(bg, clean)
    result.save(os.path.join(DIR, f'{name}_circleextend.png'))
    print(f'  {name} [bg={bg_color}]')


files = sorted(f for f in os.listdir(DIR) if f.endswith('_circle.png'))
print(f'Processing {len(files)} logos...')
for f in files:
    process(f)
print('Done.')
