import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
from tavily import TavilyClient
from tqdm import tqdm
import re

# Initialize clients
ANTHROPIC_API_KEY = "sk-ant-api03-"
TAVILY_API_KEY = "tvly-"

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Load the JSON data
def load_data(file_path: str) -> Dict:
    """Load word data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Helper function to extract fields from Claude's response
def extract_field(response: str, field_name: str) -> str:
    """Extract a specific field from Claude's response."""
    pattern = rf"{field_name}:\s*(.*?)(?:\n[A-Z]+:|$)"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

# Search for examples using Tavily
def search_for_example(word: str) -> str:
    """Search for example sentences using the Tavily API."""
    try:
        search_result = tavily_client.search(
            query=f"example sentence with Gujarati word {word}",
            search_depth="advanced"
        )
        
        # Extract potential examples from search results
        example_sentence = ""
        for result in search_result.get('results', []):
            content = result.get('content', '')
            # Look for Gujarati text (contains Unicode Gujarati characters)
            gujarati_matches = re.findall(r'[\u0A80-\u0AFF]+.*?[।.]', content)
            if gujarati_matches:
                for match in gujarati_matches:
                    if word in match:
                        example_sentence = match.strip()
                        break
                if example_sentence:
                    break
        
        return example_sentence
    except Exception as e:
        print(f"Error searching for examples of '{word}': {e}")
        return ""

# Process a single word entry with Claude
def process_word_with_llm(word_entry: List) -> List:
    """Process a word entry with Claude LLM."""
    # Extract word data
    gujarati_word = word_entry[0]
    ipa = word_entry[1] if len(word_entry) > 1 else ""
    ipa_alt = word_entry[2] if len(word_entry) > 2 else ""
    pos = word_entry[3] if len(word_entry) > 3 else ""
    definition = word_entry[4] if len(word_entry) > 4 else ""
    
    # Create prompt for Claude
    prompt = f"""
    I need help cleaning up and enhancing this Gujarati word entry:
    
    Word: {gujarati_word}
    IPA: {ipa}
    Alt IPA (to be converted to phonetic): {ipa_alt}
    Part of Speech: {pos}
    Definition: {definition}
    
    Please:
    1. Clean up and validate the IPA pronunciation
    2. Convert the Alt IPA to a clear phonetic pronunciation
    3. Provide an example sentence using this word in Gujarati (with Unicode)
    
    Return the results in this exact format:
    IPA: [cleaned IPA]
    PHONETIC: [phonetic pronunciation]
    DEFINITION: [original or improved definition]
    EXAMPLE: [example sentence in Gujarati]
    """
    
    # Call Claude API
    try:
        message = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.2,
            system="You are a linguistic expert in Gujarati. Provide accurate, well-formatted responses.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response = message.content[0].text
        
        # Parse Claude's response
        cleaned_ipa = extract_field(response, "IPA")
        phonetic = extract_field(response, "PHONETIC")
        cleaned_definition = extract_field(response, "DEFINITION")
        example = extract_field(response, "EXAMPLE")
        
        # If no example was provided, try to find one via web search
        if not example:
            example = search_for_example(gujarati_word)
        
        # Ensure we have values for all fields (fallback to original if missing)
        cleaned_word = gujarati_word
        cleaned_ipa = cleaned_ipa or ipa
        phonetic = phonetic or ipa_alt
        cleaned_pos = pos
        cleaned_definition = cleaned_definition or definition
        
        # Return updated word entry
        return [cleaned_word, cleaned_ipa, phonetic, cleaned_pos, cleaned_definition, example]
    
    except Exception as e:
        print(f"Error processing word '{gujarati_word}': {e}")
        # Add empty example if not present in original
        if len(word_entry) <= 5:
            word_entry.append("")
        return word_entry

# Process a batch of words
def process_batch(batch: Dict[str, List], batch_size: int = 10) -> Dict[str, List]:
    """Process a batch of words with rate limiting."""
    updated_batch = {}
    for i, (word_id, word_entry) in enumerate(tqdm(batch.items(), desc=f"Processing batch of {len(batch)} words")):
        updated_entry = process_word_with_llm(word_entry)
        updated_batch[word_id] = updated_entry
        
        # Rate limiting to avoid API throttling (except for the last item in batch)
        if i < len(batch) - 1:
            time.sleep(0.5)
    
    return updated_batch

# Main function
def main():
    input_file = "data/gujarati_words.json"
    output_file = "data/gujarati_words_enhanced.json"
    batch_size = 10  # Number of words to process in each batch
    
    print(f"Loading data from {input_file}...")
    data = load_data(input_file)
    total_words = len(data)
    print(f"Loaded {total_words} words")
    
    # Process words in batches
    updated_data = {}
    items = list(data.items())
    
    # For testing with a small subset, uncomment the following line:
    # items = items[:20]  # Process only first 20 words for testing
    
    for i in range(0, len(items), batch_size):
        batch = dict(items[i:i+batch_size])
        print(f"\nProcessing batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size}")
        batch_results = process_batch(batch, batch_size)
        updated_data.update(batch_results)
        
        # Save intermediate results after each batch
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        print(f"Intermediate results saved to {output_file} ({len(updated_data)}/{total_words} words processed)")
    
    print(f"\nProcessing complete. Final data saved to {output_file}")
    print(f"Processed {len(updated_data)}/{total_words} words")

if __name__ == "__main__":
    main()
