from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ToolType(str, Enum):
    FUNCTION = "function"
    API = "api"
    DATABASE = "database"

class ToolParameter(BaseModel):
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class Tool(BaseModel):
    name: str
    description: str
    type: str  # Changed from ToolType to str for simplicity
    parameters: Dict[str, Any]
    api_endpoint: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    examples: List[str] = []

class ToolResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    reasoning: Optional[str] = None 