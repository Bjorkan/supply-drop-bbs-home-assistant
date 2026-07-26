FROM ubuntu:24.04 AS downloader

ARG BUILD_VERSION
ARG BUILD_ARCH

COPY upstream-version.txt /tmp/upstream-version.txt

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl coreutils mawk \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    case "${BUILD_ARCH}" in \
      amd64) target="x86_64-unknown-linux-gnu" ;; \
      aarch64) target="aarch64-unknown-linux-gnu" ;; \
      *) echo "Unsupported Home Assistant architecture: ${BUILD_ARCH}" >&2; exit 1 ;; \
    esac; \
    upstream_version="$(tr -d '[:space:]' < /tmp/upstream-version.txt)"; \
    test -n "${upstream_version}"; \
    tag="v${upstream_version#v}"; \
    asset="supply-drop-bbs-${tag}-${target}"; \
    base="https://github.com/Mesh-America/supply-drop-bbs/releases/download/${tag}"; \
    curl --fail --location --retry 5 --retry-all-errors --output "/tmp/${asset}" "${base}/${asset}"; \
    curl --fail --location --retry 5 --retry-all-errors --output /tmp/SHA256SUMS "${base}/SHA256SUMS"; \
    awk -v file="${asset}" '$2 == file { print }' /tmp/SHA256SUMS > /tmp/SHA256SUMS.selected; test -s /tmp/SHA256SUMS.selected; \
    cd /tmp; \
    sha256sum --check SHA256SUMS.selected; \
    install -D -m 0755 "/tmp/${asset}" /out/supply-drop-bbs

FROM ubuntu:24.04

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="Supply Drop BBS Home Assistant App" \
    org.opencontainers.image.description="Home Assistant packaging for Mesh America's Supply Drop BBS" \
    org.opencontainers.image.url="https://github.com/Mesh-America/supply-drop-bbs" \
    org.opencontainers.image.licenses="LicenseRef-Supply-Drop-BBS"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates libudev1 python3 tini tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /config /data /usr/local/lib/supply-drop-bbs

COPY --from=downloader /out/supply-drop-bbs /usr/local/bin/supply-drop-bbs
COPY run.sh /run.sh
COPY generate_config.py /usr/local/lib/supply-drop-bbs/generate_config.py
COPY default-options.json /usr/local/share/supply-drop-bbs/default-options.json
COPY UPSTREAM_LICENSE UPSTREAM_NOTICE /usr/share/licenses/supply-drop-bbs/

RUN chmod 0755 /run.sh /usr/local/bin/supply-drop-bbs /usr/local/lib/supply-drop-bbs/generate_config.py

EXPOSE 8080
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
