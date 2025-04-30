from typing import Dict, List
from langchain.tools import Tool

class AgentTools:
    @staticmethod
    def get_zara_tools() -> List[Tool]:
        """Tools for Zara, the Creative Strategist"""
        return [
            Tool(
                name="campaign_ideas",
                func=lambda x: "Campaign ideas generated",
                description="Generate creative campaign concepts and strategies"
            ),
            Tool(
                name="storytelling_angles",
                func=lambda x: "Storytelling angles generated",
                description="Develop compelling narrative approaches"
            ),
            Tool(
                name="emotional_hooks",
                func=lambda x: "Emotional hooks generated",
                description="Create emotional connection points with the audience"
            )
        ]
    
    @staticmethod
    def get_max_tools() -> List[Tool]:
        """Tools for Max, the Content Architect"""
        return [
            Tool(
                name="content_generation",
                func=lambda x: "Content generated",
                description="Generate various types of content"
            ),
            Tool(
                name="content_optimization",
                func=lambda x: "Content optimized",
                description="Optimize content for different platforms"
            ),
            Tool(
                name="content_structure",
                func=lambda x: "Content structured",
                description="Organize and structure content effectively"
            )
        ]
    
    @staticmethod
    def get_mira_tools() -> List[Tool]:
        """Tools for Mira, the Research Analyst"""
        return [
            Tool(
                name="data_analysis",
                func=lambda x: "Data analyzed",
                description="Analyze trends and data"
            ),
            Tool(
                name="performance_metrics",
                func=lambda x: "Metrics generated",
                description="Generate performance metrics and insights"
            ),
            Tool(
                name="optimization_recommendations",
                func=lambda x: "Recommendations generated",
                description="Provide optimization recommendations"
            )
        ]
    
    @staticmethod
    def get_eva_tools() -> List[Tool]:
        """Tools for Eva, the Challenger & Critic"""
        return [
            Tool(
                name="content_critique",
                func=lambda x: "Content critiqued",
                description="Critique and analyze content"
            ),
            Tool(
                name="content_rewrite",
                func=lambda x: "Content rewritten",
                description="Rewrite and improve content"
            ),
            Tool(
                name="tone_adjustment",
                func=lambda x: "Tone adjusted",
                description="Adjust content tone and style"
            )
        ]
    
    @staticmethod
    def get_leo_tools() -> List[Tool]:
        """Tools for Leo, the Brand Guardian"""
        return [
            Tool(
                name="brand_voice_check",
                func=lambda x: "Voice checked",
                description="Check brand voice consistency"
            ),
            Tool(
                name="tone_analysis",
                func=lambda x: "Tone analyzed",
                description="Analyze and adjust tone"
            ),
            Tool(
                name="message_alignment",
                func=lambda x: "Message aligned",
                description="Ensure message alignment"
            )
        ]
    
    @staticmethod
    def get_tools_for_agent(agent_name: str) -> List[Tool]:
        """Get tools for a specific agent"""
        tool_getters = {
            "zara": AgentTools.get_zara_tools,
            "max": AgentTools.get_max_tools,
            "mira": AgentTools.get_mira_tools,
            "eva": AgentTools.get_eva_tools,
            "leo": AgentTools.get_leo_tools
        }
        
        if agent_name in tool_getters:
            return tool_getters[agent_name]()
        return [] 