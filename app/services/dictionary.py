import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from fastapi.responses import FileResponse
from ..models.word import Word, WordDefinition

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
        word_list = list(self.word_data.values())[skip:skip+limit]
        
        for word_entry in word_list:
            words.append(self._convert_to_word_model(word_entry))
        
        return words
    
    def search_word(self, keyword: str) -> List[Word]:
        """Search for words containing the keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching Word objects
        """
        results = []
        keyword_lower = keyword.lower()
        
        for word_id, word_entry in self.word_data.items():
            # Search in word
            if keyword_lower in word_entry[0].lower():
                results.append(self._convert_to_word_model(word_entry))
                continue
                
            # Search in definition
            if len(word_entry) >= 5 and keyword_lower in word_entry[4].lower():
                results.append(self._convert_to_word_model(word_entry))
                continue
                
            # Search in example translation
            if len(word_entry) >= 8 and keyword_lower in word_entry[7].lower():
                results.append(self._convert_to_word_model(word_entry))
        
        return results
    
    def get_word_by_id(self, word_id: str) -> Optional[Word]:
        """Get a word by its ID.
        
        Args:
            word_id: ID of the word to get
            
        Returns:
            Word object if found, None otherwise
        """
        if word_id in self.word_data:
            return self._convert_to_word_model(self.word_data[word_id])
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
    
    def _convert_to_word_model(self, word_entry: List) -> Word:
        """Convert a word entry from the JSON data to a Word model.
        
        Args:
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
        
        # Create WordDefinition object
        word_def = WordDefinition(pos=pos, definition=definition)
        
        return Word(
            word=word,
            ipa=ipa,
            romanization=romanization,
            definitions=[word_def],
            example=example,
            example_romanization=example_romanization,
            example_translation=example_translation,
            example_audio=example_audio,
            word_audio=word_audio
        )
