#!/usr/bin/env bash
# Verify prerequisites and pre-download Python dependencies.
set -uo pipefail
ok=1
if command -v uv >/dev/null; then echo "ok   uv $(uv --version | cut -d' ' -f2)"
else echo "MISSING uv -> curl -LsSf https://astral.sh/uv/install.sh | sh"; ok=0; fi

if command -v deno >/dev/null; then echo "ok   deno (JS runtime for YouTube)"
elif command -v node >/dev/null; then echo "ok   node (JS runtime for YouTube; deno also works)"
else echo "MISSING deno -> curl -fsSL https://deno.land/install.sh | sh"; ok=0; fi

if command -v nvidia-smi >/dev/null && nvidia-smi -L >/dev/null 2>&1; then echo "ok   NVIDIA GPU found, transcription will use it"
else echo "note no usable NVIDIA GPU, transcription runs on CPU (slower; see README)"; fi

[ "$ok" = 1 ] || exit 1
cd "$(dirname "$0")"
echo "...fetching yt-dlp and faster-whisper (first run only)"
uvx --from 'yt-dlp[default]@latest' yt-dlp --version >/dev/null && echo "ok   yt-dlp"
uv run --script 03_transcribe.py --help >/dev/null && echo "ok   faster-whisper"
echo "All set. Next: ./01_list_videos.sh <channel|playlist|video URL>"
