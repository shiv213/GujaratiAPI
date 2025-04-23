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
    ipa_alt: Optional[str] = None
    definitions: List[WordDefinition]