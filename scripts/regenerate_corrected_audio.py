#!/usr/bin/env python3
"""Regenerate Google TTS audio for entries changed by the correction audit."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from gtts import gTTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=Path("data/word_corrections_2026-09-15.json"),
    )
    parser.add_argument("--workers", type=int, default=6)
    return parser.parse_args()


def synthesize(text: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=destination.parent,
                suffix=".mp3",
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
            gTTS(text=text, lang="gu", slow=False).save(temporary_name)
            os.replace(temporary_name, destination)
            return
        except Exception:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(2**attempt)


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    jobs = []
    for word_id, correction in manifest["corrections"].items():
        jobs.append((correction["word"], Path("audio/words") / f"{word_id}.mp3"))
        if "example" in correction:
            jobs.append(
                (correction["example"], Path("audio/examples") / f"{word_id}.mp3")
            )

    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(synthesize, text, destination): destination
            for text, destination in jobs
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            destination = futures[future]
            try:
                future.result()
            except Exception as error:
                failures.append((destination, error))
            if completed % 50 == 0 or completed == len(jobs):
                print(f"Generated {completed}/{len(jobs)} audio files")

    if failures:
        for destination, error in failures:
            print(f"Failed: {destination}: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
