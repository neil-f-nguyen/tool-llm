# RapidAPI ToolLLM

A proof of concept implementation of ToolLLM using RapidAPI services.

## Features

- Natural language query processing
- Multiple API integrations:
  - Weather information (Open Weather API)
  - News articles (News API 14)
  - Currency conversion (Currency Converter API)
  - Movie information (AI Movie Recommender)
  - Recipe search (Recipe API)
- Semantic parsing
- Tool registration and execution
- Async API handling

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your RapidAPI key:
```
RAPIDAPI_KEY=your_rapidapi_key_here
```

## Usage

### Starting the Server

```bash
python -m src.rapidapi_toolllm.main
```

The server will start at `http://localhost:8000`

### API Endpoints

#### Chat API
```bash
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "What'\''s the weather in Hanoi?"
}'
```

Example responses:
```json
{
    "tool_name": "weather",
    "parameters": {
        "city": "hanoi",
        "lang": "EN"
    },
    "response": {
        "success": true,
        "data": {
            "temp": 25,
            "humidity": 80,
            "description": "scattered clouds"
        }
    }
}
```

#### News API Examples
```bash
# Get news about Trump's tax
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Get latest news about Trump tax in English"
}'
```

Example response:
```json
{
    "tool_name": "news",
    "parameters": {
        "query": "trump tax",
        "language": "en"
    },
    "response": {
        "success": true,
        "data": {
            "articles": [
                {
                    "title": "Trump's Tax Returns Reveal...",
                    "description": "...",
                    "url": "...",
                    "publishedAt": "..."
                }
            ]
        }
    }
}
```

#### Movie API Examples
```bash
# Search for movie information
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Find information about La La Land"
}'
```

Example response:
```json
{
    "tool_name": "movie",
    "parameters": {
        "title": "La La Land"
    },
    "response": {
        "success": true,
        "data": {
            "id": "313369",
            "title": "La La Land",
            "year": "2016",
            "rating": "8.0",
            "genres": ["Comedy", "Drama", "Musical"]
        }
    }
}
```

### Available Tools

1. Weather Tool (Open Weather API)
   - Get current weather for any city
   - Supports multiple languages
   - Example: "What's the weather in Tokyo in Japanese?"

2. News Tool (News API 14)
   - Get latest news articles
   - Filter by language
   - Example: "Get latest news about AI in English"

3. Currency Converter
   - Convert between currencies
   - Real-time exchange rates
   - Example: "Convert 100 USD to EUR"

4. Movie Search (AI Movie Recommender)
   - Find movie information
   - Get details like release year, rating, genres
   - Example: "Find information about La La Land"

5. Recipe Search
   - Search for recipes
   - Get cooking instructions
   - Example: "Find recipe for chocolate cake"

## Project Structure

```
src/rapidapi_toolllm/
├── core/
│   ├── __init__.py
│   ├── semantic_parser.py
│   └── tool_registry.py
├── models/
│   ├── __init__.py
│   └── tool.py
├── main.py
├── requirements.txt
└── README.md
```

## Error Handling

The API returns standardized error responses:
```json
{
    "success": false,
    "data": null,
    "error": "Error message here"
}
```

Common error codes:
- 400: Bad Request (invalid parameters)
- 404: Tool or Resource Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 