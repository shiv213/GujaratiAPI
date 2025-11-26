#!/usr/bin/env python3
"""
Script to fix Gujarati Unicode spelling issues using Gemini API with Google grounding.

This script identifies words with potential Unicode issues (like vowel signs at the start)
and uses Gemini to fix the Gujarati word, pronunciation (IPA), and romanization.
"""

import json
import os
import time
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from tqdm import tqdm
from google import genai
from google.genai import types

# Constants
INPUT_FILE = "data/gujarati_words_google_enhanced.json"
OUTPUT_FILE = "data/gujarati_words_google_enhanced.json"  # Overwrite in place
BACKUP_FILE = "data/gujarati_words_google_enhanced_backup.json"
PROGRESS_FILE = "data/fix_progress.json"
BATCH_SIZE = 10  # Process in batches
DELAY_BETWEEN_CALLS = 1.5  # Seconds between API calls
MAX_RETRIES = 3

# Gujarati vowel signs (matras) that should NOT appear at the start of a word
GUJARATI_VOWEL_SIGNS = set([
    '\u0abe',  # ા (aa)
    '\u0abf',  # િ (i)
    '\u0ac0',  # ી (ii)
    '\u0ac1',  # ુ (u)
    '\u0ac2',  # ૂ (uu)
    '\u0ac3',  # ૃ (vocalic r)
    '\u0ac4',  # ૄ (vocalic rr)
    '\u0ac5',  # ૅ (candra e)
    '\u0ac7',  # ે (e)
    '\u0ac8',  # ૈ (ai)
    '\u0ac9',  # ૉ (candra o)
    '\u0acb',  # ો (o)
    '\u0acc',  # ૌ (au)
    '\u0acd',  # ્ (virama/halant)
])

# Gujarati anusvara, visarga, and other signs that shouldn't start words
GUJARATI_COMBINING_SIGNS = set([
    '\u0a82',  # ં (anusvara)
    '\u0a83',  # ઃ (visarga)
])


def load_json(file_path: str) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict, file_path: str):
    """Save JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def has_unicode_issue(word: str) -> bool:
    """
    Check if a Gujarati word has Unicode issues.
    
    Common issues:
    1. Vowel signs (matras) at the start of a word
    2. Combining marks without a base character
    """
    if not word:
        return False
    
    first_char = word[0]
    
    # Check if word starts with a vowel sign (matra)
    if first_char in GUJARATI_VOWEL_SIGNS:
        return True
    
    # Check if word starts with combining signs
    if first_char in GUJARATI_COMBINING_SIGNS:
        return True
    
    return False


def find_problematic_entries(data: Dict) -> List[str]:
    """Find all entries with potential Unicode issues."""
    problematic = []
    
    for word_id, entry in data.items():
        if len(entry) > 0:
            gujarati_word = entry[0]
            if has_unicode_issue(gujarati_word):
                problematic.append(word_id)
    
    return problematic


def load_progress() -> Set[str]:
    """Load progress file to track which entries have been fixed."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()


def save_progress(fixed_ids: Set[str]):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(fixed_ids), f)


def fix_entry_with_gemini(
    client: genai.Client,
    word_id: str,
    entry: List,
    model: str = "gemini-2.5-flash-lite"
) -> Optional[List]:
    """
    Use Gemini with Google grounding to fix a word entry.
    
    Args:
        client: The Gemini API client
        word_id: The word ID
        entry: The word entry [gujarati, ipa, romanization, pos, definition, ...]
        model: The Gemini model to use
        
    Returns:
        Fixed entry or None if failed
    """
    gujarati_word = entry[0]
    current_ipa = entry[1] if len(entry) > 1 else ""
    current_romanization = entry[2] if len(entry) > 2 else ""
    definition = entry[4] if len(entry) > 4 else ""
    example_gujarati = entry[5] if len(entry) > 5 else ""
    
    prompt = f"""You are a Gujarati language expert. Fix the following Gujarati word entry that has Unicode encoding issues.

The word "{gujarati_word}" appears to have a malformed Unicode representation (likely a vowel sign at the beginning without a consonant).

Context clues:
- Current IPA pronunciation: {current_ipa}
- Current romanization: {current_romanization}
- Definition: {definition}
- Example usage: {example_gujarati}

Please provide the CORRECT versions:
1. The correctly spelled Gujarati word (proper Unicode)
2. The IPA pronunciation in square brackets like [ipa.here]
3. The romanization (transliteration to Latin script)

IMPORTANT: 
- Use Google Search to verify the correct Gujarati spelling if needed
- The vowel sign at the start should be attached to or follow a consonant
- For example, "િનચોવવું" should be "નિચોવવું" (nichōvvuṃ)

Respond in this exact JSON format only, no other text:
{{"gujarati": "corrected word", "ipa": "[ipa.here]", "romanization": "latin text"}}"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1,  # Low temperature for more consistent results
                )
            )
            
            # Extract the response text
            response_text = response.text.strip()
            
            # Try to parse JSON from response
            # Handle potential markdown code blocks
            if "```json" in response_text:
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif "```" in response_text:
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            # Parse the JSON
            result = json.loads(response_text)
            
            # Validate the result
            if "gujarati" not in result or "ipa" not in result or "romanization" not in result:
                print(f"  Warning: Incomplete response for {gujarati_word}")
                continue
            
            # Create the fixed entry
            fixed_entry = list(entry)  # Copy original
            fixed_entry[0] = result["gujarati"]
            fixed_entry[1] = result["ipa"]
            fixed_entry[2] = result["romanization"]
            
            return fixed_entry
            
        except json.JSONDecodeError as e:
            print(f"  JSON parse error (attempt {attempt + 1}): {e}")
            print(f"  Response was: {response_text[:200]}...")
        except Exception as e:
            print(f"  Error (attempt {attempt + 1}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(DELAY_BETWEEN_CALLS)
    
    return None


def main():
    """Main function to fix Gujarati word entries."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix Gujarati Unicode spelling issues using Gemini API")
    parser.add_argument("--dry-run", action="store_true", help="Only scan and report issues, don't fix")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of entries to fix")
    args = parser.parse_args()
    
    # Check for API key (only if not dry-run)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not args.dry_run and not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
        print("Or use --dry-run to scan without fixing")
        sys.exit(1)
    
    # Load data
    print(f"Loading data from {INPUT_FILE}...")
    data = load_json(INPUT_FILE)
    total_words = len(data)
    print(f"Loaded {total_words} words")
    
    # Find problematic entries
    print("\nScanning for entries with Unicode issues...")
    problematic_ids = find_problematic_entries(data)
    print(f"Found {len(problematic_ids)} entries with potential issues")
    
    if not problematic_ids:
        print("No problematic entries found!")
        return
    
    # Load progress
    fixed_ids = load_progress()
    remaining_ids = [pid for pid in problematic_ids if pid not in fixed_ids]
    print(f"Already fixed: {len(fixed_ids)}, Remaining: {len(remaining_ids)}")
    
    # Apply limit if specified
    if args.limit:
        remaining_ids = remaining_ids[:args.limit]
        print(f"Limited to {args.limit} entries")
    
    if not remaining_ids:
        print("All problematic entries have been fixed!")
        return
    
    # Show examples
    print("\nExamples of problematic entries:")
    for i, word_id in enumerate(remaining_ids[:10]):
        entry = data[word_id]
        first_char = entry[0][0]
        char_code = hex(ord(first_char))
        print(f"  ID {word_id}: '{entry[0]}' (starts with {char_code}) -> {entry[4][:50] if len(entry) > 4 else 'no definition'}...")
    
    # Dry run mode - just report
    if args.dry_run:
        print(f"\n{'=' * 50}")
        print(f"DRY RUN - No changes made")
        print(f"Total problematic entries: {len(problematic_ids)}")
        print(f"Would fix: {len(remaining_ids)} entries")
        print("\nTo actually fix these, run without --dry-run:")
        print(f"  GEMINI_API_KEY='your-key' uv run fix_gujarati_spelling.py")
        return
    
    # Create backup if it doesn't exist
    if not os.path.exists(BACKUP_FILE):
        print(f"\nCreating backup at {BACKUP_FILE}...")
        save_json(data, BACKUP_FILE)
    
    # Initialize Gemini client
    print("\nInitializing Gemini API client...")
    client = genai.Client(api_key=api_key)
    
    # Ask for confirmation
    print(f"\nReady to fix {len(remaining_ids)} entries using Gemini API with Google grounding.")
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        return
    
    # Process entries
    print("\nProcessing entries...")
    fixed_count = 0
    failed_count = 0
    
    for i, word_id in enumerate(tqdm(remaining_ids, desc="Fixing entries")):
        entry = data[word_id]
        original_word = entry[0]
        
        # Fix the entry
        fixed_entry = fix_entry_with_gemini(client, word_id, entry)
        
        if fixed_entry:
            data[word_id] = fixed_entry
            fixed_ids.add(word_id)
            fixed_count += 1
            
            # Show progress
            if fixed_count % 10 == 0:
                print(f"\n  Fixed: {original_word} -> {fixed_entry[0]}")
        else:
            failed_count += 1
            print(f"\n  Failed to fix: {original_word}")
        
        # Save progress periodically
        if (i + 1) % BATCH_SIZE == 0:
            save_json(data, OUTPUT_FILE)
            save_progress(fixed_ids)
            print(f"\n  Saved progress: {fixed_count} fixed, {failed_count} failed")
        
        # Rate limiting
        time.sleep(DELAY_BETWEEN_CALLS)
    
    # Final save
    save_json(data, OUTPUT_FILE)
    save_progress(fixed_ids)
    
    print(f"\n{'=' * 50}")
    print(f"Processing complete!")
    print(f"  Fixed: {fixed_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Output saved to: {OUTPUT_FILE}")
    
    # Clean up progress file if all done
    if failed_count == 0 and len(remaining_ids) == fixed_count:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print(f"  Removed progress file: {PROGRESS_FILE}")


if __name__ == "__main__":
    main()

