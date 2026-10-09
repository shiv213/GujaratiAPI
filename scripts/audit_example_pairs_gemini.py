#!/usr/bin/env python3
"""Audit Gujarati example triples with Vertex AI Gemini.

This script is intentionally restartable: every completed batch is written to
the output directory and skipped on the next run.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import time
from pathlib import Path

from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials


VALID_ISSUES = {"gujarati", "romanization", "translation"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gemini-2.5-flash-lite")
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def make_client() -> genai.Client:
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()
    return genai.Client(
        vertexai=True,
        project="framecut",
        location="global",
        credentials=Credentials(token=token),
    )


def prompt_for(records: list[dict[str, str]]) -> str:
    return """You are a meticulous native Gujarati lexicographer. Audit EVERY
dictionary example record below. Return a correction only when at least one
field is wrong.

Check all of these independently:
1. The Gujarati must be natural, grammatical, correctly spelled, factually
   sensible, and demonstrate the headword in the stated definition.
2. The Latin romanization must faithfully represent every part of the Gujarati
   sentence, including numbers. It must contain no Gujarati characters.
3. The English must be a natural, complete translation of the Gujarati. Pay
   special attention to numbers: Gujarati digits must keep their exact value.

Do not rewrite acceptable records for style. Never replace, remove, or avoid the
headword by substituting a synonym: the corrected Gujarati must still use the
given headword or its natural inflected form. If a factual example is false or
likely to become stale, replace it with a short timeless sentence that still
demonstrates the headword. For each bad record return the full corrected triple
and issue_codes chosen from gujarati, romanization, translation. Preserve the
record id exactly. Return JSON only in this shape:
{"corrections":[{"id":"1","gujarati":"...","romanization":"...",
"translation":"...","issue_codes":["translation"],"reason":"..."}]}

Records:
""" + json.dumps(records, ensure_ascii=False, separators=(",", ":"))


def validate(result: dict, originals: dict[str, dict[str, str]]) -> dict:
    corrections = result.get("corrections")
    if not isinstance(corrections, list):
        raise ValueError("missing corrections list")
    seen: set[str] = set()
    for item in corrections:
        required = {
            "id",
            "gujarati",
            "romanization",
            "translation",
            "issue_codes",
            "reason",
        }
        item["id"] = str(item["id"])
        if item["id"] not in originals or item["id"] in seen:
            raise ValueError(f"invalid or duplicate id: {item['id']}")
        seen.add(item["id"])
        for field in ("gujarati", "romanization", "translation"):
            item.setdefault(field, originals[item["id"]][field])
        item.setdefault("issue_codes", ["translation"])
        item.setdefault("reason", "Flagged for independent review.")
        if not set(item["issue_codes"]) <= VALID_ISSUES:
            raise ValueError(f"invalid issue codes: {item['issue_codes']}")
        if any(not str(item[field]).strip() for field in required - {"id", "issue_codes"}):
            raise ValueError(f"blank correction field: {item['id']}")
    return {"corrections": corrections}


def main() -> None:
    args = parse_args()
    words = json.loads(args.data.read_text(encoding="utf-8"))
    records = [
        {
            "id": word_id,
            "word": entry[0],
            "definition": entry[4],
            "gujarati": entry[5],
            "romanization": entry[6],
            "translation": entry[7],
        }
        for word_id, entry in words.items()
    ]
    batches = [
        records[index : index + args.batch_size]
        for index in range(0, len(records), args.batch_size)
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    client = make_client()

    def run_batch(batch_number: int) -> tuple[int, int, bool]:
        path = args.output / f"batch-{batch_number:04d}.json"
        if path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            return batch_number, len(cached["corrections"]), True
        batch = batches[batch_number]
        originals = {record["id"]: record for record in batch}
        last_error: Exception | None = None
        for attempt in range(6):
            try:
                response = client.models.generate_content(
                    model=args.model,
                    contents=prompt_for(batch),
                    config=types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json",
                        max_output_tokens=16_384,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                parsed = validate(json.loads(response.text), originals)
                path.write_text(
                    json.dumps(parsed, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                return batch_number, len(parsed["corrections"]), False
            except Exception as error:  # retry transient model/API failures
                last_error = error
                time.sleep(min(2**attempt, 30))
        raise RuntimeError(f"batch {batch_number} failed") from last_error

    total_corrections = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_batch, number) for number in range(len(batches))]
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            batch_number, count, cached = future.result()
            total_corrections += count
            print(
                f"{completed}/{len(batches)} batch={batch_number:04d} "
                f"corrections={count} cached={cached}",
                flush=True,
            )
    print(f"candidate corrections: {total_corrections}")


if __name__ == "__main__":
    main()
