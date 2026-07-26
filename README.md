# Supply Drop BBS — Home Assistant App repository

This repository packages [Mesh America's Supply Drop BBS](https://github.com/Mesh-America/supply-drop-bbs) as a Home Assistant App (formerly add-on).

The App uses the official upstream release binaries. A scheduled GitHub Actions workflow checks the upstream GitHub Releases feed once per day at 00:00 UTC. When a new stable release appears, the workflow:

1. verifies that all expected Linux binaries and `SHA256SUMS` exist;
2. builds and publishes the Home Assistant images for Home Assistant's supported `amd64` and `aarch64` architectures;
3. updates the App version and changelog only after the images were published successfully.

This ordering prevents Home Assistant from advertising an update before the corresponding container image exists.

## First publication

Create an empty **public** GitHub repository. If its URL is not `https://github.com/Bjorkan/supply-drop-bbs-home-assistant`, update `repository.yaml` before the first commit.

```bash
git init
git add .
git commit -m "Initial Home Assistant App repository"
git branch -M main
git remote add origin git@github.com:Bjorkan/supply-drop-bbs-home-assistant.git
git push -u origin main
```

The workflows publish images to `ghcr.io/<repository-owner>/supply-drop-bbs-ha-app`. The build metadata automatically normalizes the App's `image:` owner when the repository is hosted by another GitHub account.

After the first **Build Home Assistant App** workflow succeeds:

1. Open the repository's package named `supply-drop-bbs-ha-app` on GitHub.
2. Open **Package settings → Change package visibility** and make it **Public**. GitHub Container Registry creates a new package as private by default, while Home Assistant must be able to pull the image without GitHub credentials.
3. Add the repository URL in Home Assistant under **Settings → Apps → App store → Repositories**.

The package visibility change is a one-time operation. Later version tags and the `latest` tag are published to the same package automatically.

## Update model

For a new upstream release, the App version is set to the same version. The separately tracked `upstream-version.txt` prevents the sync from undoing a later wrapper-only version such as `0.12.0-1`. The scheduled workflow can also be started manually from **Actions → Sync upstream release**.

## Important runtime notes

- The upstream web admin is exposed on TCP port `8080`; it is not placed behind Home Assistant Ingress because the current upstream frontend uses root-relative API and event-stream paths.
- USB/UART devices are mapped through Home Assistant's `uart`, `usb`, and `udev` permissions.
- The SQLite database, logs, backups, node identity, and credentials persist in the App's `/data` volume.
- The generated upstream TOML configuration is available through the App configuration mapping as `config.toml`.

## Licensing

The Home Assistant wrapper code and documentation are Apache-2.0 licensed. Supply Drop BBS, including the adapted App icon and logo artwork, is distributed under its own upstream license, which includes the Commons Clause restriction; the upstream `LICENSE` and `NOTICE` are included with the App packaging and container image.
