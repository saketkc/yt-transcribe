#!/usr/bin/env bash
# Usage: ./01_list_videos.sh <URL> [extra yt-dlp args]
# Writes $DATA/videos.txt; delete lines or prefix them with # to skip videos.
source "$(dirname "$0")/common.sh"
[ $# -ge 1 ] || { sed -n '2,3p' "$0"; exit 1; }
url="$1"; shift
ytdlp --flat-playlist --print "%(webpage_url)s  # %(title)s" "$@" "$url" > "$DATA/videos.txt"
echo "$(wc -l < "$DATA/videos.txt") videos -> $DATA/videos.txt"
