# Gujarati API

A simple RESTful API for accessing Gujarati language words and their definitions.

## Features

- Get all words with pagination
- Search for words by keyword
- Get specific word details by ID

## Getting Started

### Prerequisites

- Python 3.8 or later
- FastAPI
- Uvicorn

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gujarati_api.git
   cd gujarati_api
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Prepare your data:
   - Place your Gujarati words JSON file in the `data` directory
   - Ensure it's named `gujarati_words.json`

4. Run the application:
   ```
   python main.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

### API Endpoints

- `GET /api/v1/words` - Get all words with pagination
  - Query parameters:
    - `skip` (optional): Number of items to skip (default: 0)
    - `limit` (optional): Maximum number of items to return (default: 25)

- `GET /api/v1/words/search` - Search for words containing a keyword
  - Query parameters:
    - `keyword` (required): Keyword to search for

- `GET /api/v1/words/{word_id}` - Get a word by its ID

## Data Structure

The API uses the following data model for words:

```json
{
  "word": "અકબંધ",
  "ipa": "/\\k.b\\n.d˙\\/",
  "ipa_alt": "\\.k\\.b\\~.dh\\",
  "definitions": [
    {
      "pos": "adj.",
      "definition": "1. intact. 2. neither opened nor broken."
    }
  ],
  "example": "તેણે અકબંધ પેકેજ ખોલ્યું."
}
```

The enhanced data includes:
- Cleaned and validated Gujarati words in Unicode
- Standardized part of speech tags
- Cleaned IPA pronunciations
- Phonetic pronunciations (in the ipa_alt field)
- Example sentences in Gujarati

## Data Enhancement Script

The repository includes a script to enhance the Gujarati word data using AI:

### Features

- Cleans up and validates Gujarati words in Unicode format
- Validates and standardizes part of speech tags
- Cleans up and validates IPA pronunciations
- Converts alternative IPA to phonetic pronunciations
- Adds example sentences in Gujarati
- Uses web search to find examples when needed

### Requirements

- Anthropic API key (Claude)
- Tavily API key (for web searches)

### Usage

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the enhancement script:
   ```
   python enhance_gujarati_words.py
   ```

3. The script will:
   - Process words in batches
   - Save intermediate results after each batch
   - Create an enhanced version at `data/gujarati_words_enhanced.json`

### Configuration

You can modify these parameters in the script:
- `batch_size`: Number of words to process in each batch
- For testing with a small subset, uncomment the line: `# items = items[:20]`

### Testing and Switching Data Files

The repository includes utilities to help you test and switch between different data files:

1. **Test with a small subset**:
   ```
   python test_enhance_gujarati.py
   ```
   This processes only the first 3 words and saves the result to `data/test_enhanced_words.json`.

2. **Verify enhanced data**:
   ```
   python verify_enhanced_data.py
   ```
   This checks if the enhanced data is compatible with the API models.

3. **Switch between data files**:
   ```
   python switch_data_file.py --list     # List all available data files
   python switch_data_file.py --test     # Switch to test data
   python switch_data_file.py --enhanced # Switch to enhanced data
   python switch_data_file.py --original # Restore original data
   ```
   This allows you to easily test the API with different data files without permanently replacing the original data.

4. **Example API usage**:
   ```
   python example_api_usage.py
   ```
   This demonstrates how to use the API with the enhanced data, showing how to access the example sentences and other fields.

5. **Monitor enhancement progress**:
   ```
   python monitor_enhancement.py
   ```
   This provides a real-time monitor of the enhancement process, showing progress, statistics about examples, and estimated time remaining.

6. **Analyze enhancements**:
   ```
   python analyze_enhancements.py
   ```
   This analyzes the differences between the original and enhanced data, providing statistics on changes, examples, and part of speech tags.
   ```
   python analyze_enhancements.py --output analysis_results.json
   ```
   You can also save the analysis results to a JSON file for further processing.

7. **Run complete workflow**:
   ```
   python run_enhancement_workflow.py
   ```
   This runs the complete enhancement workflow in one command, including backup, enhancement, verification, and analysis.
   ```
   python run_enhancement_workflow.py --test
   ```
   Run in test mode to process only a few words.
   ```
   python run_enhancement_workflow.py --replace
   ```
   Replace the original data file with the enhanced data after processing.
   ```
   python run_enhancement_workflow.py --skip-report --skip-analysis
   ```
   Skip generating reports and analysis to speed up the process.
   ```
   python run_enhancement_workflow.py --open-report
   ```
   Automatically open the HTML report in your browser after generation.

8. **Clean up temporary files**:
   ```
   python cleanup.py
   ```
   This lists all temporary and backup files that can be cleaned up.
   ```
   python cleanup.py --backups    # Delete backup files
   python cleanup.py --temp       # Delete temporary files
   python cleanup.py --all        # Delete all backup and temporary files
   python cleanup.py --dry-run    # Show what would be deleted without actually deleting
   ```

9. **Generate visual report**:
   ```
   python generate_report.py
   ```
   This generates an HTML report with charts and statistics comparing the original and enhanced data.
   ```
   python generate_report.py --output custom_report.html
   ```
   You can specify a custom output file for the report.

10. **Open HTML report**:
   ```
   python open_report.py
   ```
   This opens the generated HTML report in your default web browser.
   ```
   python open_report.py --list
   ```
   List all available report files and choose one to open.
   ```
   python open_report.py --file custom_report.html
   ```
   Open a specific report file.

11. **Run API with enhanced data**:
   ```
   python run_api_with_enhanced_data.py
   ```
   This runs the API server with the enhanced data and opens the API documentation in your browser.
   ```
   python run_api_with_enhanced_data.py --data test
   ```
   Run the API with test data instead of enhanced data.
   ```
   python run_api_with_enhanced_data.py --no-browser
   ```
   Run the API without automatically opening the browser.

12. **All-in-one enhancement suite**:
   ```
   python gujarati_enhancement_suite.py
   ```
   This runs the entire enhancement workflow from start to finish with a single command.
   ```
   python gujarati_enhancement_suite.py --test --open-report --run-api
   ```
   Run in test mode, open the report in browser, and start the API server after enhancement.
   ```
   python gujarati_enhancement_suite.py --help
   ```
   See all available options for customizing the enhancement process.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License - see the LICENSE file for details.
