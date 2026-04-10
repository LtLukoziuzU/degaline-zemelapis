### xlsx format changes
If the header row scan fails to find `'Data'` in column A, do not just show a generic error. Log the first 10 raw rows to the browser console (`console.error('Raw rows:', rows.slice(0, 10))`) before surfacing the user-facing message. This makes it immediately obvious whether ENA changed their format, added a new header row, or renamed the column.

### Failed geocode addresses
See [geocoding-strategy.md](geocoding-strategy.md) for the full failure handling rules.
