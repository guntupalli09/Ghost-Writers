# Research Analyst agent 
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import json
from pathlib import Path

class MiraAgent:
    def __init__(self, api_key):
        # Load Mira's prompt from agent_prompts.json
        prompts_path = Path("prompts/agent_prompts.json")
        with open(prompts_path, "r") as f:
            prompts = json.load(f)
            mira_prompt = prompts["mira"]["system_prompt"]
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        # Define Mira's tools
        tools = [
            Tool(
                name="Data Analysis",
                func=lambda x: "Data analysis tool executed",
                description="Use this tool to analyze content performance metrics and trends"
            ),
            Tool(
                name="Performance Metrics",
                func=lambda x: "Performance metrics tool executed",
                description="Use this tool to calculate and interpret key performance indicators"
            ),
            Tool(
                name="Optimization Recommendations",
                func=lambda x: "Optimization recommendations tool executed",
                description="Use this tool to generate data-driven recommendations for content improvement"
            )
        ]
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", mira_prompt),
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
            return f"Error running Mira agent: {str(e)}" 