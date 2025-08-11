import asyncio
import logging

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, api_key: str):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("AIClient initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AsyncOpenAI: {str(e)}")
            # Fallback to sync client with async wrapper
            try:
                from openai import OpenAI
                self._sync_client = OpenAI(api_key=api_key)
                self.client = self._create_async_wrapper()
                logger.info("AIClient initialized with sync wrapper")
            except Exception as e2:
                logger.error(f"Failed to initialize OpenAI client: {str(e2)}")
                raise

    def _create_async_wrapper(self):
        """Create async wrapper for sync OpenAI client"""
        class AsyncWrapper:
            def __init__(self, sync_client):
                self.sync_client = sync_client
                
            class Chat:
                def __init__(self, sync_client):
                    self.sync_client = sync_client
                    
                class Completions:
                    def __init__(self, sync_client):
                        self.sync_client = sync_client
                        
                    async def create(self, **kwargs):
                        loop = asyncio.get_event_loop()
                        return await loop.run_in_executor(
                            None, 
                            lambda: self.sync_client.chat.completions.create(**kwargs)
                        )
                
                @property
                def completions(self):
                    return self.Completions(self.sync_client)
            
            @property
            def chat(self):
                return self.Chat(self.sync_client)
        
        return AsyncWrapper(self._sync_client)

    async def generate_response(self, prompt: str, context: str = "", model: str = "gpt-4-turbo-preview") -> str:
        """Generate AI response for analysis"""
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
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1500,
                temperature=0.3
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
