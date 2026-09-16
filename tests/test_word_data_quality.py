import json
import re
import unittest
from pathlib import Path


DATA_PATH = Path("data/gujarati_words_google_enhanced.json")
MANIFEST_PATH = Path("data/word_corrections_2026-09-15.json")
INVALID_GUJARATI = re.compile(
    r"્[ાિીુૂૃૄૅેૈૉોૌ]"
    r"|[ાિીુૂૃૄૅેૈૉોૌ]{2}"
    r"|\\"
    r"|^[ંઃાિીુૂૃૄૅેૈૉોૌ્]"
)
GUJARATI_CHARACTER = re.compile(r"[઀-૿]")


class WordDataQualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_reviewed_corrections_match_active_data(self):
        for word_id, correction in self.manifest["corrections"].items():
            entry = self.words[word_id]
            self.assertEqual(entry[0], correction["word"], word_id)
            self.assertEqual(entry[1], correction["ipa"], word_id)
            self.assertEqual(entry[2], correction["romanization"], word_id)
            if "example" in correction:
                self.assertEqual(entry[5], correction["example"], word_id)
                self.assertEqual(entry[6], correction["example_romanization"], word_id)

    def test_today_word_is_correct(self):
        word = self.words["6740"]
        self.assertEqual(word[0], "હૃદયપરિવર્તન")
        self.assertEqual(word[2], "hṛdayaparivartan")
        self.assertIn("હૃદયપરિવર્તન", word[5])

    def test_words_and_examples_have_valid_character_order(self):
        for word_id, entry in self.words.items():
            self.assertIsNone(INVALID_GUJARATI.search(entry[0]), word_id)
            if len(entry) > 5:
                self.assertIsNone(INVALID_GUJARATI.search(entry[5]), word_id)

    def test_romanizations_do_not_contain_gujarati_characters(self):
        for word_id, entry in self.words.items():
            self.assertIsNone(GUJARATI_CHARACTER.search(entry[2]), word_id)


if __name__ == "__main__":
    unittest.main()
