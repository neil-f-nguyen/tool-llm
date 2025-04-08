import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

load_dotenv()

class AzureGPTIntegration:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_base = os.getenv("AZURE_OPENAI_API_BASE")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.api_base
        )
        
        # Initialize LangChain components
        self.llm = AzureChatOpenAI(
            azure_deployment=self.deployment_name,
            openai_api_version=self.api_version,
            azure_endpoint=self.api_base,
            api_key=self.api_key,
            temperature=0.7
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.tools = []
        self.agent_executor = None
        
    def register_tool(self, tool_name: str, tool_description: str, tool_function):
        """
        Register a tool for the agent to use
        """
        langchain_tool = Tool(
            name=tool_name,
            description=tool_description,
            func=tool_function
        )
        self.tools.append(langchain_tool)
        
    def setup_agent(self):
        """
        Set up the agent with the registered tools
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that can use tools to answer user questions. "
                      "Use the tools available to you to provide accurate and helpful responses."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
        
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query using Azure GPT
        """
        if not self.agent_executor:
            self.setup_agent()
            
        try:
            response = await self.agent_executor.ainvoke({"input": query})
            return {
                "success": True,
                "response": response["output"],
                "reasoning": "Processed using Azure GPT"
            }
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e),
                "reasoning": "Error processing with Azure GPT"
            }
            
    def direct_completion(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Get a direct completion from Azure GPT without using tools
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}" 