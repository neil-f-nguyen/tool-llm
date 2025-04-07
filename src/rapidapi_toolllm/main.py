from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from src.rapidapi_toolllm.core.tool_registry import ToolRegistry
from src.rapidapi_toolllm.core.semantic_parser import SemanticParser
from src.rapidapi_toolllm.models.tool import Tool, ToolResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="RapidAPI ToolLLM")

# Initialize components
tool_registry = ToolRegistry()
semantic_parser = SemanticParser()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    response: ToolResponse
    reasoning: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and execute appropriate tool
    """
    # Parse the query
    tool_name, parameters = semantic_parser.parse(request.message)
    
    if not tool_name:
        raise HTTPException(
            status_code=400,
            detail="Could not understand the query. Please try rephrasing."
        )

    # Execute the tool
    response = await tool_registry.execute_tool(tool_name, parameters)
    
    return ChatResponse(
        tool_name=tool_name,
        parameters=parameters,
        response=response,
        reasoning=f"Query matched {tool_name} tool with parameters: {parameters}"
    )

@app.get("/tools", response_model=List[Tool])
async def list_tools():
    """
    List all available tools
    """
    return tool_registry.list_tools()

@app.post("/tools", response_model=Tool)
async def register_tool(tool: Tool):
    """
    Register a new tool
    """
    tool_registry.register_tool(tool)
    return tool

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 