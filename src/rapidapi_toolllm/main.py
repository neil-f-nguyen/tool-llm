from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
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
    use_lam: bool = False  # Flag to use LAM-based processing
    use_autogen: bool = False  # Flag to use AutoGen instead of LangChain

class ChatResponse(BaseModel):
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    response: Any
    reasoning: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and execute appropriate tool
    """
    if request.use_lam:
        # Use LAM for processing
        result = await tool_registry.process_with_lam(request.message, request.use_autogen)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing with LAM: {result.get('error', 'Unknown error')}"
            )
            
        return ChatResponse(
            tool_name=None,  # Multiple tools might be used
            parameters=None,  # Parameters are handled by LAM
            response=result["response"],
            reasoning=result["reasoning"]
        )
    else:
        # Use traditional regex-based parsing
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

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 