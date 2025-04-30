from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import json
from pathlib import Path

class MaxAgent:
    def __init__(self, api_key):
        # Load Max's prompt from agent_prompts.json
        prompts_path = Path("prompts/agent_prompts.json")
        with open(prompts_path, "r") as f:
            prompts = json.load(f)
            max_prompt = prompts["max"]["system_prompt"]
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        # Define Max's tools
        tools = [
            Tool(
                name="Content Generation",
                func=lambda x: "Content generation tool executed",
                description="Use this tool to generate various types of content (blogs, tweets, emails, etc.)"
            ),
            Tool(
                name="Content Optimization",
                func=lambda x: "Content optimization tool executed",
                description="Use this tool to optimize content for different platforms and formats"
            ),
            Tool(
                name="Content Structure",
                func=lambda x: "Content structure tool executed",
                description="Use this tool to organize and structure content effectively"
            )
        ]
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", max_prompt),
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
            return f"Error running Max agent: {str(e)}"
