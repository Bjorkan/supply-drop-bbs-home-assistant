# Changelog

## 1.1.0

This Home Assistant App release packages the official [Supply Drop BBS v1.1.0](https://github.com/Mesh-America/supply-drop-bbs/releases/tag/v1.1.0).

## [1.1.0] — 2026-09-07

### Bug Fixes

- Retry fixed-position writes dropped on a full admin channel ([`f6d8aa5`](f6d8aa562b5084f100ede3809f61ca357d8d6b4c))
- Correct cargo-release config so `cargo release` actually works ([`7ae01dd`](7ae01dd23d204e9bcff437cbf59f44c4a4c45d95))

### Features

- Broadcast configured GPS position in MeshCore/Meshtastic adverts ([`087049e`](087049ed44cb9b9bfed4f70e81c8e5b29e9a52c5))

## 1.0.1

This Home Assistant App release packages the official [Supply Drop BBS v1.0.1](https://github.com/Mesh-America/supply-drop-bbs/releases/tag/v1.0.1).

## [1.0.1] — 2026-09-05

### Bug Fixes

- Harden MeshCore/Meshtastic radio settings against audit findings ([`b0f516c`](b0f516cdd4fa944f0dc82a68c3ce537633f856bb))
- Stop MeshCore radio preset from clobbering saved field overrides ([`0c9c4e7`](0c9c4e79d9043c306e4db233dfc3e60e5e94c638))

## [0.12.0] — 2026-07-18

## 0.12.0-3

- Work around Home Assistant Supervisor bug #7044 affecting bounded string options.
- Replace all `str(min,max)` schema entries with equivalent regex length validation.
- Keep the same accepted text lengths without invoking Supervisor `Range`.

## 0.12.0-2

- Avoid Supervisor `Range` validation entirely for numeric App options.
- Accept numeric YAML values and digit strings through `match(^[0-9]+$)`.
- Keep the actual numeric range checks in `generate_config.py`.

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
