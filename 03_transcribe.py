#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["faster-whisper>=1.1"]
# ///
"""Transcribe every file in $DATA/audio/ with Whisper (faster-whisper).

Writes $DATA/transcripts/<name>.txt (plain text) and <name>.srt (timestamped subtitles).
Files that already have a .txt are skipped, so it is safe to stop and re-run.

    ./03_transcribe.py                      # small model, language auto-detected
    ./03_transcribe.py --model large-v3 --language en
"""
import argparse
import os
import time
from pathlib import Path

AUDIO_EXTS = {".m4a", ".webm", ".mp3", ".opus", ".ogg", ".wav", ".mp4"}


def srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def pick_device() -> tuple[str, str]:
    import ctranslate2

    if ctranslate2.get_cuda_device_count() > 0:
        return "cuda", "float16"
    return "cpu", "int8"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="small",
                   help="tiny, base, small, medium, large-v3, turbo (default: small)")
    p.add_argument("--language", default=None, help="e.g. en, hi. Default: auto-detect per file")
    p.add_argument("--data", default=os.environ.get("DATA", "data"), help="data dir (default: $DATA or ./data)")
    args = p.parse_args()

    audio_dir = Path(args.data, "audio")
    out_dir = Path(args.data, "transcripts")
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(f for f in audio_dir.glob("*") if f.suffix in AUDIO_EXTS)
    todo = [f for f in files if not (out_dir / f"{f.stem}.txt").exists()]
    print(f"{len(files)} audio files, {len(files) - len(todo)} already done, {len(todo)} to go")
    if not todo:
        return

    from faster_whisper import WhisperModel

    device, compute = pick_device()
    print(f"Loading {args.model} on {device} ({compute})")
    model = WhisperModel(args.model, device=device, compute_type=compute, cpu_threads=os.cpu_count() or 4)

    for i, f in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {f.name}", flush=True)
        start = time.time()
        # vad_filter skips silence/music, which is where Whisper tends to hallucinate
        segments, info = model.transcribe(str(f), language=args.language, vad_filter=True)
        lines, srt = [], []
        for n, seg in enumerate(segments, 1):
            text = seg.text.strip()
            lines.append(text)
            srt.append(f"{n}\n{srt_time(seg.start)} --> {srt_time(seg.end)}\n{text}\n")
        (out_dir / f"{f.stem}.srt").write_text("\n".join(srt), encoding="utf-8")
        # .txt is written last and atomically: its presence marks the file as done
        tmp = out_dir / f"{f.stem}.txt.part"
        tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        tmp.replace(out_dir / f"{f.stem}.txt")
        mins = (time.time() - start) / 60
        print(f"    {info.duration / 60:.0f} min of {info.language} audio in {mins:.1f} min", flush=True)


if __name__ == "__main__":
    assert srt_time(3723.4567) == "01:02:03,457"
    main()
