from typing import List, Optional
from pydantic import BaseModel


class WordDefinition(BaseModel):
    """Model for word definitions."""
    pos: str  # Part of speech (e.g., "adj.", "masc.", "fem.", "neut.")
    definition: str


class Word(BaseModel):
    """Model for Gujarati words."""
    word: str
    ipa: Optional[str] = None
    romanization: Optional[str] = None  # Romanization of the word (previously ipa_alt)
    definitions: List[WordDefinition]
    example: Optional[str] = None  # Example sentence in Gujarati
    example_romanization: Optional[str] = None  # Romanization of the example sentence
    example_translation: Optional[str] = None  # English translation of the example sentence
    example_audio: Optional[str] = None  # Path to the example audio file
    word_audio: Optional[str] = None  # Path to the word audio file
