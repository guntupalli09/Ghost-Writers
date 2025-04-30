from typing import Dict, List, Any
import json
import logging

class LeoTools:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def analyze_brand_voice(self, content: str) -> Dict[str, Any]:
        """Analyze content for brand voice consistency."""
        try:
            prompt = f"""As Leo, analyze this content for brand voice consistency:

{content}

Return your response as JSON with these keys:
- tone_consistency: score from 1-10
- brand_alignment: score from 1-10
- voice_characteristics: list of identified voice traits
- inconsistencies: list of any voice inconsistencies
- recommendations: list of improvement suggestions
"""
            response = self.agent_manager.generate_response("leo", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error analyzing brand voice: {str(e)}")
            return {"error": str(e)}

    def check_message_alignment(self, messages: List[str]) -> Dict[str, Any]:
        """Check alignment of multiple messages with brand guidelines."""
        try:
            prompt = f"""As Leo, analyze these messages for brand alignment:

Messages:
{json.dumps(messages, indent=2)}

Return your response as JSON with these keys:
- overall_alignment: score from 1-10
- core_message_consistency: score from 1-10
- value_proposition_clarity: score from 1-10
- key_themes: list of identified themes
- misalignments: list of any message misalignments
- recommendations: list of improvement suggestions
"""
            response = self.agent_manager.generate_response("leo", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error checking message alignment: {str(e)}")
            return {"error": str(e)}

    def review_brand_guidelines(self, guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Review and validate brand guidelines."""
        try:
            prompt = f"""As Leo, review these brand guidelines:

{json.dumps(guidelines, indent=2)}

Return your response as JSON with these keys:
- completeness: score from 1-10
- clarity: score from 1-10
- consistency: score from 1-10
- strengths: list of guideline strengths
- gaps: list of identified gaps
- recommendations: list of improvement suggestions
"""
            response = self.agent_manager.generate_response("leo", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error reviewing brand guidelines: {str(e)}")
            return {"error": str(e)}

    def analyze_platform_consistency(self, content_by_platform: Dict[str, str]) -> Dict[str, Any]:
        """Analyze content consistency across different platforms."""
        try:
            prompt = f"""As Leo, analyze content consistency across platforms:

{json.dumps(content_by_platform, indent=2)}

Return your response as JSON with these keys:
- platform_consistency: score from 1-10
- tone_adaptation: score from 1-10
- message_consistency: score from 1-10
- platform_specific_issues: list of platform-specific issues
- recommendations: list of improvement suggestions
"""
            response = self.agent_manager.generate_response("leo", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error analyzing platform consistency: {str(e)}")
            return {"error": str(e)} 