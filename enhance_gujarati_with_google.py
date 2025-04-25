import json
import os
import time
import sys
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from gtts import gTTS
from tqdm import tqdm
from googletrans import Translator

# Constants
INPUT_FILE = "data/gujarati_words_enhanced.json"
OUTPUT_FILE = "data/gujarati_words_google_enhanced.json"
AUDIO_WORDS_DIR = "audio/words"
AUDIO_EXAMPLES_DIR = "audio/examples"
BATCH_SIZE = 5  # Small batch size to avoid rate limiting
DELAY_BETWEEN_CALLS = 2  # Delay between API calls (in seconds)
DELAY_BETWEEN_BATCHES = 10  # Delay between batches (in seconds)
MAX_RETRIES = 3  # Maximum number of retries for API calls

# Initialize the Google Translate client
translator = Translator()

print("Using googletrans library (free Google Translate API)")

# Note about rate limiting
print("\nNOTE: The free Google Translate API has rate limits. If you encounter rate limiting issues:")
print("1. Try increasing the DELAY_BETWEEN_CALLS and DELAY_BETWEEN_BATCHES constants")
print("2. Run the script during off-peak hours")
print("3. Process the data in smaller batches over multiple days\n")

# Test the translator
try:
    test_result = translator.translate("test", src="en", dest="gu")
    print("Google Translate API connection test successful.")
except Exception as e:
    print(f"Warning: Could not connect to Google Translate API: {e}")
    print("The script will continue and retry during processing.")

def ensure_directories_exist():
    """Create necessary directories if they don't exist."""
    Path(AUDIO_WORDS_DIR).mkdir(parents=True, exist_ok=True)
    Path(AUDIO_EXAMPLES_DIR).mkdir(parents=True, exist_ok=True)
    # Ensure the output directory exists
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

def load_data(file_path: str) -> Dict:
    """Load word data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data: Dict, file_path: str):
    """Save word data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def translate_gujarati(text: str) -> Tuple[str, str]:
    """
    Translate Gujarati text to English and get its romanization in a single call.
    
    Args:
        text: The Gujarati text to translate
        
    Returns:
        A tuple of (translation, romanization)
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Make a single call to get both translation and pronunciation
            result = translator.translate(text, src='gu', dest='en')
            
            # Extract the translation
            translation = ""
            if hasattr(result, 'text'):
                translation = result.text
            
            # Extract the pronunciation/romanization
            romanization = ""
            if hasattr(result, 'pronunciation') and result.pronunciation:
                romanization = result.pronunciation
                print(f"Found pronunciation: {romanization}")
            else:
                # If no pronunciation, try to extract from the translated text
                # Sometimes Google Translate includes romanization in parentheses
                import re
                if hasattr(result, 'text') and result.text:
                    romanization_match = re.search(r'\((.*?)\)', result.text)
                    if romanization_match:
                        romanization = romanization_match.group(1)
                        print(f"Extracted romanization from translation: {romanization}")
                
                # If still no romanization, use character mapping
                if not romanization:
                    print(f"No romanization found for '{text}', using character mapping")
                    gujarati_to_latin = {
                        'અ': 'a', 'આ': 'aa', 'ઇ': 'i', 'ઈ': 'i', 'ઉ': 'u', 'ઊ': 'u',
                        'એ': 'e', 'ઐ': 'ai', 'ઓ': 'o', 'ઔ': 'au', 'ક': 'k', 'ખ': 'kh',
                        'ગ': 'g', 'ઘ': 'gh', 'ચ': 'ch', 'છ': 'chh', 'જ': 'j', 'ઝ': 'jh',
                        'ટ': 't', 'ઠ': 'th', 'ડ': 'd', 'ઢ': 'dh', 'ણ': 'n', 'ત': 't',
                        'થ': 'th', 'દ': 'd', 'ધ': 'dh', 'ન': 'n', 'પ': 'p', 'ફ': 'f',
                        'બ': 'b', 'ભ': 'bh', 'મ': 'm', 'ય': 'y', 'ર': 'r', 'લ': 'l',
                        'વ': 'v', 'શ': 'sh', 'ષ': 'sh', 'સ': 's', 'હ': 'h', 'ળ': 'l',
                        'ં': 'n', 'ઃ': 'h', '઼': '', 'ા': 'a', 'િ': 'i', 'ી': 'i',
                        'ુ': 'u', 'ૂ': 'u', 'ૃ': 'ru', 'ૄ': 'ru', 'ૅ': 'e', 'ે': 'e',
                        'ૈ': 'ai', 'ૉ': 'o', 'ો': 'o', 'ૌ': 'au', '્': '', 'ૐ': 'om'
                    }
                    
                    # Convert each character
                    romanized = ""
                    for char in text:
                        romanized += gujarati_to_latin.get(char, char)
                    
                    romanization = romanized
            
            return translation, romanization
            
        except Exception as e:
            print(f"Error translating '{text}' (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                # Add a random delay before retrying to avoid rate limiting
                sleep_time = DELAY_BETWEEN_CALLS * (1 + random.random())
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
    
    # If all attempts fail, return empty strings
    return "", ""

def save_audio(text: str, file_path: str, lang: str = 'gu'):
    """Save text as audio file using Google Text-to-Speech."""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(file_path)
        return True
    except Exception as e:
        print(f"Error saving audio for '{text}': {e}")
        return False

def process_word(word_id: str, word_entry: List, word_index: int) -> Tuple[str, List]:
    """Process a single word entry with googletrans library."""
    # Extract word data
    gujarati_word = word_entry[0]
    ipa = word_entry[1] if len(word_entry) > 1 else ""
    # We'll replace the alt_ipa with Google's romanization
    pos = word_entry[3] if len(word_entry) > 3 else ""
    definition = word_entry[4] if len(word_entry) > 4 else ""
    example = word_entry[5] if len(word_entry) > 5 else ""
    
    print(f"Processing word: {gujarati_word}")
    
    # Get word translation and romanization in a single call
    _, word_romanization = translate_gujarati(gujarati_word)
    print(f"Romanization: {word_romanization}")
    
    # Initialize new entry with existing data
    new_entry = [
        gujarati_word,
        ipa,
        word_romanization,  # Replace alt_ipa with Google's romanization
        pos,
        definition,
        example
    ]
    
    # Process example if it exists
    if example:
        print(f"Processing example: {example}")
        
        # Get example translation and romanization in a single call
        example_translation, example_romanization = translate_gujarati(example)
        print(f"Example romanization: {example_romanization}")
        print(f"Example translation: {example_translation}")
        
        new_entry.append(example_romanization)
        new_entry.append(example_translation)
        
        # Save example audio
        example_audio_path = f"{AUDIO_EXAMPLES_DIR}/{word_index}.mp3"
        print(f"Saving example audio to {example_audio_path}")
        if save_audio(example, example_audio_path):
            new_entry.append(example_audio_path)
        else:
            new_entry.append("")
    else:
        # Add empty fields if no example
        new_entry.extend(["", "", ""])
    
    # Save word audio
    word_audio_path = f"{AUDIO_WORDS_DIR}/{word_index}.mp3"
    print(f"Saving word audio to {word_audio_path}")
    if save_audio(gujarati_word, word_audio_path):
        new_entry.append(word_audio_path)
    else:
        new_entry.append("")
    
    return word_id, new_entry

def process_batch(batch: Dict[str, List], start_index: int, total_words: int) -> Dict[str, List]:
    """Process a batch of words with rate limiting."""
    updated_batch = {}
    batch_items = list(batch.items())
    
    for i, (word_id, word_entry) in enumerate(tqdm(batch_items, desc=f"Processing batch {start_index//BATCH_SIZE + 1}/{(total_words + BATCH_SIZE - 1)//BATCH_SIZE}")):
        word_index = start_index + i
        updated_id, updated_entry = process_word(word_id, word_entry, word_index)
        updated_batch[updated_id] = updated_entry
        
        # Rate limiting to avoid API throttling (except for the last item in batch)
        if i < len(batch_items) - 1:
            # Add a small random variation to the delay to avoid predictable patterns
            sleep_time = DELAY_BETWEEN_CALLS * (0.8 + 0.4 * random.random())
            time.sleep(sleep_time)
    
    return updated_batch

def main():
    """Main function to enhance Gujarati words with googletrans library."""
    # Ensure directories exist
    ensure_directories_exist()
    
    print(f"Loading data from {INPUT_FILE}...")
    data = load_data(INPUT_FILE)
    total_words = len(data)
    print(f"Loaded {total_words} words")
    
    # Process words in batches
    updated_data = {}
    items = list(data.items())
    
    # For testing with a small subset, uncomment the following line:
    # items = items[:20]  # Process only first 20 words for testing
    
    for i in range(0, len(items), BATCH_SIZE):
        batch = dict(items[i:i+BATCH_SIZE])
        print(f"\nProcessing batch {i//BATCH_SIZE + 1}/{(len(items) + BATCH_SIZE - 1)//BATCH_SIZE}")
        batch_results = process_batch(batch, i, len(items))
        updated_data.update(batch_results)
        
        # Save intermediate results after each batch
        save_data(updated_data, OUTPUT_FILE)
        print(f"Intermediate results saved to {OUTPUT_FILE} ({len(updated_data)}/{total_words} words processed)")
        
        # Add a delay between batches to avoid API rate limits
        if i + BATCH_SIZE < len(items):
            # Add a small random variation to the delay
            sleep_time = DELAY_BETWEEN_BATCHES * (0.8 + 0.4 * random.random())
            print(f"Pausing between batches to avoid API rate limits... ({sleep_time:.2f} seconds)")
            time.sleep(sleep_time)
    
    print(f"\nProcessing complete. Final data saved to {OUTPUT_FILE}")
    print(f"Processed {len(updated_data)}/{total_words} words")
    print(f"Audio files saved to {AUDIO_WORDS_DIR} and {AUDIO_EXAMPLES_DIR}")

if __name__ == "__main__":
    main()
