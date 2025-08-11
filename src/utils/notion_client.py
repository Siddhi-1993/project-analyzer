import asyncio
from typing import Dict, Any
from notion_client import AsyncClient
import logging

logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self, token: str, database_id: str):
        self.client = AsyncClient(auth=token)
        self.database_id = database_id

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
        """Update the status of a project"""
        try:
            await self.client.pages.update(
                page_id=page_id,
                properties={
                    "Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            )
            logger.info(f"Updated status to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update status: {str(e)}")
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
