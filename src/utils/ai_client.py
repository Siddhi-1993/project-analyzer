import asyncio
import logging
import openai
import os

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, api_key: str):
        try:
            # Set the OpenAI API key
            openai.api_key = api_key
            logger.info("AIClient initialized successfully with OpenAI v0.28")
        except Exception as e:
            logger.error(f"Failed to initialize AIClient: {str(e)}")
            raise

    async def generate_response(self, prompt: str, context: str = "", model: str = "gpt-4") -> str:
        """Generate AI response for analysis using OpenAI v0.28 API"""
        try:
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"You are a business analyst providing professional project analysis. Context: {context}"
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Use the older OpenAI API format
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.3
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            return f"Analysis failed: {str(e)}"

    async def analyze_with_web_research(self, prompt: str, search_queries: list = None) -> str:
        """Enhanced analysis with web research capability"""
        # This could be extended to include web scraping or search API calls
        # For now, it uses the base AI analysis
        return await self.generate_response(prompt)
