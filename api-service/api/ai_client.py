"""
AI Client for OpenAI Integration
Handles all AI-related operations including job analysis, resume suggestions, and cover letter generation.
"""

import os
import json
from openai import OpenAI
from typing import Dict, Any, Optional


class AIClient:
    """Wrapper class for OpenAI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        # Try OPENAI_API_KEY first, fallback to AI_API_KEY for backwards compatibility
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('AI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY or AI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        # Use gpt-4o-mini for faster, cost-effective analysis
        # Alternative models: "gpt-4o-mini", "gpt-4-turbo", "gpt-4"
        self.default_model = os.getenv('AI_MODEL', 'gpt-4o-mini')
    
    def analyze_job_description(self, job_text: str) -> Dict[str, Any]:
        """
        Analyze a job description and extract structured job posting information.
        
        Args:
            job_text (str): The job description text to analyze
            
        Returns:
            Dict containing:
                - title: Job title
                - company_name: Company name (inferred if not explicit)
                - company_location: Company location
                - company_industry: Company industry
                - company_website: Company website URL
                - description: Concise summary (2-3 sentences max)
                - job_location: Job location (Remote, City, etc.)
                - posted_date: Posted date in YYYY-MM-DD format (empty if not found)
                - close_date: Application deadline in YYYY-MM-DD format (empty if not found)
                - requirements: List of must-have skills/requirements only
                
        Raises:
            Exception: If OpenAI API call fails
        """
        if not job_text or not job_text.strip():
            raise ValueError("Job description text cannot be empty")
        
        system_prompt = """You are an expert job description analyzer. Your task is to extract and structure key information from job postings.

Analyze the job description and extract:
1. **title**: Job title/position name
2. **company_name**: Company name - if not explicitly stated, attempt to infer from context clues
3. **company_location**: Company headquarters or main location
4. **company_industry**: Industry sector (e.g., Technology, Finance, Healthcare)
5. **company_website**: Company website URL if mentioned
6. **description**: A concise 2-3 sentence summary of the role and responsibilities
7. **job_location**: Where the job is based (e.g., "Remote", "San Francisco, CA", "Hybrid - NYC")
8. **posted_date**: Job posting date in YYYY-MM-DD format - return empty string "" if not found
9. **close_date**: Application deadline in YYYY-MM-DD format - return empty string "" if not found
10. **requirements**: Array of must-have/required skills and qualifications ONLY (not preferred/nice-to-have)

IMPORTANT:
- Attempt to infer company information from context when not explicitly stated
- Return empty string "" for any text fields if information is not found or cannot be inferred
- Return empty array [] for requirements if none are specified
- Keep description summary concise (maximum 3 sentences)
- Only include explicitly required/must-have items in requirements array

Return a JSON object with these exact keys."""

        user_prompt = f"""Analyze this job description and extract structured information:

{job_text}

Return a JSON object with the following structure:
{{
    "title": "Job Title",
    "company_name": "Company Name",
    "company_location": "City, State/Country",
    "company_industry": "Industry",
    "company_website": "https://example.com",
    "description": "Brief 2-3 sentence summary of the role",
    "job_location": "Remote or City, State",
    "posted_date": "YYYY-MM-DD or empty string",
    "close_date": "YYYY-MM-DD or empty string",
    "requirements": ["requirement1", "requirement2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=1000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Ensure all expected keys exist
            default_structure = {
                "title": "",
                "company_name": "",
                "company_location": "",
                "company_industry": "",
                "company_website": "",
                "description": "",
                "job_location": "",
                "posted_date": "",
                "close_date": "",
                "requirements": []
            }
            
            # Merge with defaults to ensure all keys exist
            for key in default_structure:
                if key not in result:
                    result[key] = default_structure[key]
            
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse OpenAI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def get_usage_stats(self) -> Dict[str, str]:
        """
        Get information about the AI client configuration.
        
        Returns:
            Dict with model and status information
        """
        return {
            "model": self.default_model,
            "status": "configured",
            "provider": "OpenAI"
        }


# Singleton instance
_ai_client_instance: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """
    Get or create the singleton AIClient instance.
    
    Returns:
        AIClient: The singleton AIClient instance
    """
    global _ai_client_instance
    if _ai_client_instance is None:
        _ai_client_instance = AIClient()
    return _ai_client_instance
