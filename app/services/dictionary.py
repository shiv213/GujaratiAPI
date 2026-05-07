import json
import os
import random
from typing import Dict, List, Optional
from pathlib import Path
from fastapi.responses import FileResponse
from ..models.word import Word, WordDefinition


API_PREFIX = "/api/v1"


class DictionaryService:
    """Service for managing the dictionary data."""
    
    def __init__(self, data_file: str):
        """Initialize the dictionary service with a data file.
        
        Args:
            data_file: Path to the JSON data file
        """
        self.data_file = data_file
        self.word_data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load word data from JSON file.
        
        Returns:
            Dict containing the word data
        """
        data_path = Path(self.data_file)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_words(self, skip: int = 0, limit: int = 25) -> List[Word]:
        """Get all words with pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of Word objects
        """
        words = []
        word_list = list(self.word_data.items())[skip:skip+limit]
        
        for word_id, word_entry in word_list:
            words.append(self._convert_to_word_model(word_id, word_entry))
        
        return words
    
    def search_word(self, keyword: str, skip: int = 0, limit: int = 25) -> List[Word]:
        """Search for words containing the keyword.
        
        Args:
            keyword: Keyword to search for
            skip: Number of matching items to skip
            limit: Maximum number of matching items to return
            
        Returns:
            List of matching Word objects
        """
        results = []
        keyword_lower = keyword.casefold()
        
        for word_id, word_entry in self.word_data.items():
            searchable_fields = [
                word_entry[0] if len(word_entry) > 0 else "",
                word_entry[1] if len(word_entry) > 1 else "",
                word_entry[2] if len(word_entry) > 2 else "",
                word_entry[3] if len(word_entry) > 3 else "",
                word_entry[4] if len(word_entry) > 4 else "",
                word_entry[5] if len(word_entry) > 5 else "",
                word_entry[6] if len(word_entry) > 6 else "",
                word_entry[7] if len(word_entry) > 7 else "",
            ]
            if any(keyword_lower in field.casefold() for field in searchable_fields if field):
                results.append(self._convert_to_word_model(word_id, word_entry))

        return results[skip:skip+limit]

    def get_words_by_text(self, word: str) -> List[Word]:
        """Get all entries matching a Gujarati word exactly.

        Args:
            word: Gujarati word text

        Returns:
            List of matching Word objects
        """
        results = []
        for word_id, word_entry in self.word_data.items():
            if len(word_entry) > 0 and word_entry[0] == word:
                results.append(self._convert_to_word_model(word_id, word_entry))
        return results

    def get_random_words(self, limit: int = 10) -> List[Word]:
        """Get random words for practice or discovery.

        Args:
            limit: Maximum number of words to return

        Returns:
            List of random Word objects
        """
        items = list(self.word_data.items())
        sample_size = min(max(limit, 0), len(items))
        return [
            self._convert_to_word_model(word_id, word_entry)
            for word_id, word_entry in random.sample(items, sample_size)
        ]

    def count_words(self) -> int:
        """Get the total number of word entries."""
        return len(self.word_data)

    def suggest_words(self, keyword: str, limit: int = 10) -> List[Word]:
        """Suggest words by exact prefix first, then broader search.

        Args:
            keyword: Gujarati or romanized prefix/search text
            limit: Maximum number of suggestions to return

        Returns:
            List of suggested Word objects
        """
        keyword_lower = keyword.casefold()
        prefix_results = []
        broader_results = []

        for word_id, word_entry in self.word_data.items():
            word = word_entry[0] if len(word_entry) > 0 else ""
            romanization = word_entry[2] if len(word_entry) > 2 else ""

            if word.casefold().startswith(keyword_lower) or romanization.casefold().startswith(keyword_lower):
                prefix_results.append(self._convert_to_word_model(word_id, word_entry))
                continue

            searchable_fields = [
                word,
                romanization,
                word_entry[4] if len(word_entry) > 4 else "",
                word_entry[5] if len(word_entry) > 5 else "",
                word_entry[7] if len(word_entry) > 7 else "",
            ]
            if any(keyword_lower in field.casefold() for field in searchable_fields if field):
                broader_results.append(self._convert_to_word_model(word_id, word_entry))

        return (prefix_results + broader_results)[:limit]
    
    def get_word_by_id(self, word_id: str) -> Optional[Word]:
        """Get a word by its ID.
        
        Args:
            word_id: ID of the word to get
            
        Returns:
            Word object if found, None otherwise
        """
        if word_id in self.word_data:
            return self._convert_to_word_model(word_id, self.word_data[word_id])
        return None
    
    def get_audio_file(self, audio_path: str) -> Optional[FileResponse]:
        """Get an audio file by its path.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            FileResponse if found, None otherwise
        """
        if not audio_path or not os.path.exists(audio_path):
            return None
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=os.path.basename(audio_path)
        )
    
    def _convert_to_word_model(self, word_id: str, word_entry: List) -> Word:
        """Convert a word entry from the JSON data to a Word model.
        
        Args:
            word_id: Stable word ID from the data file
            word_entry: List containing word data
            
        Returns:
            Word model
        """
        word = word_entry[0]
        ipa = word_entry[1] if len(word_entry) > 1 else None
        romanization = word_entry[2] if len(word_entry) > 2 else None
        
        # Get part of speech and definition
        pos = word_entry[3] if len(word_entry) > 3 else ""
        definition = word_entry[4] if len(word_entry) > 4 else ""
        
        # Get example if available
        example = word_entry[5] if len(word_entry) > 5 else None
        
        # Get enhanced data if available
        example_romanization = word_entry[6] if len(word_entry) > 6 else None
        example_translation = word_entry[7] if len(word_entry) > 7 else None
        example_audio = word_entry[8] if len(word_entry) > 8 else None
        word_audio = word_entry[9] if len(word_entry) > 9 else None
        has_example_audio = bool(example_audio and os.path.exists(example_audio))
        has_word_audio = bool(word_audio and os.path.exists(word_audio))
        
        # Create WordDefinition object
        word_def = WordDefinition(pos=pos, definition=definition)
        
        return Word(
            id=word_id,
            word=word,
            ipa=ipa,
            romanization=romanization,
            definitions=[word_def],
            example=example,
            example_romanization=example_romanization,
            example_translation=example_translation,
            example_audio=example_audio,
            word_audio=word_audio,
            example_audio_url=f"{API_PREFIX}/audio/example/{word_id}" if has_example_audio else None,
            word_audio_url=f"{API_PREFIX}/audio/word/{word_id}" if has_word_audio else None,
            has_example_audio=has_example_audio,
            has_word_audio=has_word_audio
        )
