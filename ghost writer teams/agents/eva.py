# Challenger & Critic agent 
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import json
from pathlib import Path

class EvaAgent:
    def __init__(self, api_key):
        # Load Eva's prompt from agent_prompts.json
        prompts_path = Path("prompts/agent_prompts.json")
        with open(prompts_path, "r") as f:
            prompts = json.load(f)
            eva_prompt = prompts["eva"]["system_prompt"]
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        # Define Eva's tools
        tools = [
            Tool(
                name="Content Critique",
                func=lambda x: "Content critique tool executed",
                description="Use this tool to analyze and critique content for weaknesses and areas of improvement"
            ),
            Tool(
                name="Rewrite Suggestion",
                func=lambda x: "Rewrite suggestion tool executed",
                description="Use this tool to suggest specific rewrites and improvements to content"
            ),
            Tool(
                name="Quality Assessment",
                func=lambda x: "Quality assessment tool executed",
                description="Use this tool to evaluate the overall quality and effectiveness of content"
            )
        ]
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", eva_prompt),
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
            return f"Error running Eva agent: {str(e)}" 