from typing import Dict, List, Any
import re
import logging

class ZaraTools:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager

    def generate_post_hooks_with_zara(self, posts: List[str]) -> List[Dict[str, str]]:
        """Generate alternative hooks for each post using Zara."""
        results = []
        
        for post in posts:
            prompt = f"""As Zara, generate two alternative attention-grabbing hooks for this post:

Original Post:
{post}

Return your response as JSON with these keys:
- hook1: first alternative hook
- hook2: second alternative hook

Requirements:
1. Keep the core message but make it more engaging
2. Each hook should use a different approach (question, statistic, bold statement, etc.)
3. Maximum 280 characters per hook
4. Include relevant emojis
"""
            try:
                response = self.agent_manager.generate_response("zara", prompt)
                hooks = json.loads(response)
                results.append({
                    "original": post,
                    "hook1": hooks["hook1"],
                    "hook2": hooks["hook2"]
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

Return your response as JSON with these keys:
- emotion_score: number from 1-10
- has_emoji: boolean
- analysis: detailed explanation of emotional strength
"""
            try:
                response = self.agent_manager.generate_response("eva", prompt)
                analysis = json.loads(response)
                
                if not has_emoji or analysis['emotion_score'] < 6:
                    weak_posts.append({
                        "post": post,
                        "reason": analysis['analysis'],
                        "has_emoji": has_emoji,
                        "emotion_score": analysis['emotion_score']
                    })
            except Exception as e:
                weak_posts.append({
                    "post": post,
                    "reason": f"Error: {str(e)}",
                    "has_emoji": has_emoji,
                    "emotion_score": 0
                })
        
        return weak_posts 