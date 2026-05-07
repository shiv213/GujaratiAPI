import unittest

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class WordsApiTest(unittest.TestCase):
    def test_words_include_stable_ids_and_audio_urls(self):
        response = client.get("/api/v1/words", params={"limit": 1})

        self.assertEqual(response.status_code, 200)
        words = response.json()
        self.assertEqual(len(words), 1)

        word = words[0]
        self.assertEqual(word["id"], "0")
        self.assertEqual(word["word"], "અકબંધ")
        self.assertEqual(word["word_audio_url"], "/api/v1/audio/word/0")
        self.assertEqual(word["example_audio_url"], "/api/v1/audio/example/0")
        self.assertTrue(word["has_word_audio"])
        self.assertTrue(word["has_example_audio"])

    def test_search_supports_romanization(self):
        response = client.get("/api/v1/words/search", params={"keyword": "akbndh", "limit": 5})

        self.assertEqual(response.status_code, 200)
        words = response.json()
        self.assertTrue(any(word["id"] == "0" and word["word"] == "અકબંધ" for word in words))

    def test_exact_word_lookup_returns_matching_entries(self):
        response = client.get("/api/v1/words/by-word/પ્રેમ")

        self.assertEqual(response.status_code, 200)
        words = response.json()
        self.assertEqual([word["id"] for word in words], ["3660"])

    def test_suggest_prioritizes_prefix_matches(self):
        response = client.get("/api/v1/words/suggest", params={"keyword": "prem", "limit": 3})

        self.assertEqual(response.status_code, 200)
        words = response.json()
        self.assertGreaterEqual(len(words), 1)
        self.assertEqual(words[0]["id"], "3660")

    def test_count_returns_total_entries(self):
        response = client.get("/api/v1/words/count")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"count": 6776})


if __name__ == "__main__":
    unittest.main()
