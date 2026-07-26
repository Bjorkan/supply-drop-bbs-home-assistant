# Changelog

## 0.12.0-1

- Avoid Home Assistant Supervisor's failing ranged-integer option validation.
- Preserve the same numeric limits in the App's own configuration generator.
- Improve invalid-number errors by naming the affected option and accepted range.

## 0.12.0

Initial Home Assistant App packaging of Supply Drop BBS 0.12.0.

Upstream highlights:

- applies the full radio configuration on every connect before other radio operations;
- broadcasts a self-advert on connect and every 24 hours;
- exposes configurable 2-byte or 3-byte routing paths, defaulting to 3 bytes.
