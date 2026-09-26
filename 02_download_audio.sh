#!/usr/bin/env bash
# Usage: ./02_download_audio.sh [extra yt-dlp args]
source "$(dirname "$0")/common.sh"
[ -s "$DATA/videos.txt" ] || { echo "No $DATA/videos.txt; run 01_list_videos.sh first"; exit 1; }
mkdir -p "$DATA/audio"
# sleeps avoid YouTube rate limits on long channels
ytdlp -f bestaudio \
  --batch-file "$DATA/videos.txt" \
  --download-archive "$DATA/audio/downloaded.txt" \
  --output "$DATA/audio/%(upload_date)s %(title).90B [%(id)s].%(ext)s" \
  --ignore-errors --no-overwrites --continue \
  --sleep-interval 2 --max-sleep-interval 6 \
  "$@"
echo "Audio in $DATA/audio/"
