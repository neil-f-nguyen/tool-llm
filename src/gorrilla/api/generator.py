from typing import List
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class CodeGenerator:
    """Class to generate code using API functions"""
    
    def __init__(self, registry):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.registry = registry
    
    def _create_prompt(self, query: str, relevant_functions: List) -> str:
        """Create prompt for code generation"""
        functions_str = "\n\n".join([
            f"Function: {func.name}\n"
            f"Description: {func.description}\n"
            f"Parameters: {json.dumps(func.parameters, indent=2)}\n"
            f"Returns: {json.dumps(func.returns, indent=2)}\n"
            f"Example:\n{func.example_code}\n"
            f"Documentation: {func.documentation_url}"
            for func in relevant_functions
        ])
        
        return f"""You are an AI coding assistant that helps users write code using the provided API functions.
Given the user's request and the available API functions, generate appropriate code that solves their task.

Available API Functions:
{functions_str}

User's Request: {query}

Please generate code that solves the user's request using the available API functions.
Include necessary imports and provide brief comments explaining the code.
If the request cannot be fulfilled with the available functions, explain why.

Generated Code:"""

    async def generate_code(self, query: str) -> str:
        """Generate code based on user query"""
        # Search for relevant functions
        relevant_functions = self.registry.search_functions(query)
        
        if not relevant_functions:
            return "No relevant API functions found for your request."
        
        # Create prompt
        prompt = self._create_prompt(query, relevant_functions)
        
        try:
            # Generate code using Azure OpenAI
            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant that generates code using provided API functions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating code: {str(e)}" 