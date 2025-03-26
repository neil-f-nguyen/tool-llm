from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import json
import aiohttp
import asyncio
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

# Load environment variables from .env file
load_dotenv()

class Action(BaseModel):
    """
    Model class representing an executable action in the system.
    This is the core building block of the Gorilla LAM.
    
    Attributes:
        name: Unique identifier for the action
        description: Human-readable description of what the action does
        parameters: Dictionary defining the required and optional parameters
        required_permissions: List of permissions needed to execute this action
        examples: List of example queries that would trigger this action
        api_spec: Optional OpenAPI specification for API-based actions
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    required_permissions: List[str] = []
    examples: List[str] = []
    api_spec: Optional[Dict[str, Any]] = None

class ActionRegistry:
    """
    Registry class to manage all available actions in the system.
    Provides methods to register, retrieve, and list actions.
    """
    
    def __init__(self):
        # Initialize empty dictionary to store actions
        self.actions: Dict[str, Action] = {}
        # Register default actions on initialization
        self._register_default_actions()
    
    def _register_default_actions(self):
        """
        Register the default set of actions that come with the system.
        These are basic actions that demonstrate the core functionality.
        """
        # Register file reading action
        self.register_action(Action(
            name="read_file",
            description="Read contents of a file",
            parameters={
                "file_path": {"type": "string", "description": "Path to the file"},
                "start_line": {"type": "integer", "description": "Starting line number", "optional": True},
                "end_line": {"type": "integer", "description": "Ending line number", "optional": True}
            },
            required_permissions=["file.read"],
            examples=[
                "read the contents of config.json",
                "read lines 1-10 of main.py"
            ]
        ))
        
        # Register HTTP request action with OpenAPI specification
        self.register_action(Action(
            name="http_request",
            description="Make an HTTP request",
            parameters={
                "method": {"type": "string", "description": "HTTP method"},
                "url": {"type": "string", "description": "URL to request"},
                "headers": {"type": "object", "description": "Request headers", "optional": True},
                "body": {"type": "object", "description": "Request body", "optional": True}
            },
            required_permissions=["network.request"],
            examples=[
                "get data from https://api.example.com",
                "post data to https://api.example.com"
            ],
            api_spec={
                "openapi": "3.0.0",
                "info": {
                    "title": "HTTP API",
                    "version": "1.0.0"
                },
                "paths": {
                    "/": {
                        "get": {
                            "summary": "Make HTTP request",
                            "parameters": [
                                {
                                    "name": "method",
                                    "in": "query",
                                    "required": True,
                                    "schema": {"type": "string"}
                                },
                                {
                                    "name": "url",
                                    "in": "query",
                                    "required": True,
                                    "schema": {"type": "string"}
                                }
                            ]
                        }
                    }
                }
            }
        ))
    
    def register_action(self, action: Action):
        """
        Register a new action in the registry.
        
        Args:
            action: The Action instance to register
            
        Raises:
            ValueError: If an action with the same name already exists
        """
        self.actions[action.name] = action
    
    def get_action(self, name: str) -> Action:
        """
        Retrieve an action by its name.
        
        Args:
            name: The name of the action to retrieve
            
        Returns:
            The requested Action instance
            
        Raises:
            ValueError: If the action is not found
        """
        if name not in self.actions:
            raise ValueError(f"Action {name} not found")
        return self.actions[name]
    
    def list_actions(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered actions in a serializable format.
        
        Returns:
            List of dictionaries containing action information
        """
        return [
            {
                "name": action.name,
                "description": action.description,
                "parameters": action.parameters,
                "required_permissions": action.required_permissions,
                "examples": action.examples,
                "api_spec": action.api_spec
            }
            for action in self.actions.values()
        ]

class Gorilla:
    """
    Main Gorilla Large Action Model implementation.
    This class handles the core functionality of understanding and executing actions.
    """
    
    def __init__(self):
        # Initialize Azure OpenAI client for optional GPT integration
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Initialize Gorilla model components
        self.model_name = "gorilla-llm/gorilla-7b-hf-v1"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Initialize model with empty weights for efficient loading
        with init_empty_weights():
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        
        # Initialize action registry and HTTP session
        self.registry = ActionRegistry()
        self.session = None
    
    async def __aenter__(self):
        """Initialize HTTP session when entering async context"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up HTTP session when exiting async context"""
        if self.session:
            await self.session.close()
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and execute appropriate actions.
        
        Args:
            query: The natural language query from the user
            
        Returns:
            Dictionary containing the model's response and action results
        """
        # Get list of available actions
        actions = self.registry.list_actions()
        
        # Create system prompt following Gorilla's format
        system_prompt = f"""You are Gorilla, a Large Action Model that can understand and execute complex actions.
Available actions:
{json.dumps(actions, indent=2)}

Your task is to:
1. Understand the user's request
2. Identify which action(s) to use
3. Extract parameters for the action(s)
4. Execute the action(s)
5. Return results

Format your response as JSON with the following structure:
{{
    "thought": "Your reasoning about what action to take",
    "action": "Name of the action to execute",
    "parameters": {{"param1": "value1", ...}},
    "observation": "Result of the action",
    "final_answer": "Final response to the user"
}}"""
        
        # Generate response using Gorilla model
        inputs = self.tokenizer(system_prompt + "\nUser: " + query, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=1000,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse and execute the model's response
        try:
            # Extract JSON from response text
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_str)
            
            # Execute the specified action if any
            if result.get("action"):
                action = self.registry.get_action(result["action"])
                observation = await self._execute_action(action, result["parameters"])
                result["observation"] = observation
            
            return result
        except (json.JSONDecodeError, IndexError) as e:
            return {
                "error": "Failed to parse model response",
                "raw_response": response_text
            }
    
    async def _execute_action(self, action: Action, parameters: Dict[str, Any]) -> Any:
        """
        Execute an action with the given parameters.
        
        Args:
            action: The Action instance to execute
            parameters: Dictionary of parameters for the action
            
        Returns:
            The result of the action execution
        """
        try:
            if action.name == "read_file":
                return await self._execute_read_file(parameters)
            elif action.name == "http_request":
                return await self._execute_http_request(parameters)
            else:
                raise ValueError(f"Unknown action: {action.name}")
        except Exception as e:
            return f"Error executing action: {str(e)}"
    
    async def _execute_read_file(self, params: Dict[str, Any]) -> str:
        """
        Execute the read_file action.
        
        Args:
            params: Dictionary containing file_path and optional line numbers
            
        Returns:
            The contents of the file
        """
        file_path = params["file_path"]
        start_line = params.get("start_line")
        end_line = params.get("end_line")
        
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                
            if start_line is not None and end_line is not None:
                lines = lines[start_line-1:end_line]
            
            return "".join(lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    async def _execute_http_request(self, params: Dict[str, Any]) -> str:
        """
        Execute the http_request action.
        
        Args:
            params: Dictionary containing HTTP request parameters
            
        Returns:
            The response from the HTTP request
        """
        method = params["method"]
        url = params["url"]
        headers = params.get("headers", {})
        body = params.get("body")
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=body
            ) as response:
                return await response.text()
        except Exception as e:
            return f"Error making HTTP request: {str(e)}"

# Initialize FastAPI application
app = FastAPI(title="Gorilla LAM API")

# Create global Gorilla instance
gorilla = Gorilla()

@app.post("/chat")
async def chat(request: Dict[str, str]):
    """
    Endpoint to process chat messages.
    
    Args:
        request: Dictionary containing the user's message
        
    Returns:
        The model's response and action results
    """
    async with gorilla as g:
        return await g.process_query(request["message"])

@app.get("/actions")
async def list_actions():
    """
    Endpoint to list all available actions.
    
    Returns:
        List of registered actions
    """
    return gorilla.registry.list_actions()

# Run the application if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 