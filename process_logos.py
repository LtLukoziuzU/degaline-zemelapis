"""
Generate circle, square, and rectangle variants of each logo in originallogo/.
No color/alpha/background changes — only resize and crop to uniform shapes.
Output: modifiedlogo/{name}_circle.png, {name}_square.png, {name}_rectangle.png
"""
from PIL import Image, ImageDraw
import os

SRC = 'originallogo'
DST = 'modifiedlogo'
os.makedirs(DST, exist_ok=True)

SQUARE_SIZE = 256
CIRCLE_SIZE = 256
RECT_W, RECT_H = 384, 192
PADDING = 0.10


def fit_onto_canvas(img, canvas_w, canvas_h):
    """Resize image to fit within canvas (with padding), centered. Transparent canvas."""
    max_w = int(canvas_w * (1 - 2 * PADDING))
    max_h = int(canvas_h * (1 - 2 * PADDING))
    logo = img.copy().convert('RGBA')
    logo.thumbnail((max_w, max_h), Image.LANCZOS)
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    x = (canvas_w - logo.width) // 2
    y = (canvas_h - logo.height) // 2
    canvas.paste(logo, (x, y), logo)
    return canvas


def make_square(img):
    return fit_onto_canvas(img, SQUARE_SIZE, SQUARE_SIZE)


def make_rectangle(img):
    return fit_onto_canvas(img, RECT_W, RECT_H)


def make_circle(img):
    base = fit_onto_canvas(img, CIRCLE_SIZE, CIRCLE_SIZE)
    mask = Image.new('L', (CIRCLE_SIZE, CIRCLE_SIZE), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, CIRCLE_SIZE - 1, CIRCLE_SIZE - 1], fill=255)
    base.putalpha(mask)
    return base


def process(filename):
    name, _ = os.path.splitext(filename)
    img = Image.open(os.path.join(SRC, filename))
    if img.mode == 'P':
        img = img.convert('RGBA')

    make_square(img).save(os.path.join(DST, f'{name}_square.png'))
    make_rectangle(img).save(os.path.join(DST, f'{name}_rectangle.png'))
    make_circle(img).save(os.path.join(DST, f'{name}_circle.png'))
    print(f'  {name}')


files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(('.png', '.jpg', '.jpeg')))
print(f'Processing {len(files)} logos...')
for f in files:
    process(f)
print('Done.')
