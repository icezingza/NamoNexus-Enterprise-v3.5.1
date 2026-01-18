"""Batch metadata extraction, transcription, and organization for MP3 files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from mutagen.mp3 import MP3

try:
    import imageio_ffmpeg  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    imageio_ffmpeg = None

try:
    import whisper  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    whisper = None


CASE_SUFFIX_RE = re.compile(r"\s*\(\d+\)$")

TONE_HINTS = {
    "a": {
        "tone_hint": "neutral / hidden emotion",
        "test_hint": "baseline / non-expressive",
    },
    "b": {
        "tone_hint": "panic / muffled",
        "test_hint": "low mood / panic",
    },
    "c": {
        "tone_hint": "waiting / fatigued",
        "test_hint": "fatigued / waiting",
    },
    "d": {
        "tone_hint": "extreme joy / numb",
        "test_hint": "high mood / numb",
    },
    "e": {
        "tone_hint": "numb / dark mirror",
        "test_hint": "low mood / numb",
    },
    "f": {
        "tone_hint": "farewell / end-of-life",
        "test_hint": "closing / farewell",
    },
}


def normalize_case_id(name: str) -> str:
    cleaned = CASE_SUFFIX_RE.sub("", name)
    while cleaned.lower().endswith(".mp3"):
        cleaned = cleaned[:-4]
    return cleaned


def ensure_ffmpeg_in_path() -> Optional[str]:
    if imageio_ffmpeg is None:
        return None
    ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    ffmpeg_dir = str(ffmpeg_exe.parent)
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    return str(ffmpeg_exe)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_case_letter(case_id: str) -> Optional[str]:
    match = re.search(r"case_([a-f])_", case_id.lower())
    if match:
        return match.group(1)
    return None


def collect_mp3_files(input_dir: Path) -> List[Path]:
    return sorted(
        [
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".mp3"
        ],
        key=lambda path: path.name.lower(),
    )


def build_groups(files: List[Path]) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {}
    for path in files:
        case_id = normalize_case_id(path.stem)
        groups.setdefault(case_id, []).append(path)
    for paths in groups.values():
        paths.sort(key=lambda path: path.name.lower())
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract metadata, transcribe, and organize MP3 files.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory containing MP3 files.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory (default: <input>/organized).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("WHISPER_MODEL", "base"),
        help="Whisper model size (tiny, base, small, medium, large).",
    )
    parser.add_argument(
        "--no-transcribe",
        action="store_true",
        help="Skip transcription.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    if not input_dir.exists():
        raise SystemExit(f"Input directory not found: {input_dir}")

    output_dir = Path(args.output).resolve() if args.output else input_dir / "organized"
    audio_dir = output_dir / "audio"
    transcripts_dir = output_dir / "transcripts"

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    files = collect_mp3_files(input_dir)
    if not files:
        raise SystemExit(f"No MP3 files found in {input_dir}")

    groups = build_groups(files)

    ffmpeg_path = None
    model = None
    if not args.no_transcribe:
        if whisper is None:
            raise SystemExit("Whisper is not installed. Use --no-transcribe or install.")
        ffmpeg_path = ensure_ffmpeg_in_path()
        model = whisper.load_model(args.model, device="cpu")

    records: List[Dict[str, object]] = []
    for case_id, paths in groups.items():
        case_dir = audio_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        for idx, path in enumerate(paths, start=1):
            dest_name = f"{case_id}_v{idx:02d}.mp3"
            dest_path = case_dir / dest_name
            shutil.copy2(path, dest_path)

            info = MP3(path)
            duration_seconds = round(info.info.length, 3) if info.info.length else None
            bitrate_kbps = round(info.info.bitrate / 1000) if info.info.bitrate else None
            sample_rate_hz = info.info.sample_rate or None
            channels = info.info.channels or None
            file_size_bytes = path.stat().st_size
            checksum = sha256_file(path)

            transcription_text = None
            transcription_language = None
            transcription_error = None
            transcript_path = transcripts_dir / f"{case_id}_v{idx:02d}.txt"
            if model is not None:
                try:
                    result = model.transcribe(str(path), fp16=False)
                    transcription_text = (result.get("text") or "").strip()
                    transcription_language = result.get("language")
                except Exception as exc:  # noqa: BLE001
                    transcription_error = str(exc)

            if transcription_text:
                transcript_path.write_text(transcription_text, encoding="utf-8")
            elif transcription_error:
                transcript_path.write_text(
                    f"[transcription_error] {transcription_error}",
                    encoding="utf-8",
                )
            elif model is None:
                transcript_path.write_text(
                    "[transcription_skipped]",
                    encoding="utf-8",
                )

            case_letter = extract_case_letter(case_id)
            tone_hint = None
            test_hint = None
            if case_letter and case_letter in TONE_HINTS:
                tone_hint = TONE_HINTS[case_letter]["tone_hint"]
                test_hint = TONE_HINTS[case_letter]["test_hint"]

            records.append(
                {
                    "original_path": str(path),
                    "organized_path": str(dest_path),
                    "case_id": case_id,
                    "variant_index": idx,
                    "sha256": checksum,
                    "file_size_bytes": file_size_bytes,
                    "duration_seconds": duration_seconds,
                    "bitrate_kbps": bitrate_kbps,
                    "sample_rate_hz": sample_rate_hz,
                    "channels": channels,
                    "tone_hint": tone_hint,
                    "test_hint": test_hint,
                    "transcription_language": transcription_language,
                    "transcription_text": transcription_text,
                    "transcription_error": transcription_error,
                }
            )

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    csv_path = output_dir / "metadata.csv"
    fieldnames = [
        "original_path",
        "organized_path",
        "case_id",
        "variant_index",
        "sha256",
        "file_size_bytes",
        "duration_seconds",
        "bitrate_kbps",
        "sample_rate_hz",
        "channels",
        "tone_hint",
        "test_hint",
        "transcription_language",
        "transcription_text",
        "transcription_error",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    summary_lines = [
        "# Audio Test Batch Summary",
        "",
        f"- Input directory: {input_dir}",
        f"- Output directory: {output_dir}",
        f"- Files processed: {len(files)}",
        f"- Case groups: {len(groups)}",
        f"- Transcription model: {args.model if model else 'skipped'}",
        f"- FFMPEG path: {ffmpeg_path or 'not used'}",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Tone/Test Hints (provided mapping):",
        "",
        "| Case | Tone hint | Test hint |",
        "| --- | --- | --- |",
    ]
    for case_letter, hints in sorted(TONE_HINTS.items()):
        summary_lines.append(
            f"| case_{case_letter} | {hints['tone_hint']} | {hints['test_hint']} |"
        )
    summary_lines.append("")
    summary_path = output_dir / "summary.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
