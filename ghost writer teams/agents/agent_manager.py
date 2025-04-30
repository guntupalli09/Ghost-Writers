from typing import Dict, List, Optional, Tuple, Any
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.globals import set_verbose, get_verbose
import json
import re
from pathlib import Path
import asyncio
from tools.agent_tools import AgentTools
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from agents.mira_tools import MiraTools
from agents.leo_tools import LeoTools
from agents.max_tools import MaxTools

class AgentManager:
    def __init__(self):
        self.agents = {}
        self.language = "English"
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.initialize_agents()
        self.initialize_tools()

    def initialize_tools(self):
        """Initialize specialized agent tools."""
        self.mira_tools = MiraTools(self)
        self.leo_tools = LeoTools(self)
        self.max_tools = MaxTools(self)

    def set_language(self, language: str) -> None:
        """Set the language for agent responses."""
        self.language = language

    def _get_language_instruction(self) -> str:
        """Get the language instruction prefix based on current language setting."""
        if self.language == "English":
            return ""
        return f"""Please respond in {self.language}. 
Keep any code, technical terms, brand names, and URLs in English, but translate all other content.

"""

    def initialize_agents(self):
        """Initialize all agents with their respective tools and memory."""
        try:
            with open("prompts/agent_prompts.json", "r") as f:
                prompts = json.load(f)

            # Get model name from environment or use default
            import os
            model_name = os.getenv("LLM_MODEL", "llama2")

            llm = ChatOllama(model=model_name, temperature=0.7)

            # Set verbose mode for debugging
            set_verbose(True)

            for agent_name, config in prompts.items():
                try:
                    tools = AgentTools.get_tools_for_agent(agent_name)
                    memory = ConversationBufferMemory(return_messages=True)

                    # Add default brand voice to memory
                    memory.chat_memory.add_user_message("Our brand voice is confident, clear, and witty.")

                    prompt = ChatPromptTemplate.from_messages([
                        ("system", config["prompt"]),
                        ("human", "{input}"),
                        MessagesPlaceholder(variable_name="agent_scratchpad"),
                    ])

                    agent = OpenAIFunctionsAgent(
                        llm=llm,
                        tools=tools,
                        prompt=prompt,
                        memory=memory
                    )

                    executor = AgentExecutor(
                        agent=agent,
                        tools=tools,
                        verbose=get_verbose(),
                        handle_parsing_errors=True
                    )

                    self.agents[agent_name] = {
                        "executor": executor,
                        "memory": memory,
                        "config": config
                    }
                except Exception as e:
                    logging.error(f"Error initializing agent {agent_name}: {str(e)}")

        except Exception as e:
            logging.error(f"Error in initialize_agents: {str(e)}")
            raise

    def generate_response(self, agent_name: str, user_input: str) -> str:
        """Generate a response from a specific agent."""
        if agent_name not in self.agents:
            return f"Error: Agent {agent_name} not found"

        try:
            # Add language instruction if needed
            prompt = self._get_language_instruction() + user_input
            
            # Get agent executor
            executor = self.agents[agent_name]["executor"]
            
            # Generate response
            response = executor.run(prompt)
            return response
        except Exception as e:
            logging.error(f"Error generating response for {agent_name}: {str(e)}")
            return f"Error: {str(e)}"

    def rewrite_with_eva(self, user_input: str) -> Dict[str, str]:
        if "eva" not in self.agents:
            return {"error": "Eva agent not found"}

        prompt = f"""As Eva, the sharp critic and challenger, analyze and improve this content.

Content to review:
{user_input}

Provide your response in this exact format:

Critique:
[Your detailed critique of the content, highlighting strengths and areas for improvement]

Version 1:
[First improved version that addresses the issues while maintaining the core message]

Version 2:
[Alternative version with a different approach or tone]
"""
        try:
            output = self.agents["eva"]["executor"].run(prompt)
            result = {
                "critique": re.search(r"Critique:\s*(.*?)\s*Version 1:", output, re.DOTALL),
                "version_1": re.search(r"Version 1:\s*(.*?)\s*Version 2:", output, re.DOTALL),
                "version_2": re.search(r"Version 2:\s*(.*)", output, re.DOTALL)
            }

            return {
                "critique": result["critique"].group(1).strip() if result["critique"] else "",
                "version_1": result["version_1"].group(1).strip() if result["version_1"] else "",
                "version_2": result["version_2"].group(1).strip() if result["version_2"] else ""
            }
        except Exception as e:
            return {"error": f"Error: {str(e)}"}

    def generate_calendar(self, num_weeks: int, platforms: List[str], theme: str) -> str:
        """Generate a content calendar using the full team of agents."""
        try:
            # Validate inputs
            if not platforms:
                raise ValueError("At least one platform must be specified")
            if num_weeks < 1:
                raise ValueError("Number of weeks must be at least 1")
            if not theme.strip():
                raise ValueError("Theme cannot be empty")

            # Calculate dates for the calendar
            today = datetime.now()
            dates = [(today + timedelta(days=i)).strftime('%B %d, %Y') for i in range(num_weeks * 7)]
            
            # Get initial calendar from Max using the new tools
            try:
                calendar_data = self.max_tools.generate_content_series(
                    topic=theme,
                    num_pieces=num_weeks * len(platforms),
                    platform=platforms[0]  # Use first platform as base
                )
                
                if not calendar_data:
                    raise ValueError("No calendar data received from Max")
                    
                # Handle both string and dict responses
                if isinstance(calendar_data, str):
                    try:
                        # Try to clean the response before parsing
                        cleaned_response = calendar_data.strip()
                        if cleaned_response.startswith("```json"):
                            cleaned_response = cleaned_response[7:]
                        if cleaned_response.endswith("```"):
                            cleaned_response = cleaned_response[:-3]
                        cleaned_response = cleaned_response.strip()
                        
                        # Try to find the JSON object
                        start = cleaned_response.find('{')
                        end = cleaned_response.rfind('}') + 1
                        if start >= 0 and end > start:
                            cleaned_response = cleaned_response[start:end]
                            
                        calendar_data = json.loads(cleaned_response)
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON parsing error: {str(e)}")
                        logging.error(f"Raw response: {calendar_data}")
                        raise ValueError("Invalid JSON response from Max")
                
                if "error" in calendar_data:
                    raise ValueError(calendar_data.get("error", "Failed to generate calendar data"))
                
                if "pieces" not in calendar_data or not calendar_data["pieces"]:
                    raise ValueError("No content pieces were generated")
                    
            except Exception as e:
                logging.error(f"Error in content generation: {str(e)}")
                raise ValueError(f"Failed to generate content: {str(e)}")
            
            # Format calendar data into markdown table
            calendar = """| Date | Platform | Type | Topic | Copy |
|------|----------|------|-------|------|
"""
            total_pieces = len(calendar_data["pieces"])
            total_dates = len(dates)
            total_platforms = len(platforms)
            
            if total_pieces == 0 or total_dates == 0 or total_platforms == 0:
                raise ValueError("Invalid data: missing pieces, dates, or platforms")
            
            # Calculate the number of pieces to generate
            num_pieces = min(total_pieces, total_dates)
            
            for i in range(num_pieces):
                try:
                    date = dates[i]
                    platform = platforms[i % total_platforms]
                    piece = calendar_data["pieces"][i]
                    
                    if not piece or not isinstance(piece, dict):
                        continue
                        
                    title = piece.get("title", "").strip()
                    content = piece.get("content", "").strip()
                    
                    if not title or not content:
                        continue
                        
                    calendar += f"| {date} | {platform} | Post | {title} | {content} |\n"
                except Exception as e:
                    logging.warning(f"Error processing piece {i}: {str(e)}")
                    continue
            
            if calendar.count("\n") <= 2:  # Only header rows
                raise ValueError("No valid content pieces were generated")
            
            # Get Mira's research insights using new tools
            research = self.mira_tools.analyze_trends(theme)
            research_text = "## 📊 Strategic Insights\n\n"
            if "error" not in research:
                research_text += "Key Trends:\n" + "\n".join(f"- {trend}" for trend in research.get("key_trends", []))
                research_text += "\n\nOpportunities:\n" + "\n".join(f"- {opp}" for opp in research.get("opportunities", []))
                research_text += "\n\nRecommendations:\n" + "\n".join(f"- {rec}" for rec in research.get("recommendations", []))
            else:
                research_text += "Error getting research insights."
            
            # Get Eva's critique
            critique = self.score_calendar_with_eva(calendar)
            critique_text = "## 🔍 Eva's Critique\n\n"
            if isinstance(critique, dict) and "error" not in critique:
                critique_text += f"Content Variety: {critique.get('Content Variety', 'N/A')}/10\n"
                critique_text += f"Message Clarity: {critique.get('Message Clarity', 'N/A')}/10\n"
                critique_text += f"Platform Fit: {critique.get('Platform Fit', 'N/A')}/10\n"
                critique_text += f"Overall Impact: {critique.get('Overall Impact', 'N/A')}/10\n"
            else:
                critique_text += "Error getting critique."
            
            # Get Leo's brand alignment check
            brand_check = self.brand_check_with_leo(calendar)
            brand_text = "## 🛡️ Leo's Brand Check\n\n"
            if isinstance(brand_check, dict) and "error" not in brand_check:
                brand_text += f"Voice Consistency: {brand_check.get('Voice Consistency', 'N/A')}/10\n"
                brand_text += f"Brand Alignment: {brand_check.get('Brand Alignment', 'N/A')}/10\n"
                brand_text += f"Value Proposition: {brand_check.get('Value Proposition', 'N/A')}/10\n"
                brand_text += f"Professional Tone: {brand_check.get('Professional Tone', 'N/A')}/10\n"
                brand_text += "\nAnalysis:\n" + brand_check.get("Analysis", "No analysis available")
                brand_text += "\n\nRecommendations:\n" + "\n".join(f"- {rec}" for rec in brand_check.get("Recommendations", []))
            else:
                brand_text += "Error getting brand check."
            
            # Format the final output
            final_output = f"""# Content Calendar

## Theme: {theme}
## Platforms: {', '.join(platforms)}
## Duration: {num_weeks} weeks

{calendar}

{research_text}

{critique_text}

{brand_text}
"""
            return final_output
            
        except Exception as e:
            logging.error(f"Error generating calendar: {str(e)}")
            return f"Error generating calendar: {str(e)}"

    def score_calendar_with_eva(self, calendar_text: str) -> Dict[str, Any]:
        """Get Eva's scoring and analysis of the calendar."""
        try:
            prompt = f"""As Eva, provide a detailed critique of this content calendar:

{calendar_text}

IMPORTANT: Structure your response as a JSON object with these sections:
{{
    "scores": {{
        "Content Variety": <score 1-10>,
        "Message Clarity": <score 1-10>,
        "Platform Fit": <score 1-10>,
        "Overall Impact": <score 1-10>
    }},
    "analysis": {{
        "Content Variety": "Detailed analysis of content variety and suggestions for improvement",
        "Message Clarity": "Analysis of message clarity and how to enhance it",
        "Platform Fit": "Evaluation of platform-specific optimization",
        "Overall Impact": "Assessment of overall effectiveness and engagement potential"
    }},
    "strengths": [
        "Key strength 1 with specific example",
        "Key strength 2 with specific example"
    ],
    "improvements": [
        "Specific improvement suggestion 1",
        "Specific improvement suggestion 2"
    ]
}}

Provide specific examples and actionable suggestions in your analysis."""

            response = self.generate_response("eva", prompt)
            
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Try to find JSON object
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                response = response[start:end]
            
            try:
                result = json.loads(response)
                # Validate scores are between 1 and 10
                if "scores" in result:
                    for key, value in result["scores"].items():
                        if not isinstance(value, (int, float)) or value < 1 or value > 10:
                            result["scores"][key] = 5  # Default to middle score if invalid
                else:
                    result["scores"] = {
                        "Content Variety": 5,
                        "Message Clarity": 5,
                        "Platform Fit": 5,
                        "Overall Impact": 5
                    }
                
                # Ensure all sections exist
                if "analysis" not in result:
                    result["analysis"] = {
                        "Content Variety": "Analysis not available",
                        "Message Clarity": "Analysis not available",
                        "Platform Fit": "Analysis not available",
                        "Overall Impact": "Analysis not available"
                    }
                if "strengths" not in result:
                    result["strengths"] = ["No strengths identified"]
                if "improvements" not in result:
                    result["improvements"] = ["No improvements suggested"]
                
                return result
                
            except json.JSONDecodeError:
                logging.warning("Failed to parse JSON response, falling back to text parsing")
                # Fallback to text parsing
                result = {
                    "scores": {
                        "Content Variety": 5,
                        "Message Clarity": 5,
                        "Platform Fit": 5,
                        "Overall Impact": 5
                    },
                    "analysis": {},
                    "strengths": [],
                    "improvements": []
                }
                
                current_section = None
                current_aspect = None
                
                for line in response.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try to extract scores
                    if ':' in line:
                        aspect, score_text = line.split(':', 1)
                        aspect = aspect.strip().strip('"')
                        if aspect in result["scores"]:
                            try:
                                score_match = re.search(r'\d+', score_text)
                                if score_match:
                                    score = int(score_match.group())
                                    if 1 <= score <= 10:
                                        result["scores"][aspect] = score
                                        current_aspect = aspect
                            except (ValueError, AttributeError):
                                continue
                    
                    # Try to extract analysis sections
                    if "strengths" in line.lower():
                        current_section = "strengths"
                    elif "improvements" in line.lower() or "weaknesses" in line.lower():
                        current_section = "improvements"
                    elif line.startswith("-") or line.startswith("*"):
                        point = line.lstrip("- *").strip()
                        if current_section and point:
                            result[current_section].append(point)
                        elif current_aspect:
                            result["analysis"][current_aspect] = point
                
                return result
                
        except Exception as e:
            logging.error(f"Error in score_calendar_with_eva: {str(e)}")
            return {
                "scores": {
                    "Content Variety": 5,
                    "Message Clarity": 5,
                    "Platform Fit": 5,
                    "Overall Impact": 5
                },
                "analysis": {
                    "Content Variety": "Error analyzing content variety",
                    "Message Clarity": "Error analyzing message clarity",
                    "Platform Fit": "Error analyzing platform fit",
                    "Overall Impact": "Error analyzing overall impact"
                },
                "strengths": ["Error identifying strengths"],
                "improvements": ["Error identifying improvements"]
            }

    def brand_check_with_leo(self, calendar_text: str) -> Dict[str, Any]:
        """Get Leo's brand alignment check."""
        try:
            prompt = f"""As Leo, provide a comprehensive brand alignment analysis for this content calendar:

{calendar_text}

IMPORTANT: Structure your response as a JSON object with these sections:
{{
    "scores": {{
        "Voice Consistency": <score 1-10>,
        "Brand Alignment": <score 1-10>,
        "Value Proposition": <score 1-10>,
        "Professional Tone": <score 1-10>
    }},
    "analysis": "Detailed analysis of overall brand alignment, including specific examples",
    "tone_review": {{
        "strengths": [
            "Specific example of strong brand voice usage",
            "Another example of effective tone"
        ],
        "concerns": [
            "Specific example where tone needs adjustment",
            "Another area for tone improvement"
        ]
    }},
    "recommendations": [
        "Actionable recommendation with specific example",
        "Another specific improvement suggestion"
    ]
}}

Focus on concrete examples and actionable feedback. Identify both strong points and areas for improvement."""

            response = self.generate_response("leo", prompt)
            
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Try to find JSON object
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                response = response[start:end]
            
            try:
                result = json.loads(response)
                # Validate scores are between 1 and 10
                if "scores" in result:
                    for key, value in result["scores"].items():
                        if not isinstance(value, (int, float)) or value < 1 or value > 10:
                            result["scores"][key] = 5  # Default to middle score if invalid
                else:
                    result["scores"] = {
                        "Voice Consistency": 5,
                        "Brand Alignment": 5,
                        "Value Proposition": 5,
                        "Professional Tone": 5
                    }
                
                # Ensure all sections exist
                if "analysis" not in result:
                    result["analysis"] = "Analysis not available"
                if "tone_review" not in result:
                    result["tone_review"] = {
                        "strengths": ["No strengths identified"],
                        "concerns": ["No concerns identified"]
                    }
                if "recommendations" not in result:
                    result["recommendations"] = ["No recommendations provided"]
                
                return result
                
            except json.JSONDecodeError:
                logging.warning("Failed to parse JSON response, falling back to text parsing")
                # Fallback to text parsing
                result = {
                    "scores": {
                        "Voice Consistency": 5,
                        "Brand Alignment": 5,
                        "Value Proposition": 5,
                        "Professional Tone": 5
                    },
                    "analysis": "",
                    "tone_review": {
                        "strengths": [],
                        "concerns": []
                    },
                    "recommendations": []
                }
                
                current_section = None
                analysis_text = []
                
                for line in response.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try to extract scores
                    if ':' in line:
                        aspect, score_text = line.split(':', 1)
                        aspect = aspect.strip().strip('"')
                        if aspect in result["scores"]:
                            try:
                                score_match = re.search(r'\d+', score_text)
                                if score_match:
                                    score = int(score_match.group())
                                    if 1 <= score <= 10:
                                        result["scores"][aspect] = score
                            except (ValueError, AttributeError):
                                continue
                    
                    # Try to extract sections
                    if "analysis" in line.lower():
                        current_section = "analysis"
                    elif "strengths" in line.lower():
                        current_section = "strengths"
                    elif "concerns" in line.lower() or "weaknesses" in line.lower():
                        current_section = "concerns"
                    elif "recommendations" in line.lower():
                        current_section = "recommendations"
                    elif line.startswith("-") or line.startswith("*"):
                        point = line.lstrip("- *").strip()
                        if current_section == "analysis":
                            analysis_text.append(point)
                        elif current_section == "strengths":
                            result["tone_review"]["strengths"].append(point)
                        elif current_section == "concerns":
                            result["tone_review"]["concerns"].append(point)
                        elif current_section == "recommendations":
                            result["recommendations"].append(point)
                
                if analysis_text:
                    result["analysis"] = " ".join(analysis_text)
                
                return result
                
        except Exception as e:
            logging.error(f"Error in brand_check_with_leo: {str(e)}")
            return {
                "scores": {
                    "Voice Consistency": 5,
                    "Brand Alignment": 5,
                    "Value Proposition": 5,
                    "Professional Tone": 5
                },
                "analysis": "Error performing brand analysis",
                "tone_review": {
                    "strengths": ["Error identifying strengths"],
                    "concerns": ["Error identifying concerns"]
                },
                "recommendations": ["Error generating recommendations"]
            }

    def clear_chat_history(self):
        for agent in self.agents.values():
            if hasattr(agent["executor"], "memory"):
                agent["executor"].memory.clear()

    async def generate_responses_async(self, agent_names: List[str], user_input: str, shared_context: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Generate responses from multiple agents asynchronously with shared context."""
        async def _generate_response(agent_name: str) -> Tuple[str, str]:
            try:
                # Build prompt with shared context if available
                prompt = self._get_language_instruction()
                if shared_context and agent_name in shared_context:
                    prompt += f"""Context from other agents:
{shared_context[agent_name]}

Your task:
{user_input}"""
                else:
                    prompt += user_input
                
                # Run in thread pool since LangChain calls are blocking
                response = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.generate_response,
                    agent_name,
                    prompt
                )
                return agent_name, response
            except Exception as e:
                logging.error(f"Error in async response generation for {agent_name}: {str(e)}")
                return agent_name, f"Error: {str(e)}"

        tasks = [_generate_response(agent) for agent in agent_names]
        results = await asyncio.gather(*tasks)
        return dict(results)

    def optimize_ctas_with_eva(self, calendar_text: str) -> Dict[str, str]:
        """Get Eva's optimization of CTAs in the calendar."""
        try:
            prompt = f"""As Eva, analyze and optimize the CTAs in this content calendar:

{calendar_text}

Return your response as a JSON object with these exact keys:
{{
    "Analysis": "Overall analysis of CTA effectiveness",
    "Weak CTAs": ["List of weak CTAs that need improvement"],
    "Improvements": ["List of suggested improvements"],
    "Best Practices": "Summary of CTA best practices to follow"
}}
"""
            response = self.generate_response("eva", prompt)
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to old parsing method for backward compatibility
                sections = response.split('\n\n')
                result = {
                    "Analysis": sections[0] if len(sections) > 0 else "",
                    "Weak CTAs": sections[1].split('\n')[1:] if len(sections) > 1 else [],
                    "Improvements": sections[2].split('\n')[1:] if len(sections) > 2 else [],
                    "Best Practices": sections[3] if len(sections) > 3 else ""
                }
                return result
        except Exception as e:
            return {"error": str(e)}

    def generate_post_hooks_with_zara(self, posts: List[str]) -> List[Dict[str, str]]:
        """Generate alternative hooks for each post using Zara."""
        results = []
        
        for post in posts:
            prompt = f"""As Zara, generate two alternative attention-grabbing hooks for this post:

Original Post:
{post}

Requirements:
1. Keep the core message but make it more engaging
2. Each hook should use a different approach (question, statistic, bold statement, etc.)
3. Maximum 280 characters per hook
4. Include relevant emojis

Provide exactly two alternatives in this format:
Hook 1: [First hook]
Hook 2: [Second hook]
"""
            try:
                response = self.generate_response("zara", prompt)
                hooks = {
                    "hook1": re.search(r"Hook 1:(.*?)Hook 2:", response, re.DOTALL),
                    "hook2": re.search(r"Hook 2:(.*)", response, re.DOTALL)
                }
                
                results.append({
                    "original": post,
                    "hook1": hooks["hook1"].group(1).strip() if hooks["hook1"] else "",
                    "hook2": hooks["hook2"].group(1).strip() if hooks["hook2"] else ""
                })
            except Exception as e:
                results.append({
                    "original": post,
                    "hook1": f"Error: {str(e)}",
                    "hook2": f"Error: {str(e)}"
                })
        
        return results

    def detect_weak_emotion(self, posts: List[str]) -> List[str]:
        """Detect posts that lack emotional engagement or emojis."""
        weak_posts = []
        
        for post in posts:
            # Check for emoji presence
            has_emoji = bool(re.search(r'[\U0001F300-\U0001F9FF]', post))
            
            prompt = f"""As Eva, analyze this post for emotional engagement:

{post}

Consider:
1. Presence of emojis
2. Emotional language
3. Personal connection
4. Engagement triggers

Rate emotional strength (1-10) and explain why.
"""
            try:
                response = self.generate_response("eva", prompt)
                score_match = re.search(r'(\d+)/10', response)
                score = int(score_match.group(1)) if score_match else 0
                
                if not has_emoji or score < 6:
                    weak_posts.append({
                        "post": post,
                        "reason": response,
                        "has_emoji": has_emoji,
                        "emotion_score": score
                    })
            except Exception as e:
                weak_posts.append({
                    "post": post,
                    "reason": f"Error: {str(e)}",
                    "has_emoji": has_emoji,
                    "emotion_score": 0
                })
        
        return weak_posts

    def summarize_agent_memory(self, agent_name: str) -> str:
        """Get a summary of the agent's recent memory."""
        if agent_name not in self.agents:
            return "Agent not found"
            
        try:
            memory = self.agents[agent_name]["memory"]
            if not memory.chat_memory.messages:
                return "No memory yet"
            
            # Get the last few messages
            recent_messages = memory.chat_memory.messages[-5:]
            
            # Format them into a summary
            summary = []
            for msg in recent_messages:
                if isinstance(msg, HumanMessage):
                    summary.append(f"👤 Asked about: {msg.content[:100]}...")
                elif isinstance(msg, AIMessage):
                    summary.append(f"🤖 Responded about: {msg.content[:100]}...")
            
            return "\n".join(summary)
        except Exception as e:
            logging.error(f"Error summarizing memory for {agent_name}: {str(e)}")
            return f"Error accessing memory: {str(e)}"

    def clear_all_memory(self) -> bool:
        """Clear memory and chat history for all agents."""
        try:
            # Clear agent memories
            for agent_data in self.agents.values():
                if "memory" in agent_data:
                    agent_data["memory"].clear()
            
            return True
        except Exception as e:
            logging.error(f"Error clearing memory: {str(e)}")
            return False

    def __del__(self):
        """Cleanup thread pool on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

