from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from ..models.word import Word
from ..services.dictionary import DictionaryService

router = APIRouter(prefix="/api/v1", tags=["words"])

# Dependency to get the dictionary service
def get_dictionary_service():
    """Get an instance of the dictionary service."""
    return DictionaryService("data/gujarati_words_google_enhanced.json")

@router.get("/words", response_model=List[Word])
async def get_words(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(25, ge=1, le=500, description="Maximum number of items to return"),
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get all words with pagination."""
    return dict_service.get_all_words(skip=skip, limit=limit)

@router.get("/words/search", response_model=List[Word])
async def search_words(
    keyword: str = Query(..., description="Keyword to search for"),
    skip: int = Query(0, ge=0, description="Number of matching items to skip"),
    limit: int = Query(25, ge=1, le=500, description="Maximum number of matching items to return"),
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Search for words containing the keyword across Gujarati, romanization, IPA, definitions, and examples."""
    results = dict_service.search_word(keyword, skip=skip, limit=limit)
    if not results:
        return []
    return results

@router.get("/words/suggest", response_model=List[Word])
async def suggest_words(
    keyword: str = Query(..., min_length=1, description="Gujarati or romanized text to suggest from"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of suggestions to return"),
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Suggest words for typeahead. Exact word/romanization prefixes are ranked first."""
    return dict_service.suggest_words(keyword=keyword, limit=limit)

@router.get("/words/random", response_model=List[Word])
async def get_random_words(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of random words to return"),
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get random words for practice or discovery."""
    return dict_service.get_random_words(limit=limit)

@router.get("/words/count")
async def get_word_count(
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get the total number of word entries."""
    return {"count": dict_service.count_words()}

@router.get("/words/by-word/{word}", response_model=List[Word])
async def get_words_by_text(
    word: str,
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get all dictionary entries matching a Gujarati word exactly."""
    return dict_service.get_words_by_text(word)

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

@router.get("/audio/word/{word_id}")
async def get_word_audio(
    word_id: str,
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get the audio file for a word."""
    word = dict_service.get_word_by_id(word_id)
    if not word or not word.word_audio:
        raise HTTPException(status_code=404, detail="Word audio not found")
    
    audio_response = dict_service.get_audio_file(word.word_audio)
    if not audio_response:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return audio_response

@router.get("/audio/example/{word_id}")
async def get_example_audio(
    word_id: str,
    dict_service: DictionaryService = Depends(get_dictionary_service)
):
    """Get the audio file for an example sentence."""
    word = dict_service.get_word_by_id(word_id)
    if not word or not word.example_audio:
        raise HTTPException(status_code=404, detail="Example audio not found")
    
    audio_response = dict_service.get_audio_file(word.example_audio)
    if not audio_response:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return audio_response
