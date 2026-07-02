#!/usr/bin/env bash
# Install Playwright Chromium system libs on hub WSL without sudo (apt download + extract).
set -euo pipefail
LIBROOT="${HOME}/playwright-libs"
mkdir -p "$LIBROOT"
cd "$LIBROOT"

PKGS=(
  libnspr4 libnss3 libgbm1 libxkbcommon0 libdrm2 libxcomposite1 libxdamage1
  libxfixes3 libxrandr2 libasound2t64 libatk1.0-0t64 libatk-bridge2.0-0t64
  libcups2t64 libpango-1.0-0 libcairo2 libx11-6 libxcb1 libxext6 libxi6
)

for pkg in "${PKGS[@]}"; do
  apt-get download "$pkg" 2>/dev/null || true
done

for deb in *.deb; do
  [[ -f "$deb" ]] || continue
  dpkg-deb -x "$deb" .
done

echo "export LD_LIBRARY_PATH=${LIBROOT}/usr/lib/x86_64-linux-gnu:\${LD_LIBRARY_PATH:-}"
