#!/usr/bin/env sh
# Instala o hls_dl: baixa o script e coloca no PATH.
set -eu

REPO="Hoyasumii/hls-dl"
URL="https://raw.githubusercontent.com/$REPO/main/hls_dl.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 não encontrado. No Termux: pkg install python" >&2
  exit 1
fi

# Termux define $PREFIX (já está no PATH); no resto usa ~/.local/bin
if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/bin" ]; then
  BIN="$PREFIX/bin"
else
  BIN="$HOME/.local/bin"
  mkdir -p "$BIN"
fi

DEST="$BIN/hls_dl"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$DEST"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$DEST" "$URL"
else
  echo "Precisa de curl ou wget." >&2
  exit 1
fi
chmod +x "$DEST"

case ":$PATH:" in
  *":$BIN:"*) ;;
  *)
    RC="$HOME/.profile"
    [ -n "${BASH_VERSION:-}" ] || [ "${SHELL##*/}" = "bash" ] && RC="$HOME/.bashrc"
    [ "${SHELL##*/}" = "zsh" ] && RC="$HOME/.zshrc"
    echo "export PATH=\"$BIN:\$PATH\"" >> "$RC"
    echo "Adicionado $BIN ao PATH em $RC (abra um novo terminal ou: source $RC)"
    ;;
esac

echo "hls_dl instalado em $DEST. Uso: hls_dl \"LINK.m3u8\""
