from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
import re
import logging

class CalendarAgent:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def generate_calendar(self, num_weeks: int, platforms: List[str], theme: str) -> str:
        """Generate a content calendar using the full team of agents."""
        try:
            # Calculate dates for the calendar
            today = datetime.now()
            dates = [(today + timedelta(days=i)).strftime('%B %d, %Y') for i in range(num_weeks * 7)]
            
            # Get initial calendar from Max
            max_prompt = f"""Create a {num_weeks}-week content calendar starting from today ({dates[0]}).
Theme: {theme}
Platforms: {', '.join(platforms)}

Return your response as a JSON list of dictionaries with keys: Date, Platform, Type, Topic, Copy

Rules:
1. Use ONLY the exact dates provided: {', '.join(dates)}
2. Include at least one post per platform per week
3. Mix content types (Thread, Post, Article, Story)
4. Keep copy under 280 characters
5. Return valid JSON format
"""

            calendar_json = self.agent_manager.agents["max"]["executor"].run(max_prompt)
            calendar_data = json.loads(calendar_json)
            
            # Format as markdown table for compatibility
            calendar = """| Date | Platform | Type | Topic | Copy |
|------|----------|------|-------|------|
"""
            for entry in calendar_data:
                calendar += f"| {entry['Date']} | {entry['Platform']} | {entry['Type']} | {entry['Topic']} | {entry['Copy']} |\n"

            # Get Mira's research insights
            mira_prompt = f"""As our Research Analyst, analyze this content calendar and provide strategic insights:

{calendar}

Focus on these key areas and format your response with emojis:

📊 Distribution Strategy:
• How to optimize content distribution
• Best posting times for each platform
• Platform-specific recommendations

📈 Engagement Opportunities:
• Interactive content suggestions
• Community building tactics
• Call-to-action optimization

⏰ Best Posting Times:
• Weekday recommendations
• Time zone considerations
• Platform-specific peak hours

🎯 Audience Insights:
• Target audience behavior patterns
• Content consumption preferences
• Platform-specific audience expectations

🔮 Performance Predictions:
• Expected engagement metrics
• Potential viral content opportunities
• ROI projections

Provide actionable insights for each section using bullet points.
"""
            research = self.agent_manager.agents["mira"]["executor"].run(mira_prompt)
            
            # Get Eva's critique and suggestions
            eva_prompt = f"""As our Critic & Challenger, review this content calendar:

{calendar}

Return your analysis as JSON with these keys:
- quality_scores: dict with keys content_variety, message_clarity, platform_fit, overall_impact (1-10)
- strengths: list of key strengths
- improvements: list of areas for improvement
- suggestions: list of actionable suggestions
"""
            critique_json = self.agent_manager.agents["eva"]["executor"].run(eva_prompt)
            critique_data = json.loads(critique_json)
            
            # Format critique for display
            critique = f"""🎯 Quality Scores:
• Content Variety: {critique_data['quality_scores']['content_variety']}/10
• Message Clarity: {critique_data['quality_scores']['message_clarity']}/10
• Platform Fit: {critique_data['quality_scores']['platform_fit']}/10
• Overall Impact: {critique_data['quality_scores']['overall_impact']}/10

💡 Strengths:
{chr(10).join(['• ' + s for s in critique_data['strengths']])}

⚠️ Areas for Improvement:
{chr(10).join(['• ' + s for s in critique_data['improvements']])}

✨ Enhancement Suggestions:
{chr(10).join(['• ' + s for s in critique_data['suggestions']])}
"""
            
            # Get Leo's brand alignment check
            leo_prompt = f"""As our Brand Guardian, review this calendar for brand consistency:

{calendar}

Provide your analysis in this format:

🎭 Voice Consistency:
• Evaluate tone across platforms
• Note any inconsistencies
• Highlight strong examples

🎯 Brand Message Alignment:
• Check core message presence
• Assess value proposition clarity
• Review key themes

⚡ Impact Analysis:
• Brand perception impact
• Message memorability
• Audience resonance

✅ Recommendations:
• Specific improvements
• Tone adjustments
• Message strengthening
"""
            brand_check = self.agent_manager.agents["leo"]["executor"].run(leo_prompt)
            
            # Format the final output
            final_output = f"""# Content Calendar

## Theme: {theme}
## Platforms: {', '.join(platforms)}
## Duration: {num_weeks} weeks

{calendar}

## 📊 Strategic Insights (Mira)
{research}

## 🔍 Eva's Critique
{critique}

## 🛡️ Leo's Brand Check
{brand_check}
"""
            return final_output
            
        except Exception as e:
            logging.error(f"Error generating calendar: {str(e)}")
            return f"Error generating calendar: {str(e)}"

    def score_calendar_with_eva(self, calendar_text: str) -> Dict[str, int]:
        """Get Eva's scoring of the calendar."""
        prompt = f"""As Eva, score this content calendar on these aspects (1-10):

{calendar_text}

Return your response as JSON with these keys:
- content_variety: score (1-10)
- message_clarity: score (1-10)
- platform_fit: score (1-10)
- overall_impact: score (1-10)
"""
        try:
            response = self.agent_manager.generate_response("eva", prompt)
            return json.loads(response)
        except Exception as e:
            return {"error": str(e)}

    def optimize_ctas_with_eva(self, calendar_text: str) -> Dict[str, Any]:
        """Have Eva analyze and improve CTAs in the content calendar."""
        prompt = f"""As Eva, analyze the CTAs (Calls to Action) in this content calendar and provide specific improvements:

{calendar_text}

Return your response as JSON with these keys:
- analysis: overall assessment of CTA strategy
- weak_ctas: list of posts with weak/vague CTAs
- improvements: list of specific improvements with alternatives
- best_practices: list of 3-5 CTA best practices
"""
        try:
            response = self.agent_manager.generate_response("eva", prompt)
            return json.loads(response)
        except Exception as e:
            return {"error": f"Error analyzing CTAs: {str(e)}"} 