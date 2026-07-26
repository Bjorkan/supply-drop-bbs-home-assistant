# Supply Drop BBS Home Assistant App

## Before starting

Configure at least one transport:

- **MeshCore serial:** enable MeshCore, select `serial`, and use a mapped device such as `/dev/ttyACM0` or preferably a stable `/dev/serial/by-id/...` path.
- **MeshCore TCP/HAT:** enable MeshCore, select `tcp` or `hat`, and enter the CompanionFrameServer address. `127.0.0.1` refers to this App container, not the Home Assistant host.
- **Meshtastic serial/HAT:** enable Meshtastic and select the matching connection type and serial device.
- **Meshtastic TCP:** enter the `meshtasticd` address and port.

Both transports can be enabled simultaneously.

## Web administration

The upstream web administration listens on port `8080`. Open it using the App's **Open Web UI** button or `http://<home-assistant-host>:<configured-port>`.

Supply Drop BBS creates the first registered mesh user as Sysop. Registration happens over the configured mesh transport. Passwords are stored in the BBS database, not in Home Assistant App options.

The current upstream frontend is deliberately exposed as a normal port rather than Home Assistant Ingress because it uses root-relative API, download, and Server-Sent Events paths.

Keep `web_enabled` enabled when using the Home Assistant App watchdog. If you deliberately disable the web plugin, also disable the watchdog in the App system settings because the `/health` endpoint will no longer be available.

## Configuration ownership

`config_mode` controls how `/config/config.toml` is handled:

- `home_assistant` updates the fields represented by App options at every start. Advanced upstream sections that are not managed by these options are retained.
- `file` creates the file once if it is absent, then leaves an existing file untouched. Use this mode when the upstream Settings page or manual TOML editing should be authoritative.

In `home_assistant` mode, changes made through the upstream Settings page to fields also represented by Home Assistant options are replaced at the next App restart.

## Persistent files

The App keeps these under `/data`. Home Assistant backups stop the App first so the SQLite database is captured consistently:

- `bbs.sqlite` and SQLite journal files
- logs
- automatic backups
- node credentials and identity data stored by Supply Drop BBS

The App's `config.toml` is stored in the mapped App configuration directory and is included in upstream backup snapshots.

## Security and external access

By default, cookies are not marked Secure because the web UI is served over local HTTP. When publishing the UI through an HTTPS reverse proxy, set:

- `web_external_origin` to the exact public origin, for example `https://bbs.example.com`
- `web_cookie_secure` to `true`

Do not expose the admin port directly to the internet without TLS and appropriate network access controls.

## Updates

The repository checks the official Supply Drop BBS GitHub Releases feed once per day at 00:00 UTC. A Home Assistant update is published only after the corresponding `amd64` and `aarch64` images have been built successfully.

## License

The wrapper is Apache-2.0 licensed. The packaged Supply Drop BBS binary is governed by the included upstream `UPSTREAM_LICENSE` and `UPSTREAM_NOTICE`, including its Commons Clause restriction.
