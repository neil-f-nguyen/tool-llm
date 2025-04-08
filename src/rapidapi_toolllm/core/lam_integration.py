from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import autogen
from autogen import AssistantAgent, UserProxyAgent

load_dotenv()

class LAMIntegration:
    def __init__(self):
        self.azure_api_key = os.getenv("AZURE_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.azure_deployment = os.getenv("AZURE_DEPLOYMENT")
        self.tools: List[Dict[str, Any]] = []
        self.autogen_assistant: Optional[AssistantAgent] = None
        self.autogen_user: Optional[UserProxyAgent] = None

    def register_tool(self, tool_name: str, tool_description: str, tool_function: callable) -> None:
        """Register a new tool with AutoGen"""
        tool = {
            "name": tool_name,
            "func": tool_function,
            "description": tool_description
        }
        self.tools.append(tool)

    def _setup_autogen(self) -> None:
        """Setup AutoGen with Azure GPT"""
        config_list = [{
            'model': 'gpt-4',
            'api_key': self.azure_api_key,
            'base_url': self.azure_endpoint,
            'api_type': 'azure',
            'api_version': '2024-02-15-preview'
        }]

        # Create system message with list of available tools
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tools
        ])
        
        system_message = f"""You are an intelligent AI assistant that can use tools to answer questions.
Here are the available tools:

{tools_description}

When a user asks a question, analyze it and use the most appropriate tool to answer."""

        self.autogen_assistant = AssistantAgent(
            name="assistant",
            llm_config={"config_list": config_list},
            system_message=system_message
        )

        self.autogen_user = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "workspace"}
        )

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query using AutoGen"""
        if not self.autogen_assistant or not self.autogen_user:
            self._setup_autogen()

        try:
            chat_response = await self.autogen_user.initiate_chat(
                self.autogen_assistant,
                message=query
            )
            return {
                "response": chat_response.summary,
                "tool_name": None,
                "parameters": None
            }
        except Exception as e:
            return {
                "error": str(e),
                "tool_name": None,
                "parameters": None
            } 