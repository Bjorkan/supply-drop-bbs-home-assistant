#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import urllib.request

API = "https://api.github.com/repos/Mesh-America/supply-drop-bbs/releases/latest"
EXPECTED_TARGETS = (
    "x86_64-unknown-linux-gnu",
    "aarch64-unknown-linux-gnu",
)


def fetch_release() -> dict:
    request = urllib.request.Request(
        API,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "supply-drop-bbs-home-assistant-sync",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
    if release.get("draft") or release.get("prerelease"):
        raise SystemExit("Latest release is not a stable published release")
    return release


def version_from_tag(tag: str) -> str:
    match = re.fullmatch(r"v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)", tag)
    if not match:
        raise SystemExit(f"Unsupported upstream release tag: {tag!r}")
    return match.group(1)


def validate_assets(release: dict, tag: str) -> None:
    assets = {
        str(asset.get("name")): asset
        for asset in release.get("assets", [])
        if asset.get("name")
    }
    expected = {"SHA256SUMS"}
    expected.update(f"supply-drop-bbs-{tag}-{target}" for target in EXPECTED_TARGETS)
    missing = sorted(expected - assets.keys())
    if missing:
        raise SystemExit("Upstream release is missing required assets: " + ", ".join(missing))

    incomplete = sorted(
        name
        for name in expected
        if assets[name].get("state") != "uploaded" or int(assets[name].get("size") or 0) <= 0
    )
    if incomplete:
        raise SystemExit("Upstream release assets are not ready: " + ", ".join(incomplete))


def read_current_version(config: pathlib.Path) -> str:
    text = config.read_text(encoding="utf-8")
    match = re.search(r'(?m)^version:\s*["\']?([^"\'\s]+)', text)
    if not match:
        raise SystemExit("Unable to read current App version")
    return match.group(1)


def read_tracked_upstream_version(path: pathlib.Path) -> str:
    version = path.read_text(encoding="utf-8").strip()
    if version_from_tag(version) != version:
        raise SystemExit(f"Invalid tracked upstream version in {path}: {version!r}")
    return version


def read_current_image(config: pathlib.Path) -> str:
    text = config.read_text(encoding="utf-8")
    match = re.search(r"(?m)^image:\s*(\S+)", text)
    if not match:
        raise SystemExit("Unable to read current App image")
    return match.group(1)


def write_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


def replace_line(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    if not pattern.search(text):
        raise SystemExit(f"Missing {key}: in config")
    return pattern.sub(f"{key}: {value}", text, count=1)


def check(args: argparse.Namespace) -> int:
    release = fetch_release()
    tag = str(release["tag_name"])
    version = version_from_tag(tag)
    validate_assets(release, tag)
    current_app = read_current_version(args.config)
    tracked_upstream = read_tracked_upstream_version(args.upstream_version)
    expected_image = f"ghcr.io/{args.owner.lower()}/supply-drop-bbs-ha-app"
    current_image = read_current_image(args.config)
    update_available = tracked_upstream != version
    build_version = version if update_available else current_app

    write_output("tag", tag)
    write_output("version", version)
    write_output("build_version", build_version)
    write_output("update", str(update_available).lower())
    write_output("image_changed", str(current_image != expected_image).lower())
    print(f"Current App version: {current_app}")
    print(f"Packaged upstream version: {tracked_upstream}")
    print(f"Latest upstream version: {version}")
    return 0


def update(args: argparse.Namespace) -> int:
    release = fetch_release()
    tag = str(release["tag_name"])
    version = version_from_tag(tag)
    validate_assets(release, tag)
    if args.expected_tag and args.expected_tag != tag:
        raise SystemExit(f"Upstream latest tag changed from {args.expected_tag} to {tag}; retry workflow")

    tracked_upstream = read_tracked_upstream_version(args.upstream_version)
    upstream_changed = tracked_upstream != version

    text = args.config.read_text(encoding="utf-8")
    if upstream_changed:
        text = replace_line(text, "version", f'"{version}"')
        args.upstream_version.write_text(version + "\n", encoding="utf-8")
    text = replace_line(text, "image", f"ghcr.io/{args.owner.lower()}/supply-drop-bbs-ha-app")
    args.config.write_text(text, encoding="utf-8")

    body = str(release.get("body") or "No upstream release notes were supplied.").strip()
    section = (
        f"## {version}\n\n"
        "This Home Assistant App release packages the official "
        f"[Supply Drop BBS {tag}](https://github.com/Mesh-America/supply-drop-bbs/releases/tag/{tag}).\n\n"
        f"{body}\n"
    )
    existing = args.changelog.read_text(encoding="utf-8") if args.changelog.exists() else ""
    version_heading = re.compile(rf"(?m)^##\s+{re.escape(version)}(?:\s|$)")
    if upstream_changed and not version_heading.search(existing):
        old_sections = re.sub(r"\A# Changelog\s*", "", existing).strip()
        changelog = "# Changelog\n\n" + section
        if old_sections:
            changelog += "\n" + old_sections + "\n"
        args.changelog.write_text(changelog, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    check_parser = sub.add_parser("check")
    check_parser.add_argument("--config", required=True, type=pathlib.Path)
    check_parser.add_argument("--upstream-version", required=True, type=pathlib.Path)
    check_parser.add_argument("--owner", required=True)
    check_parser.set_defaults(func=check)

    update_parser = sub.add_parser("update")
    update_parser.add_argument("--config", required=True, type=pathlib.Path)
    update_parser.add_argument("--upstream-version", required=True, type=pathlib.Path)
    update_parser.add_argument("--changelog", required=True, type=pathlib.Path)
    update_parser.add_argument("--owner", required=True)
    update_parser.add_argument("--expected-tag", default="")
    update_parser.set_defaults(func=update)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
