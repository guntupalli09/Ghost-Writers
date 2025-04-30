# Brand Guardian agent 
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import json
from pathlib import Path

class LeoAgent:
    def __init__(self, api_key):
        # Load Leo's prompt from agent_prompts.json
        prompts_path = Path("prompts/agent_prompts.json")
        with open(prompts_path, "r") as f:
            prompts = json.load(f)
            leo_prompt = prompts["leo"]["system_prompt"]
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        # Define Leo's tools
        tools = [
            Tool(
                name="Brand Voice Analysis",
                func=lambda x: "Brand voice analysis tool executed",
                description="Use this tool to analyze and ensure consistency in brand voice and tone"
            ),
            Tool(
                name="Message Alignment",
                func=lambda x: "Message alignment tool executed",
                description="Use this tool to check if content aligns with brand messaging and values"
            ),
            Tool(
                name="Style Guide Check",
                func=lambda x: "Style guide check tool executed",
                description="Use this tool to verify content follows brand style guidelines"
            )
        ]
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", leo_prompt),
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
            return f"Error running Leo agent: {str(e)}" 