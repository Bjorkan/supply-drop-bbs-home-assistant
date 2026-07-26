<p align="center">
  <img src="supply-drop-bbs/logo.png" width="180" alt="Supply Drop BBS logo" />
</p>

<h1 align="center">Supply Drop BBS for Home Assistant</h1>

<p align="center">
  Run Mesh America's Supply Drop BBS as a managed Home Assistant App.<br />
  Connect MeshCore, Meshtastic, or both to one shared bulletin-board system.
</p>

<p align="center">
  <a href="https://github.com/Bjorkan/supply-drop-bbs-home-assistant/actions/workflows/build.yaml">
    <img src="https://github.com/Bjorkan/supply-drop-bbs-home-assistant/actions/workflows/build.yaml/badge.svg" alt="Build status" />
  </a>
  &nbsp;
  <a href="https://github.com/Bjorkan/supply-drop-bbs-home-assistant/actions/workflows/sync-upstream.yaml">
    <img src="https://github.com/Bjorkan/supply-drop-bbs-home-assistant/actions/workflows/sync-upstream.yaml/badge.svg" alt="Upstream synchronization status" />
  </a>
  &nbsp;
  <a href="https://github.com/Mesh-America/supply-drop-bbs/releases/latest">
    <img src="https://img.shields.io/github/v/release/Mesh-America/supply-drop-bbs?label=upstream&color=3a8ad8" alt="Latest upstream release" />
  </a>
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/supervisor_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FBjorkan%2Fsupply-drop-bbs-home-assistant">
    <img src="https://my.home-assistant.io/badges/supervisor_addon_repository.svg" alt="Open your Home Assistant instance and add this App repository" />
  </a>
</p>

---

## What it is

[Supply Drop BBS](https://github.com/Mesh-America/supply-drop-bbs) is a bulletin-board system for LoRa mesh networks. Mesh users interact with it from their radios, while the operator uses the optional web interface to administer the service.

This repository packages the official upstream application as a Home Assistant App (formerly add-on). Home Assistant manages the container lifecycle, configuration, persistent storage, hardware access, backups, updates, and watchdog monitoring.

Supply Drop BBS can serve **MeshCore and Meshtastic at the same time**. Both transports use the same accounts, rooms, private mail, and message database, so the BBS remains one shared system regardless of which radio network a user connects through.

```text
MeshCore radio ───────┐
                      ├── Supply Drop BBS ── shared users, rooms and messages
Meshtastic radio ─────┘              │
                                     └── web administration on port 8080
```

## Features

- Official, checksum-verified Supply Drop BBS release binaries
- MeshCore support through serial, TCP, or HAT configurations
- Meshtastic support through serial, TCP, or HAT configurations
- Simultaneous MeshCore and Meshtastic operation
- Shared user, room, mail, and message storage across transports
- Home Assistant-managed options or direct `config.toml` management
- Persistent SQLite database, logs, backups, identity, and credentials
- Web administration with Home Assistant watchdog support
- Cold Home Assistant backups for a consistent SQLite snapshot
- Multi-architecture images for `amd64` and `aarch64`
- Automatic synchronization with stable upstream GitHub releases

## Requirements

- Home Assistant OS or another installation with Home Assistant Supervisor and Apps support
- An `amd64` or `aarch64` Home Assistant host
- At least one supported MeshCore or Meshtastic connection
- USB/UART hardware exposed to Home Assistant when using a directly connected radio

## Installation

### Add the repository

Use the button above, or add the repository manually:

1. Open **Settings → Apps → App store** in Home Assistant.
2. Open the repository menu.
3. Add:

   ```text
   https://github.com/Bjorkan/supply-drop-bbs-home-assistant
   ```

4. Refresh the App store if the App does not appear immediately.

### Install and start the App

1. Select **Supply Drop BBS** from the App store.
2. Install the App.
3. Open the **Configuration** tab.
4. Enable and configure at least one transport.
5. Save the configuration.
6. Start the App and inspect the log for connection errors.
7. Open **Web UI** to reach the administration interface.

The first mesh user who registers with a new database becomes the Sysop. Registration and normal BBS use happen over MeshCore or Meshtastic, not through the web administration interface.

## Transport setup

Both transports can be enabled together or used independently.

| Transport | Connection | Typical use |
|---|---|---|
| MeshCore | `serial` | A MeshCore radio connected directly by USB/UART |
| MeshCore | `tcp` | A CompanionFrameServer reachable over the network |
| MeshCore | `hat` | A HAT setup exposed through its companion service |
| Meshtastic | `serial` | A Meshtastic radio connected directly by USB/UART |
| Meshtastic | `tcp` | A reachable `meshtasticd` instance |
| Meshtastic | `hat` | A Meshtastic-compatible UART/HAT connection |

For USB radios, prefer a stable device path such as:

```text
/dev/serial/by-id/usb-...
```

A stable path avoids the device unexpectedly changing between `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`, and similar names after a reboot or reconnect.

> [!IMPORTANT]
> `127.0.0.1` inside the App refers to the Supply Drop BBS container itself, not the Home Assistant host. Use a reachable hostname or IP address for services running elsewhere.

Radio region, frequency, channels, and other firmware-specific settings must be configured on the radio itself before connecting it to Supply Drop BBS.

## Configuration ownership

The `config_mode` option controls who owns `/config/config.toml`.

### `home_assistant`

This is the default and recommended mode for most installations.

- Home Assistant App options are applied whenever the App starts.
- Existing advanced TOML sections that are not represented by App options are retained.
- Values managed by Home Assistant options overwrite matching manual changes on restart.

### `file`

Use this mode when the upstream web settings page or manual TOML editing should be authoritative.

- A default file is created when `config.toml` does not exist.
- An existing file is left untouched on subsequent starts.
- You are responsible for keeping the file valid.

The effective file is available through the App configuration mapping as:

```text
config.toml
```

The App validates the configuration before starting Supply Drop BBS. An invalid file causes startup to stop with an error instead of launching with a partially understood configuration.

For the full option reference and operational notes, see [the App documentation](supply-drop-bbs/DOCS.md).

## Persistent data and backups

Runtime state is stored in the Home Assistant-managed `/data` volume, including:

- `bbs.sqlite` and its SQLite journal files
- application logs
- automatic Supply Drop BBS backups
- node identity and credentials
- other runtime state created by Supply Drop BBS

The App declares Home Assistant backups as **cold backups**, so Home Assistant stops the App while capturing its data. This avoids taking an inconsistent snapshot while SQLite is writing.

The generated or manually managed `config.toml` is stored in the mapped App configuration directory and is included with the App configuration data.

## Web administration and security

The administration interface listens on TCP port `8080` and is opened through the App's **Web UI** button.

It is exposed as a normal port instead of Home Assistant Ingress because the upstream frontend currently uses root-relative API, download, and event-stream paths.

For local HTTP use, leave `web_cookie_secure` disabled. When publishing the interface behind an HTTPS reverse proxy:

1. Set `web_external_origin` to the exact public origin, for example `https://bbs.example.com`.
2. Enable `web_cookie_secure`.
3. Restrict access with suitable authentication and network controls.

Do not expose the administration port directly to the internet without TLS and appropriate access restrictions.

The watchdog checks the upstream `/health` endpoint. If you deliberately disable the web plugin, disable the Home Assistant watchdog for the App as well.

## Automatic upstream updates

The repository checks the latest stable release from `Mesh-America/supply-drop-bbs` once per day at **00:00 UTC**.

When a new release is found, GitHub Actions performs the update in this order:

1. Confirm that the release is published, stable, and not a prerelease.
2. Confirm that the required `amd64`, `aarch64`, and `SHA256SUMS` assets exist.
3. Download and verify the official binaries against the upstream checksums.
4. Build and publish architecture-specific Home Assistant images.
5. Publish the multi-architecture GHCR manifest.
6. Update the App version, tracked upstream version, and changelog.
7. Commit the metadata update to `main`.

The App metadata is updated only after all images have been published successfully. Home Assistant therefore does not advertise an update whose container image is missing.

The synchronization can also be started manually from **Actions → Sync upstream release**.

See [the App changelog](supply-drop-bbs/CHANGELOG.md) for packaged releases.

## Repository layout

```text
.
├── repository.yaml                 Home Assistant App repository metadata
├── supply-drop-bbs/
│   ├── config.yaml                 App metadata, options and schema
│   ├── DOCS.md                     Documentation shown in Home Assistant
│   ├── Dockerfile                  Multi-architecture App image
│   ├── generate_config.py          Home Assistant options → upstream TOML
│   ├── run.sh                      Startup and validation entrypoint
│   └── upstream-version.txt        Packaged upstream release
└── .github/
    ├── scripts/                     Build and release synchronization helpers
    └── workflows/                   Image build and upstream update workflows
```

## Support and issue reporting

Choose the repository that owns the affected behavior:

- **Home Assistant packaging, installation, App options, image builds, or update automation:** report it in this repository.
- **Supply Drop BBS behavior, mesh commands, rooms, mail, database logic, or upstream web UI:** report it to [Mesh-America/supply-drop-bbs](https://github.com/Mesh-America/supply-drop-bbs/issues).
- **Security vulnerabilities in Supply Drop BBS:** follow the [upstream security policy](https://github.com/Mesh-America/supply-drop-bbs/security/policy).

Include the App version, Home Assistant architecture, relevant App configuration, and complete startup logs when reporting a packaging problem. Remove passwords, keys, and other private data first.

## Licensing

The Home Assistant wrapper code and wrapper documentation in this repository are licensed under the [Apache License 2.0](LICENSE).

The packaged Supply Drop BBS application and adapted upstream artwork are governed by the included [upstream license](supply-drop-bbs/UPSTREAM_LICENSE) and [notice](supply-drop-bbs/UPSTREAM_NOTICE). The upstream license includes the Commons Clause restriction and is not OSI-approved open source. Review those terms before redistribution or commercial use.

This repository is an independent Home Assistant packaging project. Supply Drop BBS itself is developed by [Mesh America](https://github.com/Mesh-America).
