#!/usr/bin/env python3
"""Create or merge Supply Drop BBS TOML from Home Assistant App options."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import pathlib
import re
import tempfile
import tomllib
from typing import Any

BARE_KEY = re.compile(r"^[A-Za-z0-9_-]+$")


def nonempty(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def set_optional(mapping: dict[str, Any], key: str, value: Any) -> None:
    parsed = nonempty(value)
    if parsed is None:
        mapping.pop(key, None)
    else:
        mapping[key] = parsed


def command_prefix(value: Any, option_name: str) -> str | None:
    parsed = nonempty(value)
    if parsed is None:
        return None
    if len(parsed) != 1:
        raise ValueError(f"{option_name} must be empty or exactly one character")
    return parsed


def load_existing(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a TOML table")
    return data


def ensure_table(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        value = {}
        parent[key] = value
    return value


def build_config(existing: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    cfg = existing

    bbs = ensure_table(cfg, "bbs")
    bbs.update(
        {
            "name": str(options["bbs_name"]),
            "data_dir": "/data",
            "welcome_msg": str(options["welcome_message"]),
            "timezone": str(options["timezone"]),
            "require_verify": bool(options["require_verify"]),
        }
    )
    set_optional(bbs, "guest_room", options.get("guest_room"))

    database = ensure_table(cfg, "database")
    database["path"] = "/data/bbs.sqlite"

    logging = ensure_table(cfg, "logging")
    logging["level"] = str(options["log_level"]).upper()
    logging.setdefault("format", "compact")
    logging["file"] = "/data/log/bbs.log"

    backup = ensure_table(cfg, "backup")
    backup.update(
        {
            "enabled": bool(options["backup_enabled"]),
            "interval_hours": int(options["backup_interval_hours"]),
            "directory": "/data/backups",
        }
    )

    plugins = ensure_table(cfg, "plugins")

    cli = ensure_table(plugins, "cli")
    cli.update({"enabled": False, "socket": "/data/cli.sock"})

    mesh = ensure_table(plugins, "mesh")
    mesh.update(
        {
            "enabled": bool(options["meshcore_enabled"]),
            "connection_type": str(options["meshcore_connection_type"]),
            "addr": str(options["meshcore_tcp_address"]),
            "serial_port": str(options["meshcore_serial_port"]),
            "baud_rate": int(options["meshcore_baud_rate"]),
            "path_bytes": int(options["meshcore_path_bytes"]),
            "flood_after_send": bool(options["meshcore_flood_after_send"]),
            "reply_max_attempts": int(options["meshcore_reply_max_attempts"]),
        }
    )
    prefix = command_prefix(options.get("meshcore_command_prefix"), "meshcore_command_prefix")
    if prefix is None:
        mesh.pop("command_prefix", None)
    else:
        mesh["command_prefix"] = prefix

    meshtastic = ensure_table(plugins, "meshtastic")
    meshtastic.update(
        {
            "enabled": bool(options["meshtastic_enabled"]),
            "connection_type": str(options["meshtastic_connection_type"]),
            "addr": str(options["meshtastic_tcp_address"]),
            "serial_port": str(options["meshtastic_serial_port"]),
            "baud_rate": int(options["meshtastic_baud_rate"]),
        }
    )
    prefix = command_prefix(options.get("meshtastic_command_prefix"), "meshtastic_command_prefix")
    if prefix is None:
        meshtastic.pop("command_prefix", None)
    else:
        meshtastic["command_prefix"] = prefix
    set_optional(meshtastic, "long_name", options.get("meshtastic_long_name"))
    set_optional(meshtastic, "short_name", options.get("meshtastic_short_name"))

    web = ensure_table(plugins, "web")
    web.update(
        {
            "enabled": bool(options["web_enabled"]),
            "bind": "0.0.0.0:8080",
            "cookie_secure": bool(options["web_cookie_secure"]),
            "prometheus": bool(options["prometheus_enabled"]),
            "config_path": "/config/config.toml",
        }
    )
    set_optional(web, "external_origin", options.get("web_external_origin"))

    return cfg


def format_key(key: str) -> str:
    return key if BARE_KEY.fullmatch(key) else json.dumps(key, ensure_ascii=False)


def format_path(parts: tuple[str, ...]) -> str:
    return ".".join(format_key(part) for part in parts)


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are not supported in config.toml")
        return repr(value)
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, list) and all(not isinstance(item, dict) for item in value):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    raise TypeError(f"unsupported TOML value: {value!r}")


def emit_table(lines: list[str], path: tuple[str, ...], table: dict[str, Any], array: bool = False) -> None:
    if path:
        marker = "[[" if array else "["
        close = "]]" if array else "]"
        lines.append(f"{marker}{format_path(path)}{close}")

    for key, value in table.items():
        if isinstance(value, dict):
            continue
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            continue
        if value is None:
            continue
        lines.append(f"{format_key(str(key))} = {format_value(value)}")

    for key, value in table.items():
        if isinstance(value, dict):
            if lines and lines[-1] != "":
                lines.append("")
            emit_table(lines, path + (str(key),), value)
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            for item in value:
                if lines and lines[-1] != "":
                    lines.append("")
                emit_table(lines, path + (str(key),), item, array=True)


def dumps_toml(data: dict[str, Any]) -> str:
    lines: list[str] = []
    emit_table(lines, (), data)
    return "\n".join(lines).rstrip() + "\n"


def atomic_dump(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(dumps_toml(data))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--options", required=True, type=pathlib.Path)
    parser.add_argument("--defaults", required=True, type=pathlib.Path)
    parser.add_argument("--config", required=True, type=pathlib.Path)
    args = parser.parse_args()

    defaults = json.loads(args.defaults.read_text(encoding="utf-8"))
    supplied = json.loads(args.options.read_text(encoding="utf-8"))
    if not isinstance(defaults, dict):
        raise ValueError("default-options.json must contain an object")
    if not isinstance(supplied, dict):
        raise ValueError("options.json must contain an object")
    options = defaults | supplied

    mode = str(options.get("config_mode", "home_assistant"))
    existing = load_existing(args.config)

    if mode == "file" and existing:
        print(f"[info] File-managed configuration retained: {args.config}")
        return 0
    if mode not in {"home_assistant", "file"}:
        raise ValueError("config_mode must be 'home_assistant' or 'file'")

    cfg = build_config(existing, options)
    atomic_dump(args.config, cfg)
    print(f"[info] Wrote Supply Drop BBS configuration: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
