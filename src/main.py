from typing import List, Dict, Any, Optional, Callable, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import re
from enum import Enum
import aiohttp
import requests
from bs4 import BeautifulSoup
import wikipedia

# Load environment variables
load_dotenv()

class ToolType(str, Enum):
    FUNCTION = "function"
    API = "api"
    DATABASE = "database"

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None

class Tool(BaseModel):
    name: str
    description: str
    type: ToolType
    parameters: List[ToolParameter]
    function: Optional[Callable] = None
    api_endpoint: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_body_template: Optional[Dict[str, Any]] = None

class ToolRequest(BaseModel):
    tools: List[Tool]
    query: str
    max_steps: Optional[int] = 5

class ToolResponse(BaseModel):
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    final_answer: Optional[str] = None

class ToolRegistry:
    """Class to manage tool registration and execution"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Tool) -> None:
        """Register a new tool"""
        if tool.name in self.tools:
            raise ValueError(f"Tool {tool.name} already exists")
        self.tools[tool.name] = tool
    
    def get_tool(self, tool_name: str) -> Tool:
        """Get a tool by name"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return self.tools[tool_name]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "type": tool.type,
                "parameters": [param.dict() for param in tool.parameters]
            }
            for tool in self.tools.values()
        ]

class SemanticParser:
    """Class to handle semantic parsing of user queries"""
    
    def __init__(self):
        self.patterns = {
            "calculator": r"(calculate|compute|sum|add|subtract|multiply|divide)\s+(\d+)\s*(plus|minus|times|divided by)\s*(\d+)",
            "weather": r"(weather|temperature|forecast)\s+(in|at|for)\s+([a-zA-Z\s,]+)(?:\s+on\s+(\d{4}-\d{2}-\d{2}))?",
            "wikipedia": r"(what is|who is|tell me about|search for)\s+([a-zA-Z\s,]+)",
            "news": r"(news|latest news|recent news)\s+(about|on|regarding)\s+([a-zA-Z\s,]+)",
            "currency": r"(convert|change)\s+(\d+)\s+([A-Z]{3})\s+(to|in)\s+([A-Z]{3})"
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract relevant information"""
        for tool_name, pattern in self.patterns.items():
            match = re.search(pattern, query.lower())
            if match:
                return {
                    "tool": tool_name,
                    "matches": match.groups()
                }
        return None

class ToolExecutor:
    """Class to handle tool execution"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool with given input"""
        tool = self.registry.get_tool(tool_name)
        
        if tool.type == ToolType.FUNCTION:
            return tool.function(**tool_input)
        elif tool.type == ToolType.API:
            return await self._execute_api(tool, tool_input)
        elif tool.type == ToolType.DATABASE:
            return await self._execute_database(tool, tool_input)
        else:
            raise ValueError(f"Unsupported tool type: {tool.type}")
    
    async def _execute_api(self, tool: Tool, tool_input: Dict[str, Any]) -> Any:
        """Execute API-based tool"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            # Prepare request parameters
            headers = tool.api_headers or {}
            params = {}
            body = None
            
            # Handle different API methods
            if tool.api_method == "GET":
                params = tool_input
            else:
                body = tool_input
            
            # Special handling for weather API
            if tool.name == "weather":
                # First, get coordinates for the location
                search_url = f"{tool.api_endpoint}?name={tool_input['location']}&count=1"
                async with self.session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        location_data = await response.json()
                        if location_data.get("results"):
                            location = location_data["results"][0]
                            lat = location["latitude"]
                            lon = location["longitude"]
                            
                            # Then get weather data
                            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
                            async with self.session.get(weather_url) as weather_response:
                                if weather_response.status == 200:
                                    weather_data = await weather_response.json()
                                    return self._format_weather_response(weather_data, location["name"])
            
            # Make the request for other APIs
            async with self.session.request(
                method=tool.api_method,
                url=tool.api_endpoint,
                headers=headers,
                params=params,
                json=body
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_api_response(tool.name, data)
                else:
                    return f"Error: API request failed with status {response.status}"
        except Exception as e:
            return f"Error executing API: {str(e)}"
    
    def _format_weather_response(self, weather_data: Dict[str, Any], location: str) -> str:
        """Format weather API response"""
        daily = weather_data.get("daily", {})
        if not daily:
            return f"Weather data not available for {location}"
        
        dates = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_probability_max", [])
        
        if not dates:
            return f"Weather data not available for {location}"
        
        forecast = []
        for i in range(min(3, len(dates))):
            forecast.append(
                f"{dates[i]}: {temps_min[i]}°C to {temps_max[i]}°C, "
                f"{precip[i]}% chance of precipitation"
            )
        
        return f"Weather forecast for {location}:\n" + "\n".join(forecast)
    
    def _format_api_response(self, tool_name: str, data: Dict[str, Any]) -> str:
        """Format API response based on tool type"""
        if tool_name == "currency":
            amount = data.get("amount", 0)
            from_curr = data.get("base", "")
            to_curr = data.get("rates", {}).keys()
            if to_curr:
                to_curr = list(to_curr)[0]
                rate = data["rates"][to_curr]
                result = amount * rate
                return f"{amount} {from_curr} = {result:.2f} {to_curr}"
        
        elif tool_name == "news":
            articles = data.get("articles", [])
            if not articles:
                return "No news articles found"
            
            formatted_articles = []
            for article in articles[:5]:  # Limit to 5 articles
                formatted_articles.append(
                    f"- {article.get('title', 'No title')}\n"
                    f"  Source: {article.get('source', {}).get('name', 'Unknown')}\n"
                    f"  URL: {article.get('url', 'No URL')}"
                )
            
            return "Latest news:\n" + "\n".join(formatted_articles)
        
        return str(data)  # Default formatting for other APIs

class ToolLLM:
    """Class to handle ToolLLM operations"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.registry = ToolRegistry()
        self.parser = SemanticParser()
        self.executor = ToolExecutor(self.registry)
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        # Register calculator tool
        calculator_tool = Tool(
            name="calculator",
            description="Perform basic mathematical operations",
            type=ToolType.FUNCTION,
            parameters=[
                ToolParameter(
                    name="operation",
                    type="string",
                    description="The operation to perform",
                    enum=["add", "subtract", "multiply", "divide"]
                ),
                ToolParameter(
                    name="num1",
                    type="number",
                    description="First number"
                ),
                ToolParameter(
                    name="num2",
                    type="number",
                    description="Second number"
                )
            ],
            function=self._calculator
        )
        self.registry.register_tool(calculator_tool)
        
        # Register weather tool using Open-Meteo API (free, no API key needed)
        weather_tool = Tool(
            name="weather",
            description="Get weather information for a location",
            type=ToolType.API,
            parameters=[
                ToolParameter(
                    name="location",
                    type="string",
                    description="City name to get weather for"
                ),
                ToolParameter(
                    name="date",
                    type="string",
                    description="Date to get weather for (YYYY-MM-DD)",
                    required=False
                )
            ],
            api_endpoint="https://geocoding-api.open-meteo.com/v1/search",
            api_method="GET",
            api_headers={"Accept": "application/json"}
        )
        self.registry.register_tool(weather_tool)
        
        # Register Wikipedia search tool
        wikipedia_tool = Tool(
            name="wikipedia",
            description="Search for information on Wikipedia",
            type=ToolType.DATABASE,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Topic to search for on Wikipedia"
                )
            ]
        )
        self.registry.register_tool(wikipedia_tool)
        
        # Register news search tool using Gnews API (free tier available)
        news_tool = Tool(
            name="news",
            description="Get latest news about a topic",
            type=ToolType.API,
            parameters=[
                ToolParameter(
                    name="topic",
                    type="string",
                    description="Topic to search news for"
                ),
                ToolParameter(
                    name="count",
                    type="number",
                    description="Number of news articles to return",
                    required=False
                )
            ],
            api_endpoint="https://gnews.io/api/v4/search",
            api_method="GET",
            api_headers={"Accept": "application/json"}
        )
        self.registry.register_tool(news_tool)
        
        # Register currency converter tool using Frankfurter API (free, no API key needed)
        currency_tool = Tool(
            name="currency",
            description="Convert between different currencies",
            type=ToolType.API,
            parameters=[
                ToolParameter(
                    name="amount",
                    type="number",
                    description="Amount to convert"
                ),
                ToolParameter(
                    name="from_currency",
                    type="string",
                    description="Source currency code (e.g., USD, EUR)"
                ),
                ToolParameter(
                    name="to_currency",
                    type="string",
                    description="Target currency code (e.g., USD, EUR)"
                )
            ],
            api_endpoint="https://api.frankfurter.app/latest",
            api_method="GET"
        )
        self.registry.register_tool(currency_tool)
    
    def _calculator(self, operation: str, num1: float, num2: float) -> float:
        """Calculator function implementation"""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
        }
        return operations[operation](num1, num2)
    
    def _create_prompt(self, tools: List[Tool], query: str) -> str:
        """Create prompt with tools description"""
        tools_description = "\n".join([
            f"Tool: {tool.name}\nDescription: {tool.description}\nParameters: {[param.dict() for param in tool.parameters]}"
            for tool in tools
        ])
        
        return f"""You are an AI assistant that can use the following tools:

{tools_description}

User's question: {query}

Please analyze the question and decide which tool to use. Respond in the following format:
Thought: [your reasoning]
Action: [tool name to use]
Action Input: [input for the tool in JSON format]
Observation: [result from the tool]
Thought: [next reasoning]
Final Answer: [final answer]
"""
    
    def _parse_and_execute_tool(self, response_text: str) -> str:
        """Parse response and execute tool if needed"""
        lines = response_text.split('\n')
        action = None
        action_input = None
        
        for line in lines:
            if line.startswith('Action:'):
                action = line.replace('Action:', '').strip()
            elif line.startswith('Action Input:'):
                action_input = line.replace('Action Input:', '').strip()
        
        if action and action_input:
            try:
                tool_input = json.loads(action_input)
                result = self.executor.execute(action, tool_input)
                
                return response_text.replace(
                    'Observation: [result from the tool]',
                    f'Observation: {result}'
                )
            except Exception as e:
                return response_text.replace(
                    'Observation: [result from the tool]',
                    f'Observation: Error executing tool: {str(e)}'
                )
        
        return response_text
    
    async def process_query(self, request: ToolRequest) -> str:
        """Process user query and return response"""
        try:
            # First try semantic parsing
            parsed = self.parser.parse_query(request.query)
            if parsed:
                # If we can parse the query, use the parsed information
                tool_name = parsed["tool"]
                matches = parsed["matches"]
                
                # Create appropriate tool input based on the tool type
                if tool_name == "calculator":
                    operation_map = {
                        "plus": "add",
                        "minus": "subtract",
                        "times": "multiply",
                        "divided by": "divide"
                    }
                    operation = operation_map[matches[2]]
                    tool_input = {
                        "operation": operation,
                        "num1": float(matches[1]),
                        "num2": float(matches[3])
                    }
                elif tool_name == "weather":
                    tool_input = {
                        "location": matches[2],
                        "date": matches[3] if matches[3] else None
                    }
                elif tool_name == "wikipedia":
                    tool_input = {
                        "query": matches[2]
                    }
                elif tool_name == "news":
                    tool_input = {
                        "topic": matches[2],
                        "count": int(matches[3]) if matches[3] else 5
                    }
                elif tool_name == "currency":
                    tool_input = {
                        "amount": float(matches[1]),
                        "from_currency": matches[2],
                        "to_currency": matches[3]
                    }
                
                # Execute the tool directly
                result = await self.executor.execute(tool_name, tool_input)
                return f"Final Answer: {result}"
            
            # If semantic parsing fails, use LLM
            prompt = self._create_prompt(request.tools, request.query)
            
            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "You are an AI assistant capable of using the provided tools. When using a tool, provide the input in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            return self._parse_and_execute_tool(response_text)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Initialize FastAPI app
app = FastAPI(title="ToolLLM POC")
tool_llm = ToolLLM()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat message"""
    # Convert ChatRequest to ToolRequest
    tool_request = ToolRequest(
        query=request.message,
        tools=[],
        max_steps=5
    )
    return await tool_llm.process_query(tool_request)

@app.get("/tools")
async def get_tools():
    return {"tools": tool_llm.registry.list_tools()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 