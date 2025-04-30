from typing import Dict, List, Any
import json
import logging
import re

class MaxTools:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def generate_content(self, topic: str, platform: str, style: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for a specific platform and style."""
        try:
            prompt = f"""As Max, generate content with these specifications:

Topic: {topic}
Platform: {platform}
Style Guidelines:
{json.dumps(style, indent=2)}

Return your response as JSON with these keys:
- headline: main headline/title
- body: main content body
- call_to_action: suggested call to action
- hashtags: list of relevant hashtags
- notes: any additional notes or suggestions
"""
            response = self.agent_manager.generate_response("max", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error generating content: {str(e)}")
            return {"error": str(e)}

    def optimize_for_platform(self, content: str, platform: str) -> Dict[str, Any]:
        """Optimize content for a specific platform."""
        try:
            prompt = f"""As Max, optimize this content for {platform}:

{content}

Return your response as JSON with these keys:
- optimized_content: platform-optimized version
- character_count: character count
- platform_specific_notes: list of platform-specific optimizations
- suggested_media: list of suggested media types
- engagement_tips: list of engagement-boosting tips
"""
            response = self.agent_manager.generate_response("max", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error optimizing content: {str(e)}")
            return {"error": str(e)}

    def generate_content_variations(self, content: str, num_variations: int) -> Dict[str, Any]:
        """Generate multiple variations of content."""
        try:
            prompt = f"""As Max, generate {num_variations} variations of this content:

{content}

Return your response as JSON with these keys:
- variations: list of content variations
- tone_differences: list of tone differences between variations
- best_use_cases: list of best use cases for each variation
- recommendations: list of recommendations for which variation to use
"""
            response = self.agent_manager.generate_response("max", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error generating content variations: {str(e)}")
            return {"error": str(e)}

    def generate_content_series(self, topic: str, num_pieces: int, platform: str) -> Dict[str, Any]:
        """Generate a series of related content pieces."""
        try:
            prompt = f"""As Max, generate a series of {num_pieces} UNIQUE and ENGAGING content pieces.

Topic: {topic}
Platform: {platform}
Required number of pieces: {num_pieces} (IMPORTANT: You must generate exactly this many UNIQUE pieces)

IMPORTANT: Your response MUST be valid JSON with exactly {num_pieces} UNIQUE pieces. Follow these rules:
1. Start with {{ and end with }}
2. Use double quotes for all strings
3. Separate array items with commas
4. Do not include any text before or after the JSON object
5. Do not use line breaks within strings
6. Do not use single quotes
7. Generate EXACTLY {num_pieces} UNIQUE pieces, no more, no less
8. Each piece must have a unique title and content
9. NO placeholder content like "Post X" or "Content for post X"
10. Each piece should build on the overall narrative

Return your response as a JSON object with these exact keys:
{{
    "series_title": "string",
    "pieces": [
        {{
            "title": "string - unique, engaging title",
            "content": "string - unique, engaging content",
            "order": number,
            "connections": ["string - how this connects to other pieces"]
        }}
        ... repeat for all {num_pieces} pieces ...
    ],
    "series_flow": "string - how the pieces build a cohesive narrative",
    "engagement_strategy": ["string - specific strategies for engagement"]
}}

Example response format (but with {num_pieces} pieces):
{{
    "series_title": "AI in Cricket: A Game-Changing Series",
    "pieces": [
        {{
            "title": "How AI is Revolutionizing Cricket Analytics",
            "content": "🎯 Game-changing news! Our AI-powered app is transforming cricket analytics. From predicting player performance to analyzing match strategies, we're bringing data science to the crease! 🏏 #CricketTech #AI",
            "order": 1,
            "connections": ["Introduces the core technology"]
        }},
        {{
            "title": "Real Stories: Teams Using Cricket AI",
            "content": "🌟 Success story alert! The Delhi Capitals boosted their win rate by 23% using our AI insights. See how teams are making smarter decisions with data! 📈 #CricketInnovation #SportsAnalytics",
            "order": 2,
            "connections": ["Shows practical application of the technology"]
        }}
    ],
    "series_flow": "From technology introduction to real-world impact",
    "engagement_strategy": ["Use data points to spark discussion", "Share success stories"]
}}

Remember: Each piece must be unique and valuable. No placeholders or generic content."""

            response = self.agent_manager.generate_response("max", prompt)
            
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Try to parse the response as JSON
            try:
                result = json.loads(response)
                
                # Validate the structure
                if not isinstance(result, dict):
                    raise ValueError("Response is not a JSON object")
                    
                required_keys = ["series_title", "pieces", "series_flow", "engagement_strategy"]
                for key in required_keys:
                    if key not in result:
                        raise ValueError(f"Missing required key: {key}")
                        
                if not isinstance(result["pieces"], list):
                    raise ValueError("'pieces' must be a list")
                
                # Validate each piece has required fields and meaningful content
                seen_titles = set()
                seen_content = set()
                valid_pieces = []
                
                for piece in result["pieces"]:
                    # Check for required fields
                    if not all(k in piece for k in ["title", "content", "order", "connections"]):
                        continue
                        
                    title = piece["title"].strip()
                    content = piece["content"].strip()
                    
                    # Skip if title or content is empty or too generic
                    if not title or not content:
                        continue
                    if "Post" in title and title.replace("Post", "").strip().isdigit():
                        continue
                    if "Content for post" in content:
                        continue
                        
                    # Skip duplicates
                    if title in seen_titles or content in seen_content:
                        continue
                        
                    seen_titles.add(title)
                    seen_content.add(content)
                    valid_pieces.append(piece)
                
                # If we don't have enough valid pieces, generate more
                while len(valid_pieces) < num_pieces:
                    # Generate an additional piece with the same prompt but for one piece
                    single_prompt = f"""As Max, generate ONE unique and engaging content piece about {topic} for {platform}.

Return as JSON:
{{
    "title": "unique, engaging title",
    "content": "unique, engaging content",
    "order": {len(valid_pieces) + 1},
    "connections": ["how this connects to the series"]
}}"""
                    
                    try:
                        additional_response = self.agent_manager.generate_response("max", single_prompt)
                        additional_piece = json.loads(additional_response)
                        
                        title = additional_piece["title"].strip()
                        content = additional_piece["content"].strip()
                        
                        if (title and content and 
                            title not in seen_titles and 
                            content not in seen_content and
                            "Post" not in title and
                            "Content for post" not in content):
                            
                            seen_titles.add(title)
                            seen_content.add(content)
                            valid_pieces.append(additional_piece)
                    except:
                        continue
                
                result["pieces"] = valid_pieces[:num_pieces]
                return result
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {str(e)}")
                logging.error(f"Raw response: {response}")
                
                # Create a fallback response with unique content
                fallback = {
                    "series_title": f"Content Series: {topic}",
                    "pieces": [],
                    "series_flow": "Building knowledge progressively",
                    "engagement_strategy": ["Share valuable insights", "Encourage discussion"]
                }
                
                # Generate unique pieces one at a time
                while len(fallback["pieces"]) < num_pieces:
                    single_prompt = f"""Generate ONE unique and engaging content piece about {topic} for {platform}.
Make it specific and valuable. No generic placeholders."""
                    
                    try:
                        piece_response = self.agent_manager.generate_response("max", single_prompt)
                        
                        # Try to extract title and content
                        title_match = re.search(r"Title:?\s*(.+?)(?:\n|Content:)", piece_response, re.IGNORECASE | re.DOTALL)
                        content_match = re.search(r"Content:?\s*(.+?)(?:\n|$)", piece_response, re.IGNORECASE | re.DOTALL)
                        
                        title = title_match.group(1).strip() if title_match else f"Insight {len(fallback['pieces']) + 1}: {topic}"
                        content = content_match.group(1).strip() if content_match else piece_response.strip()
                        
                        if title and content and "Post" not in title and "Content for post" not in content:
                            fallback["pieces"].append({
                                "title": title,
                                "content": content,
                                "order": len(fallback["pieces"]) + 1,
                                "connections": [f"Part {len(fallback['pieces']) + 1} of the series"]
                            })
                    except:
                        continue
                
                return fallback
                
        except Exception as e:
            logging.error(f"Error generating content series: {str(e)}")
            # Return a minimal valid response with unique content
            return {
                "series_title": f"Content Series: {topic}",
                "pieces": [
                    {
                        "title": f"Understanding {topic} - Part {i+1}",
                        "content": f"Exploring key aspect {i+1} of {topic} and its impact on {platform}",
                        "order": i+1,
                        "connections": [f"Part {i+1} of the educational series"]
                    } for i in range(num_pieces)
                ],
                "series_flow": "Educational series building knowledge progressively",
                "engagement_strategy": ["Share insights", "Encourage discussion"]
            } 