import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self, token: str, database_id: str):
        try:
            # Import and initialize with minimal parameters
            from notion_client import AsyncClient
            self.client = AsyncClient(auth=token)
            self.database_id = database_id
            logger.info("NotionClient initialized successfully")
        except Exception as e:
            # If AsyncClient fails, try the synchronous client as fallback
            logger.warning(f"AsyncClient failed: {str(e)}, trying fallback...")
            from notion_client import Client
            import asyncio
            
            # Create a wrapper for sync client
            self._sync_client = Client(auth=token)
            self.database_id = database_id
            self.client = self._async_wrapper()
            logger.info("NotionClient initialized with sync wrapper")

    def _async_wrapper(self):
        """Create async wrapper for sync client"""
        class AsyncWrapper:
            def __init__(self, sync_client):
                self.sync_client = sync_client
                
            class Pages:
                def __init__(self, sync_client):
                    self.sync_client = sync_client
                    
                async def retrieve(self, page_id):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, self.sync_client.pages.retrieve, page_id)
                    
                async def update(self, page_id, properties):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, self.sync_client.pages.update, page_id, properties)
            
            @property
            def pages(self):
                return self.Pages(self.sync_client)
        
        return AsyncWrapper(self._sync_client)

    async def get_page_data(self, page_id: str) -> Dict[str, Any]:
        """Retrieve project data from Notion page"""
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            properties = page['properties']
            
            # Extract text content from different property types
            data = {}
            
            # Title property
            if 'Project Name' in properties and properties['Project Name']['title']:
                data['Project Name'] = properties['Project Name']['title'][0]['text']['content']
            
            # Rich text property
            if 'Description' in properties and properties['Description']['rich_text']:
                data['Description'] = ''.join([
                    text['text']['content'] for text in properties['Description']['rich_text']
                ])
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get page data: {str(e)}")
            raise

    async def update_page_status(self, page_id: str, status: str):
        """Update the analysis status of a project"""
        try:
            await self.client.pages.update(
                page_id=page_id,
                properties={
                    "Analysis Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            )
            logger.info(f"Updated Analysis Status to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update Analysis Status: {str(e)}")
            raise

    async def update_page_results(self, page_id: str, results: Dict[str, Any]):
        """Update page with analysis results"""
        try:
            properties = {}
            
            # Text fields
            text_fields = [
                'Market Analysis', 'Competitive Analysis', 'Technical Feasibility',
                'Risk Assessment', 'Financial Overview', 'AI Recommendation'
            ]
            
            for field in text_fields:
                if field in results:
                    properties[field] = {
                        "rich_text": [
                            {
                                "text": {
                                    "content": str(results[field])[:2000]  # Notion limit
                                }
                            }
                        ]
                    }
            
            # Number field
            if 'Priority Score' in results:
                properties['Priority Score'] = {
                    "number": results['Priority Score']
                }
            
            # Date field
            if 'Analysis Date' in results:
                properties['Analysis Date'] = {
                    "date": {
                        "start": results['Analysis Date'][:10]  # YYYY-MM-DD format
                    }
                }
            
            await self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            logger.info("Successfully updated page with analysis results")
            
        except Exception as e:
            logger.error(f"Failed to update results: {str(e)}")
            raise
