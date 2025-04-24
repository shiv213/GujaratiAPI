from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..models.word import Word
from ..services.dictionary import DictionaryService

router = APIRouter(prefix="/api/v1", tags=["words"])

# Dependency to get the dictionary service
def get_dictionary_service():
    """Get an instance of the dictionary service."""
    return DictionaryService("data/gujarati_words_enhanced.json")

@router.get("/words", response_model=List[Word])
async def get_words(
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(25, description="Maximum number of items to return"),
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get all words with pagination."""
    return dict_service.get_all_words(skip=skip, limit=limit)

@router.get("/words/search", response_model=List[Word])
async def search_words(
    keyword: str = Query(..., description="Keyword to search for"),
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Search for words containing the keyword."""
    results = dict_service.search_word(keyword)
    if not results:
        return []
    return results

@router.get("/words/{word_id}", response_model=Word)
async def get_word(
    word_id: str, 
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get a word by its ID."""
    word = dict_service.get_word_by_id(word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word