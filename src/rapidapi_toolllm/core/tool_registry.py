from typing import Dict, List, Optional, Any
from src.rapidapi_toolllm.models.tool import Tool, ToolResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self._register_default_tools()

    def _register_default_tools(self):
        # Register Weather API Tool using Open Weather API
        self.register_tool(Tool(
            name="weather",
            description="Get current weather for a location",
            type="api",
            parameters={
                "city": {
                    "type": "string",
                    "description": "City name (e.g., 'hanoi', 'london')",
                    "required": True
                },
                "lang": {
                    "type": "string",
                    "description": "Language code (e.g., 'EN', 'VI')",
                    "required": False,
                    "default": "EN"
                }
            },
            api_endpoint="https://open-weather13.p.rapidapi.com/city/{city}/{lang}",
            api_method="GET",
            api_headers={
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "open-weather13.p.rapidapi.com"
            },
            examples=[
                "What's the weather in Hanoi?",
                "Get weather for Tokyo in Japanese",
                "How's the weather in New York in English?"
            ]
        ))

        # Register News API Tool
        self.register_tool(Tool(
            name="news",
            description="Get latest news articles",
            type="api",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query for news",
                    "required": True
                },
                "language": {
                    "type": "string",
                    "description": "Language code (e.g., 'en', 'vi')",
                    "required": False,
                    "default": "en"
                }
            },
            api_endpoint="https://news-api14.p.rapidapi.com/v2/search/publishers",
            api_method="GET",
            api_headers={
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "news-api14.p.rapidapi.com"
            },
            examples=[
                "Get latest news about Trump tax",
                "Show me news about technology in English",
                "Find news about Vietnam in Vietnamese"
            ]
        ))
        
        # Register Currency Converter Tool
        self.register_tool(Tool(
            name="currency",
            description="Convert between currencies",
            type="api",
            parameters={
                "from": {
                    "type": "string",
                    "description": "Source currency code (e.g., USD)",
                    "required": True
                },
                "to": {
                    "type": "string",
                    "description": "Target currency code (e.g., EUR)",
                    "required": True
                },
                "amount": {
                    "type": "number",
                    "description": "Amount to convert",
                    "required": True
                }
            },
            api_endpoint="https://currency-converter5.p.rapidapi.com/currency/convert",
            api_method="GET",
            api_headers={
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "currency-converter5.p.rapidapi.com"
            },
            examples=[
                "Convert 100 USD to EUR",
                "What is 50 GBP in JPY?"
            ]
        ))
        
        # Register Movie Search Tool
        self.register_tool(Tool(
            name="movie",
            description="Search for movies and get details",
            type="api",
            parameters={
                "title": {
                    "type": "string",
                    "description": "Movie title to search for",
                    "required": True
                }
            },
            api_endpoint="https://ai-movie-recommender.p.rapidapi.com/api/getID",
            api_method="GET",
            api_headers={
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "ai-movie-recommender.p.rapidapi.com"
            },
            examples=[
                "Find information about La La Land",
                "Search for movie The Matrix",
                "Get details about Inception"
            ]
        ))
        
        # Register Recipe Search Tool
        self.register_tool(Tool(
            name="recipe",
            description="Search for recipes",
            type="api",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Recipe to search for",
                    "required": True
                }
            },
            api_endpoint="https://recipe-by-api-ninjas.p.rapidapi.com/v1/recipe",
            api_method="GET",
            api_headers={
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "recipe-by-api-ninjas.p.rapidapi.com"
            },
            examples=[
                "Find a recipe for pasta carbonara",
                "Search for chicken curry recipe"
            ]
        ))

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self.tools.values())

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResponse:
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResponse(
                success=False,
                data=None,
                error=f"Tool {tool_name} not found"
            )

        try:
            if tool.type == "api":
                # Format URL with path parameters if needed
                url = tool.api_endpoint
                if "{" in url and "}" in url:  # Check if URL contains path parameters
                    try:
                        url = url.format(**parameters)
                    except KeyError as e:
                        return ToolResponse(
                            success=False,
                            data=None,
                            error=f"Missing required parameter: {str(e)}"
                        )

                async with httpx.AsyncClient() as client:
                    # If URL doesn't contain path parameters, send as query params
                    if "{" not in url and "}" not in url:
                        response = await client.request(
                            method=tool.api_method,
                            url=url,
                            headers=tool.api_headers,
                            params=parameters
                        )
                    else:
                        response = await client.request(
                            method=tool.api_method,
                            url=url,
                            headers=tool.api_headers
                        )
                    response.raise_for_status()
                    return ToolResponse(
                        success=True,
                        data=response.json()
                    )
            else:
                return ToolResponse(
                    success=False,
                    data=None,
                    error=f"Tool type {tool.type} not supported"
                )
        except Exception as e:
            return ToolResponse(
                success=False,
                data=None,
                error=str(e)
            ) 