#!/usr/bin/env bash
set -Eeuo pipefail

OPTIONS=/data/options.json
CONFIG=/config/config.toml
DEFAULTS=/usr/local/share/supply-drop-bbs/default-options.json

mkdir -p /data /config

if [[ ! -s "${OPTIONS}" ]]; then
  echo "[warning] /data/options.json is missing; using packaged defaults" >&2
  cp "${DEFAULTS}" "${OPTIONS}"
fi

python3 /usr/local/lib/supply-drop-bbs/generate_config.py \
  --options "${OPTIONS}" \
  --defaults "${DEFAULTS}" \
  --config "${CONFIG}"

/usr/local/bin/supply-drop-bbs --config "${CONFIG}" config check

VERSION=$(/usr/local/bin/supply-drop-bbs --version 2>/dev/null || true)
echo "[info] Starting ${VERSION:-Supply Drop BBS}"
echo "[info] Persistent data: /data"
echo "[info] Effective configuration: ${CONFIG}"

action="run"
exec /usr/local/bin/supply-drop-bbs --config "${CONFIG}" "${action}"
