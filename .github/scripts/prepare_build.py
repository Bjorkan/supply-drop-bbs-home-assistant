#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re


def replace_line(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    replacement = f'{key}: {value}'
    if not pattern.search(text):
        raise SystemExit(f"Missing {key}: in config")
    return pattern.sub(replacement, text, count=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=pathlib.Path)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--version", default="")
    parser.add_argument("--upstream-version-file", required=True, type=pathlib.Path)
    parser.add_argument("--upstream-version", default="")
    args = parser.parse_args()

    text = args.config.read_text(encoding="utf-8")
    owner = args.owner.lower()
    text = replace_line(text, "image", f"ghcr.io/{owner}/supply-drop-bbs-ha-app")
    if args.version:
        text = replace_line(text, "version", f'"{args.version}"')
    args.config.write_text(text, encoding="utf-8")
    if args.upstream_version:
        args.upstream_version_file.write_text(args.upstream_version + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
