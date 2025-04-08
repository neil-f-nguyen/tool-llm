# RapidAPI ToolLLM

A proof of concept implementation of a ToolLLM system that integrates various RapidAPI services.

## Features

- **Weather API**: Open Weather API for current weather data
- **News API**: News API 14 for searching news articles
- **Currency Converter API**: For converting between currencies
- **Movie API**: AI Movie Recommender for fetching movie information
- **Recipe API**: For searching recipes
- **Azure GPT Integration**: Large Action Model (LAM) for advanced natural language processing

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   RAPIDAPI_KEY=your_rapidapi_key
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_API_BASE=your_azure_openai_api_base
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   ```

## Usage

### Starting the Server

```
python -m src.rapidapi_toolllm.main
```

### API Endpoints

#### Chat Endpoint

```
POST /chat
```

Request body:
```json
{
  "message": "What's the weather in Hanoi?",
  "use_llm": false
}
```

The `use_llm` parameter determines whether to use the traditional regex-based parsing or the Azure GPT-based processing.

Response:
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
      "coord": {
        "lon": 105.8412,
        "lat": 21.0245
      },
      "weather": [
        {
          "id": 800,
          "main": "Clear",
          "description": "clear sky",
          "icon": "01d"
        }
      ],
      "base": "stations",
      "main": {
        "temp": 28.99,
        "feels_like": 28.99,
        "temp_min": 28.99,
        "temp_max": 28.99,
        "pressure": 1013,
        "humidity": 65
      },
      "visibility": 10000,
      "wind": {
        "speed": 2.06,
        "deg": 90
      },
      "clouds": {
        "all": 0
      },
      "dt": 1617789600,
      "sys": {
        "type": 1,
        "id": 9308,
        "country": "VN",
        "sunrise": 1617759347,
        "sunset": 1617803971
      },
      "timezone": 25200,
      "id": 1581130,
      "name": "Hanoi",
      "cod": 200
    }
  },
  "reasoning": "Query matched weather tool with parameters: {'city': 'hanoi', 'lang': 'EN'}"
}
```

#### List Tools Endpoint

```
GET /tools
```

Response:
```json
[
  {
    "name": "weather",
    "description": "Get current weather for a location",
    "type": "api",
    "parameters": {
      "city": {
        "type": "string",
        "description": "City name (e.g., 'hanoi', 'london')",
        "required": true
      },
      "lang": {
        "type": "string",
        "description": "Language code (e.g., 'EN', 'VI')",
        "required": false,
        "default": "EN"
      }
    },
    "api_endpoint": "https://open-weather13.p.rapidapi.com/city/{city}/{lang}",
    "api_method": "GET",
    "api_headers": {
      "X-RapidAPI-Key": "your_rapidapi_key",
      "X-RapidAPI-Host": "open-weather13.p.rapidapi.com"
    },
    "examples": [
      "What's the weather in Hanoi?",
      "Get weather for Tokyo in Japanese",
      "How's the weather in New York in English?"
    ]
  },
  // Other tools...
]
```

#### Register Tool Endpoint

```
POST /tools
```

Request body:
```json
{
  "name": "custom_tool",
  "description": "A custom tool description",
  "type": "api",
  "parameters": {
    "param1": {
      "type": "string",
      "description": "Parameter 1 description",
      "required": true
    }
  },
  "api_endpoint": "https://api.example.com/endpoint",
  "api_method": "GET",
  "api_headers": {
    "Authorization": "Bearer your_token"
  },
  "examples": [
    "Example usage 1",
    "Example usage 2"
  ]
}
```

#### Health Check Endpoint

```
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

## Azure GPT Integration

The project now includes integration with Azure GPT for advanced natural language processing. This allows for:

1. **Improved Query Understanding**: Azure GPT can better understand complex queries that might be difficult for regex-based parsing.
2. **Multi-step Execution**: The system can now handle queries that require multiple tool executions in sequence.
3. **Contextual Responses**: Azure GPT maintains conversation history for more contextual responses.

To use Azure GPT, set the `use_llm` parameter to `true` in your chat request:

```json
{
  "message": "What's the weather in Hanoi and then find news about Vietnam?",
  "use_llm": true
}
```

Azure GPT will:
1. Understand that this is a multi-step query
2. First fetch the weather in Hanoi
3. Then search for news about Vietnam
4. Combine the results into a coherent response

## Examples

### Weather API

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What'\''s the weather in Tokyo in Japanese?", "use_llm": false}'
```

### News API

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Get latest news about AI in English", "use_llm": false}'
```

### Currency Converter API

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Convert 100 USD to EUR", "use_llm": false}'
```

### Movie API

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Find information about La La Land", "use_llm": false}'
```

### Recipe API

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Find a recipe for pasta carbonara", "use_llm": false}'
```

### Azure GPT Example

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What'\''s the weather in Paris and suggest a movie to watch on a rainy day?", "use_llm": true}'
```

## License

MIT 