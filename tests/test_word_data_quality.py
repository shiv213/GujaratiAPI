import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path


DATA_PATH = Path("data/gujarati_words_google_enhanced.json")
MANIFEST_PATHS = (
    Path("data/word_corrections_2026-09-15.json"),
    Path("data/word_corrections_2026-09-30.json"),
)
AUDIO_MANIFEST_PATH = Path("data/word_audio_corrections_2026-09-30.json")
PRONUNCIATION_AUDIT_PATH = Path(
    "data/pronunciation_audio_audit_2026-09-30.json"
)
INVALID_GUJARATI = re.compile(
    r"્[ાિીુૂૃૄૅેૈૉોૌ]"
    r"|[ાિીુૂૃૄૅેૈૉોૌ]{2}"
    r"|(?<![ક-હ])[ાિીુૂૃૄૅેૈૉોૌ]"
    r"|\\"
    r"|^[ંઃાિીુૂૃૄૅેૈૉોૌ્]"
)
GUJARATI_CHARACTER = re.compile(r"[઀-૿]")


class WordDataQualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.manifests = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in MANIFEST_PATHS
        ]
        cls.audio_manifest = json.loads(
            AUDIO_MANIFEST_PATH.read_text(encoding="utf-8")
        )
        cls.pronunciation_audit = json.loads(
            PRONUNCIATION_AUDIT_PATH.read_text(encoding="utf-8")
        )

    def test_reviewed_corrections_match_active_data(self):
        for manifest in self.manifests:
            for word_id, correction in manifest["corrections"].items():
                entry = self.words[word_id]
                self.assertEqual(entry[0], correction["word"], word_id)
                self.assertEqual(entry[1], correction["ipa"], word_id)
                self.assertEqual(entry[2], correction["romanization"], word_id)
                if "example" in correction:
                    self.assertEqual(entry[5], correction["example"], word_id)
                    self.assertEqual(
                        entry[6], correction["example_romanization"], word_id
                    )
                if "word_audio_sha256" in correction:
                    self.assertEqual(
                        hashlib.sha256(Path(entry[9]).read_bytes()).hexdigest(),
                        correction["word_audio_sha256"],
                        word_id,
                    )
                if "example_audio_sha256" in correction:
                    self.assertEqual(
                        hashlib.sha256(Path(entry[8]).read_bytes()).hexdigest(),
                        correction["example_audio_sha256"],
                        word_id,
                    )

    def test_today_word_is_correct(self):
        word = self.words["6740"]
        self.assertEqual(word[0], "હૃદયપરિવર્તન")
        self.assertEqual(word[2], "hṛdayaparivartan")
        self.assertIn("હૃદયપરિવર્તન", word[5])

    def test_siskaro_example_is_correct(self):
        verb = self.words["6398"]
        self.assertEqual(verb[7], "When a snake gets angry, it starts to hiss.")

        word = self.words["6399"]
        self.assertEqual(word[0], "સિસકારો")
        self.assertEqual(word[2], "siskaro")
        self.assertEqual(word[5], "સાપનો સિસકારો સાંભળીને તે ડરી ગયો.")
        self.assertEqual(word[6], "sapno siskaro sanbhline te dri gyo.")
        self.assertEqual(
            word[7], "He got scared upon hearing the snake's hiss."
        )
        self.assertEqual(
            hashlib.sha256(Path(word[9]).read_bytes()).hexdigest(),
            "64ce51c6f2534348457c8f3df0500a7e08371c0f3b39a724ba8ac320bd23836f",
        )

    def test_reviewed_word_audio_matches_manifest(self):
        entries = self.audio_manifest["entries"]
        self.assertEqual(len(entries), self.audio_manifest["count"])
        self.assertEqual(len(entries), 420)
        for correction in entries:
            word_id = correction["id"]
            word = self.words[word_id]
            self.assertEqual(word[0], correction["word"], word_id)
            self.assertEqual(
                hashlib.sha256(Path(word[9]).read_bytes()).hexdigest(),
                correction["sha256"],
                word_id,
            )

    def test_words_and_examples_have_valid_character_order(self):
        for word_id, entry in self.words.items():
            self.assertIsNone(INVALID_GUJARATI.search(entry[0]), word_id)
            self.assertIsNone(INVALID_GUJARATI.search(entry[5]), word_id)

    def test_words_and_examples_are_complete_gujarati_text(self):
        for word_id, entry in self.words.items():
            self.assertEqual(len(entry), 10, word_id)
            for text in (entry[0], entry[5]):
                self.assertTrue(text.strip(), word_id)
                self.assertEqual(text, unicodedata.normalize("NFC", text), word_id)
                foreign_letters = [
                    character
                    for character in text
                    if character.isalpha()
                    and not "\u0a80" <= character <= "\u0aff"
                ]
                self.assertEqual(foreign_letters, [], word_id)
            for audio_path in (entry[8], entry[9]):
                self.assertTrue(audio_path, word_id)
                self.assertTrue(Path(audio_path).is_file(), word_id)
                self.assertGreater(Path(audio_path).stat().st_size, 1_000, word_id)

    def test_regenerated_pronunciation_audio_matches_source(self):
        entries = self.pronunciation_audit["entries"]
        self.assertEqual(len(entries), self.pronunciation_audit["count"])
        self.assertEqual(len(entries), 59)
        for correction in entries:
            word_id = correction["id"]
            word = self.words[word_id]
            text_index = 0 if correction["kind"] == "word" else 5
            path_index = 9 if correction["kind"] == "word" else 8
            self.assertEqual(word[text_index], correction["text"], word_id)
            self.assertEqual(word[path_index], correction["path"], word_id)
            self.assertEqual(
                hashlib.sha256(Path(correction["path"]).read_bytes()).hexdigest(),
                correction["sha256"],
                word_id,
            )

    def test_romanizations_do_not_contain_gujarati_characters(self):
        for word_id, entry in self.words.items():
            self.assertIsNone(GUJARATI_CHARACTER.search(entry[2]), word_id)


if __name__ == "__main__":
    unittest.main()
