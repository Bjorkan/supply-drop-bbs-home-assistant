# Changelog

## 1.2.0

This Home Assistant App release packages the official [Supply Drop BBS v1.2.0](https://github.com/Mesh-America/supply-drop-bbs/releases/tag/v1.2.0).

## [1.2.0] — 2026-09-11

### Bug Fixes

- Sanitize remaining bbs.name / remote-node display surfaces (#301) ([`8e7d16a`](8e7d16a088d1875980b32f1c7968289ae57a63b1))
- Panic-safe table indexing, O_NOFOLLOW on .tmp, atomic side effects (#300) ([`344fe5d`](344fe5d46a7df20138e001715680e685323173d0))
- Warn, not info, when a radio bridge connects with no SelfInfo (#299) ([`9789126`](9789126e8ddfb87f4dec6e9bea5689c49bf5e574))
- Harden the self-heal git update block (#297) ([`f84086d`](f84086d8eb882ee51972e54203dbfb55d535a1e1))
- Make location + share_in_advert writes atomic together ([`cc7782c`](cc7782c8350aee03d248c0315e26480a20398034))
- Strip Unicode display-spoofing codepoints from node names ([`c7aba70`](c7aba70b1b3800f3357eaf9fc89e0b1706f084cf))

### Chores

- Sync issue tracker export (close 2nt, x1b duplicates) (#302) ([`7b8c335`](7b8c335dcd87c3e5edf84f66773a3c4011fb17ca))
- Harden and document the release/CI workflow supply-chain posture (#298) ([`4a91a3f`](4a91a3ffb219ac43e2dfb7411c7a4d731dfae5ab))

### Features

- Add time-limited account suspension ("timeout") (#303) ([`996ecb8`](996ecb8da97a7371d545659eecedc976b9266e2a))
- Add user ban/unban commands ([`ad19987`](ad19987998e27d93813f2f79972f3ea39976cc4e))

## 1.1.3

This Home Assistant App release packages the official [Supply Drop BBS v1.1.3](https://github.com/Mesh-America/supply-drop-bbs/releases/tag/v1.1.3).

## [1.1.3] — 2026-09-09

### Bug Fixes

- Force the SRC_DIR self-healing fetch (#248) ([`8520512`](8520512b8cf15e6e27f0d65641a004a9370e317e))

### Chores

- Update issue tracker export ([`c28a33a`](c28a33ad4997b379202fda86e636736467c56c27))
- Update interaction log ([`8bdaae0`](8bdaae0d8bfc598aef2da4df9d9d5e7b18fbeca7))

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
