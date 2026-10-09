#!/usr/bin/env python3
"""Regenerate example MP3s changed by an example-pair audit manifest."""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def synthesize(token: str, word_id: str, text: str) -> str:
    destination = Path("audio/examples") / f"{word_id}.mp3"
    body = json.dumps(
        {
            "input": {"text": text},
            "voice": {
                "languageCode": "gu-IN",
                "name": "gu-IN-Wavenet-A",
            },
            "audioConfig": {"audioEncoding": "MP3"},
        }
    ).encode()
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                "https://texttospeech.googleapis.com/v1/text:synthesize",
                data=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "x-goog-user-project": "framecut",
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                audio = base64.b64decode(json.load(response)["audioContent"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=destination.parent, delete=False
            ) as temporary:
                temporary.write(audio)
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, destination)
            return word_id
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    jobs = [
        (word_id, correction["corrected"]["gujarati"])
        for word_id, correction in manifest["corrections"].items()
        if "gujarati" in correction["changed_fields"]
    ]
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(synthesize, token, *job) for job in jobs]
        for completed, future in enumerate(
            concurrent.futures.as_completed(futures), 1
        ):
            future.result()
            if completed % 25 == 0 or completed == len(futures):
                print(f"Generated {completed}/{len(futures)} example MP3s")


if __name__ == "__main__":
    main()
