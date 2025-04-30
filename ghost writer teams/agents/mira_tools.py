from typing import Dict, List, Any
import json
import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class MiraTools:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.embeddings = OllamaEmbeddings(model="llama2")
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def load_documents(self, documents: List[str]) -> None:
        """Load documents into the vector store for RAG."""
        try:
            # Convert documents to Document objects
            docs = [Document(page_content=doc) for doc in documents]
            
            # Split documents into chunks
            splits = self.text_splitter.split_documents(docs)
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings
                )
            else:
                self.vector_store.add_documents(splits)
                
        except Exception as e:
            logging.error(f"Error loading documents: {str(e)}")
            raise

    def analyze_trends(self, topic: str) -> Dict[str, List[str]]:
        """Analyze trends and opportunities for a given topic."""
        try:
            prompt = f"""As Mira, analyze trends and opportunities for this topic:

{topic}

IMPORTANT: Structure your response as a clear JSON object with these sections:
{{
    "key_trends": [
        "Trend 1 - explain the trend and its relevance",
        "Trend 2 - explain the trend and its relevance",
        "Trend 3 - explain the trend and its relevance"
    ],
    "opportunities": [
        "Opportunity 1 - explain how to leverage it",
        "Opportunity 2 - explain how to leverage it",
        "Opportunity 3 - explain how to leverage it"
    ],
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ]
}}

Make each point detailed and actionable. Do not use placeholder text or generic statements."""

            response = self.agent_manager.generate_response("mira", prompt)
            
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
                # Validate structure
                required_keys = ["key_trends", "opportunities", "recommendations"]
                for key in required_keys:
                    if key not in result or not isinstance(result[key], list):
                        result[key] = []
                return result
            except json.JSONDecodeError:
                # Fallback to text parsing
                result = {
                    "key_trends": [],
                    "opportunities": [],
                    "recommendations": []
                }
                
                current_section = None
                for line in response.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if "key trends" in line.lower():
                        current_section = "key_trends"
                    elif "opportunities" in line.lower():
                        current_section = "opportunities"
                    elif "recommendations" in line.lower():
                        current_section = "recommendations"
                    elif line.startswith("-") or line.startswith("*") and current_section:
                        point = line.lstrip("- *").strip()
                        if point and current_section in result:
                            result[current_section].append(point)
                
                return result
                
        except Exception as e:
            logging.error(f"Error in analyze_trends: {str(e)}")
            return {
                "key_trends": [
                    "Error analyzing trends. Please try again.",
                ],
                "opportunities": [
                    "Error analyzing opportunities. Please try again.",
                ],
                "recommendations": [
                    "Error generating recommendations. Please try again.",
                ]
            }

    def research_competitors(self, competitors: List[str]) -> Dict[str, Any]:
        """Research and analyze competitors."""
        try:
            prompt = f"""As Mira, analyze these competitors:

Competitors: {', '.join(competitors)}

Return your response as JSON with these keys:
- strengths: list of competitor strengths
- weaknesses: list of competitor weaknesses
- opportunities: list of market opportunities
- threats: list of potential threats
- recommendations: list of strategic recommendations
"""
            response = self.agent_manager.generate_response("mira", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error researching competitors: {str(e)}")
            return {"error": str(e)}

    def analyze_audience(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience data and provide insights."""
        try:
            prompt = f"""As Mira, analyze this audience data:

{json.dumps(audience_data, indent=2)}

Return your response as JSON with these keys:
- demographics: key demographic insights
- behaviors: key behavioral patterns
- preferences: content and platform preferences
- pain_points: identified pain points
- recommendations: list of audience-specific recommendations
"""
            response = self.agent_manager.generate_response("mira", prompt)
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Error analyzing audience: {str(e)}")
            return {"error": str(e)} 