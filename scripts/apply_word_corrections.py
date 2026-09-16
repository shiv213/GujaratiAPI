#!/usr/bin/env python3
"""Apply a reviewed Gujarati spelling and pronunciation correction manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_DATA_FILES = (
    Path("data/gujarati_words_google_enhanced.json"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=Path("data/word_corrections_2026-09-15.json"),
    )
    parser.add_argument("data_files", nargs="*", type=Path)
    return parser.parse_args()


def apply_manifest(manifest_path: Path, data_paths: list[Path]) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    corrections = manifest["corrections"]

    for data_path in data_paths:
        data = json.loads(data_path.read_text(encoding="utf-8"))

        for word_id, correction in corrections.items():
            entry = data[word_id]
            expected = correction["original"]
            corrected = correction["word"]
            if entry[0] not in {expected, corrected}:
                raise ValueError(
                    f"{data_path}: entry {word_id} is {entry[0]!r}, "
                    f"expected {expected!r} or {corrected!r}"
                )

            entry[0] = corrected
            entry[1] = correction["ipa"]
            entry[2] = correction["romanization"]

            if len(entry) > 5 and "example" in correction:
                entry[5] = correction["example"]
            if len(entry) > 6 and "example_romanization" in correction:
                entry[6] = correction["example_romanization"]

        data_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Updated {len(corrections)} entries in {data_path}")


def main() -> None:
    args = parse_args()
    data_paths = args.data_files or list(DEFAULT_DATA_FILES)
    apply_manifest(args.manifest, data_paths)


if __name__ == "__main__":
    main()
