set -euo pipefail
DATA="${DATA:-data}"
mkdir -p "$DATA"

# YouTube needs a JS runtime; yt-dlp uses deno by default, node must be opted into
ytdlp() {
  local js=()
  if ! command -v deno >/dev/null && command -v node >/dev/null; then js=(--js-runtimes node); fi
  uvx --from 'yt-dlp[default]@latest' yt-dlp "${js[@]}" "$@"
}
