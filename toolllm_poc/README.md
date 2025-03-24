# ToolLLM POC with Azure OpenAI

This is a Proof of Concept (POC) of the ToolLLM application using Azure OpenAI API.

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Fill in your Azure OpenAI information in the `.env` file:
  - AZURE_OPENAI_API_KEY
  - AZURE_OPENAI_ENDPOINT
  - AZURE_OPENAI_DEPLOYMENT_NAME

## Running the Application

```bash
cd src
python main.py
```

The application will run on `http://localhost:8000`

## API Endpoints

### 1. GET /tools
Get the list of available tools

### 2. POST /chat
Send a query and receive AI response

Request body:
```json
{
    "tools": [
        {
            "name": "calculator",
            "description": "Perform basic mathematical operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "num1": {"type": "number"},
                    "num2": {"type": "number"}
                },
                "required": ["operation", "num1", "num2"]
            }
        }
    ],
    "query": "Calculate 5 + 3"
}
```

## Usage Examples

1. Get list of tools:
```bash
curl http://localhost:8000/tools
```

2. Send a query:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tools": [{"name": "calculator", "description": "Perform basic mathematical operations", "parameters": {"type": "object", "properties": {"operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}, "num1": {"type": "number"}, "num2": {"type": "number"}}, "required": ["operation", "num1", "num2"]}}],
    "query": "Calculate 5 + 3"
  }'
``` 