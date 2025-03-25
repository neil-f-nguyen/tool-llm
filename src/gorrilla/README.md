# Gorilla API POC

This is a proof-of-concept implementation of the Gorilla API, based on the paper from Berkeley. The project provides an API that helps developers write code by suggesting and using appropriate API functions from various ML/AI libraries.

## Features

- API function registry with detailed function specifications
- Semantic search for finding relevant API functions
- Code generation using Azure OpenAI
- Support for multiple ML/AI libraries:
  - HuggingFace Transformers
  - PyTorch
  - TensorFlow (coming soon)
  - Scikit-learn (coming soon)
  - NumPy (coming soon)
  - Pandas (coming soon)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   ```

## Running the API

Start the FastAPI server:
```bash
cd src
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /generate
Generate code based on a natural language query.

Request body:
```json
{
    "query": "create a sentiment analysis pipeline"
}
```

### GET /functions
List all available API functions.

## Example Usage

1. List available functions:
   ```bash
   curl http://localhost:8000/functions
   ```

2. Generate code:
   ```bash
   curl -X POST http://localhost:8000/generate \
        -H "Content-Type: application/json" \
        -d '{"query": "create a sentiment analysis pipeline"}'
   ```

## Project Structure

```
gorilla/
├── src/
│   └── main.py
├── requirements.txt
└── README.md
```

## Future Improvements

1. Add more API functions from popular ML/AI libraries
2. Implement function versioning
3. Add support for custom API functions
4. Improve code generation with better prompts
5. Add unit tests and integration tests
6. Add API documentation using Swagger/OpenAPI
7. Implement caching for frequently used functions
8. Add support for function composition

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License 