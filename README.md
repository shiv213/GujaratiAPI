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
  ]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License - see the LICENSE file for details.