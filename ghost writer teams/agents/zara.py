from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import json
from pathlib import Path

class ZaraAgent:
    def __init__(self, api_key):
        # Load Zara's prompt from agent_prompts.json
        prompts_path = Path("prompts/agent_prompts.json")
        with open(prompts_path, "r") as f:
            prompts = json.load(f)
            zara_prompt = prompts["zara"]["system_prompt"]
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        # Define Zara's tools
        tools = [
            Tool(
                name="Creative Strategy",
                func=lambda x: "Creative strategy tool executed",
                description="Use this tool to develop creative campaign strategies and emotional hooks"
            ),
            Tool(
                name="Storytelling",
                func=lambda x: "Storytelling tool executed",
                description="Use this tool to craft compelling narratives and storytelling angles"
            )
        ]
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", zara_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(llm, tools, prompt)
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def run(self, input_text):
        """Run the agent with the given input"""
        try:
            response = self.agent_executor.invoke({"input": input_text})
            return response["output"]
        except Exception as e:
            return f"Error running Zara agent: {str(e)}"
