from typing import List, Dict, Any
from pydantic import BaseModel
from enum import Enum

class APIProvider(str, Enum):
    AZURE_OPENAI = "azure-openai"
    HUGGINGFACE = "huggingface"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SCIKIT_LEARN = "scikit-learn"
    NUMPY = "numpy"
    PANDAS = "pandas"

class APIFunction(BaseModel):
    name: str
    description: str
    provider: APIProvider
    parameters: List[Dict[str, Any]]
    returns: Dict[str, Any]
    example_code: str
    documentation_url: str

class APIRegistry:
    """Registry for API functions"""
    
    def __init__(self):
        self.functions: Dict[str, APIFunction] = {}
        self._load_default_functions()
    
    def _load_default_functions(self):
        """Load default API functions"""
        # HuggingFace Transformers
        self.register_function(APIFunction(
            name="pipeline",
            description="Create a transformer pipeline for various NLP tasks",
            provider=APIProvider.HUGGINGFACE,
            parameters=[
                {
                    "name": "task",
                    "type": "string",
                    "description": "The task to perform (e.g., sentiment-analysis, text-generation)",
                    "required": True
                },
                {
                    "name": "model",
                    "type": "string",
                    "description": "The model to use for the task",
                    "required": False
                }
            ],
            returns={
                "type": "Pipeline",
                "description": "A pipeline object that can be used for inference"
            },
            example_code="""from transformers import pipeline
nlp = pipeline("sentiment-analysis")
result = nlp("I love this!")[0]
print(f"label: {result['label']}, score: {result['score']:.4f}")""",
            documentation_url="https://huggingface.co/docs/transformers/main_classes/pipelines"
        ))

        # Azure OpenAI
        self.register_function(APIFunction(
            name="AzureOpenAI.chat.completions.create",
            description="Create a chat completion using Azure OpenAI",
            provider=APIProvider.AZURE_OPENAI,
            parameters=[
                {
                    "name": "model",
                    "type": "string",
                    "description": "The name of the model to use (e.g., gpt-4, gpt-35-turbo)",
                    "required": True
                },
                {
                    "name": "messages",
                    "type": "list",
                    "description": "List of message objects with role and content",
                    "required": True
                },
                {
                    "name": "temperature",
                    "type": "float",
                    "description": "Sampling temperature between 0 and 2",
                    "required": False,
                    "default": 0.7
                }
            ],
            returns={
                "type": "ChatCompletion",
                "description": "Chat completion response object"
            },
            example_code="""from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your-api-key",
    api_version="2024-02-15-preview",
    azure_endpoint="your-endpoint"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7
)
print(response.choices[0].message.content)""",
            documentation_url="https://learn.microsoft.com/en-us/azure/ai-services/openai/reference"
        ))
    
    def register_function(self, function: APIFunction):
        """Register a new API function"""
        if function.name in self.functions:
            raise ValueError(f"Function {function.name} already exists")
        self.functions[function.name] = function
    
    def get_function(self, function_name: str) -> APIFunction:
        """Get a function by name"""
        if function_name not in self.functions:
            raise ValueError(f"Function {function_name} not found")
        return self.functions[function_name]
    
    def search_functions(self, query: str) -> List[APIFunction]:
        """Search for functions matching the query"""
        matches = []
        query_lower = query.lower()
        for func in self.functions.values():
            # Check name match
            if query_lower in func.name.lower():
                matches.append(func)
                continue
            
            # Check description match
            if query_lower in func.description.lower():
                matches.append(func)
                continue
            
            # Check parameters match
            for param in func.parameters:
                if query_lower in param["description"].lower():
                    matches.append(func)
                    break
        
        return matches 