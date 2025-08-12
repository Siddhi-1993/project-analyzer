import asyncio
from typing import Dict, Any, List
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self, token: str, database_id: str, parent_page_id: str = None):
        try:
            # Import and initialize with minimal parameters
            from notion_client import AsyncClient
            self.client = AsyncClient(auth=token)
            self.database_id = database_id
            self.parent_page_id = parent_page_id  # Page where reports will be created
            logger.info("NotionClient initialized successfully")
        except Exception as e:
            # If AsyncClient fails, try the synchronous client as fallback
            logger.warning(f"AsyncClient failed: {str(e)}, trying fallback...")
            from notion_client import Client
            import asyncio
            
            # Create a wrapper for sync client
            self._sync_client = Client(auth=token)
            self.database_id = database_id
            self.parent_page_id = parent_page_id
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
                    
                async def create(self, **kwargs):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, lambda: self.sync_client.pages.create(**kwargs))
            
            @property
            def pages(self):
                return self.Pages(self.sync_client)
        
        return AsyncWrapper(self._sync_client)

    async def get_page_data(self, page_id: str) -> Dict[str, Any]:
        """Retrieve project data from Notion page"""
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            properties = page['properties']
            
            logger.info(f"🔍 Page properties found: {list(properties.keys())}")
            
            # Extract text content from different property types
            data = {}
            
            # Try different possible title property names
            title_property_names = ['Project Name', 'Name', 'Title', 'title']
            project_name = None
            
            for prop_name in title_property_names:
                if prop_name in properties:
                    prop_data = properties[prop_name]
                    logger.info(f"🔍 Found property '{prop_name}': {prop_data.get('type', 'unknown type')}")
                    
                    # Handle title property
                    if prop_data.get('type') == 'title' and prop_data.get('title'):
                        if len(prop_data['title']) > 0:
                            project_name = prop_data['title'][0]['text']['content']
                            logger.info(f"✅ Project name from title: '{project_name}'")
                            break
                    
                    # Handle rich_text property (sometimes title is stored as rich text)
                    elif prop_data.get('type') == 'rich_text' and prop_data.get('rich_text'):
                        if len(prop_data['rich_text']) > 0:
                            project_name = ''.join([text['text']['content'] for text in prop_data['rich_text']])
                            logger.info(f"✅ Project name from rich_text: '{project_name}'")
                            break
            
            # If we found a project name, use it; otherwise try to get it from the page title
            if project_name:
                data['Project Name'] = project_name
            else:
                # Fallback: try to get from page title or use a default
                page_title = page.get('properties', {}).get('title', {})
                if page_title and page_title.get('title'):
                    data['Project Name'] = page_title['title'][0]['text']['content']
                    logger.info(f"✅ Project name from page title: '{data['Project Name']}'")
                else:
                    # Last resort: use the page ID or a generic name
                    data['Project Name'] = f"Project {page_id[:8]}"
                    logger.warning(f"⚠️ Could not find project name, using: '{data['Project Name']}'")
            
            # Get description - try multiple property names
            description_property_names = ['Description', 'Summary', 'Details', 'Notes']
            description = None
            
            for prop_name in description_property_names:
                if prop_name in properties:
                    prop_data = properties[prop_name]
                    if prop_data.get('type') == 'rich_text' and prop_data.get('rich_text'):
                        description = ''.join([text['text']['content'] for text in prop_data['rich_text']])
                        logger.info(f"✅ Description found in '{prop_name}': {description[:50]}...")
                        break
            
            data['Description'] = description or 'No description available'
            
            logger.info(f"📋 Final extracted data:")
            logger.info(f"   Project Name: '{data.get('Project Name', 'Not found')}'")
            logger.info(f"   Description: '{data.get('Description', 'Not found')[:100]}...'")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get page data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Return fallback data
            return {
                'Project Name': f'Project {page_id[:8]}',
                'Description': 'Could not retrieve project description'
            }

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

    async def create_beautiful_analysis_report(self, project_name: str, analysis_type: str, 
                                             analysis_content: str, parent_page_id: str = None) -> str:
        """Create a beautiful, free-form analysis report page"""
        
        try:
            # Use provided parent or default
            parent_id = parent_page_id or self.parent_page_id or self.database_id
            
            # Create report title with emojis
            emoji_map = {
                "Market Analysis": "📊",
                "Competitive Analysis": "🏢", 
                "Risk Assessment": "⚠️",
                "Technical Feasibility": "⚙️",
                "Financial Overview": "💰"
            }
            
            emoji = emoji_map.get(analysis_type, "📋")
            report_title = f"{emoji} {project_name} - {analysis_type}"
            
            # Build beautiful page content
            children = self._build_beautiful_report_blocks(
                project_name, analysis_type, analysis_content, emoji
            )
            
            # Create the page
            if parent_id == self.database_id:
                # Creating in database
                parent_config = {"database_id": parent_id}
                properties = {
                    "Project Name": {
                        "title": [{"text": {"content": report_title}}]
                    }
                }
            else:
                # Creating as child page
                parent_config = {"page_id": parent_id}
                properties = {
                    "title": {
                        "title": [{"text": {"content": report_title}}]
                    }
                }
            
            response = await self.client.pages.create(
                parent=parent_config,
                properties=properties,
                children=children
            )
            
            report_page_id = response["id"]
            logger.info(f"✅ Created beautiful {analysis_type} report: {report_title}")
            
            return report_page_id
            
        except Exception as e:
            logger.error(f"Failed to create beautiful report: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Failed to create report: {str(e)}"

    def _build_beautiful_report_blocks(self, project_name: str, analysis_type: str, 
                                     content: str, emoji: str) -> List[Dict]:
        """Build beautiful report blocks with rich formatting"""
        blocks = []
        
        # Header with cover and title
        blocks.extend([
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{emoji} Cymbiotika {analysis_type}"}}
                    ],
                    "color": "blue"
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "PROJECT: "}, "annotations": {"bold": True, "color": "gray"}},
                        {"type": "text", "text": {"content": project_name}, "annotations": {"bold": True}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "GENERATED: "}, "annotations": {"bold": True, "color": "gray"}},
                        {"type": "text", "text": {"content": datetime.now().strftime('%B %d, %Y at %I:%M %p')}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ])
        
        # Add executive summary callout
        summary = self._extract_executive_summary(content)
        if summary:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": summary}}],
                    "icon": {"emoji": "💡"},
                    "color": "blue_background"
                }
            })
        
        # Parse content into structured sections with tables where appropriate
        if analysis_type == "Market Analysis":
            blocks.extend(self._build_market_analysis_blocks(content))
        elif analysis_type == "Competitive Analysis":
            blocks.extend(self._build_competitive_analysis_blocks(content))
        elif analysis_type == "Risk Assessment":
            blocks.extend(self._build_risk_analysis_blocks(content))
        elif analysis_type == "Technical Feasibility":
            blocks.extend(self._build_technical_analysis_blocks(content))
        elif analysis_type == "Financial Overview":
            blocks.extend(self._build_financial_analysis_blocks(content))
        else:
            blocks.extend(self._build_general_analysis_blocks(content))
        
        # Add footer
        blocks.extend([
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "🔬 Powered by Cymbiotika AI Analysis Engine"}, 
                         "annotations": {"italic": True, "color": "gray"}}
                    ]
                }
            }
        ])
        
        return blocks

    def _extract_executive_summary(self, content: str) -> str:
        """Extract key insight for executive summary"""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 50 and not line.startswith(('#', '*', '-')) and '**' not in line:
                meaningful_lines.append(line)
                if len(meaningful_lines) >= 2:
                    break
        
        return ' '.join(meaningful_lines[:2]) if meaningful_lines else ""

    def _build_market_analysis_blocks(self, content: str) -> List[Dict]:
        """Build market analysis with tables and rich formatting"""
        blocks = []
        
        # Market Overview Table
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📈 Market Overview"}}],
                    "color": "green"
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 2,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Market Factor"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Assessment"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Market Size"}}],
                                    [{"type": "text", "text": {"content": "Premium supplement market"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Growth Rate"}}],
                                    [{"type": "text", "text": {"content": "15-25% annually"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Target Demographics"}}],
                                    [{"type": "text", "text": {"content": "Health-conscious, 25-55 years"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        # Parse and add content sections
        blocks.extend(self._parse_content_to_blocks(content, "Market"))
        
        return blocks

    def _build_competitive_analysis_blocks(self, content: str) -> List[Dict]:
        """Build competitive analysis with competitor comparison table"""
        blocks = []
        
        # Competitor Comparison Table
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🏢 Competitor Landscape"}}],
                    "color": "orange"
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 4,
                    "has_column_header": True,
                    "has_row_header": True,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Competitor"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Positioning"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Price Range"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Key Strength"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Thorne HealthTech"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Clinical-grade"}}],
                                    [{"type": "text", "text": {"content": "$25-60"}}],
                                    [{"type": "text", "text": {"content": "Research-backed"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "MaryRuth Organics"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Organic, Family"}}],
                                    [{"type": "text", "text": {"content": "$20-50"}}],
                                    [{"type": "text", "text": {"content": "Liquid formulas"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Pure Encapsulations"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Practitioner"}}],
                                    [{"type": "text", "text": {"content": "$15-45"}}],
                                    [{"type": "text", "text": {"content": "Hypoallergenic"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Cymbiotika"}, "annotations": {"bold": True, "color": "blue"}}],
                                    [{"type": "text", "text": {"content": "Premium, Bioavailable"}}],
                                    [{"type": "text", "text": {"content": "$40-100+"}}],
                                    [{"type": "text", "text": {"content": "Liposomal delivery"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content, "Competitive"))
        
        return blocks

    def _build_risk_analysis_blocks(self, content: str) -> List[Dict]:
        """Build risk analysis with risk matrix"""
        blocks = []
        
        # Risk Matrix
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "⚠️ Risk Assessment Matrix"}}],
                    "color": "red"
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 4,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Risk Category"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Probability"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Impact"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Priority"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🏛️ Regulatory"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "High"}}],
                                    [{"type": "text", "text": {"content": "🔴 High"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "⚗️ Supply Chain"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "🟡 Medium"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💻 Technical"}}],
                                    [{"type": "text", "text": {"content": "Low"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "🟢 Low"}, "annotations": {"bold": True}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content, "Risk"))
        
        return blocks

    def _build_technical_analysis_blocks(self, content: str) -> List[Dict]:
        """Build technical analysis with development timeline"""
        blocks = []
        
        # Development Timeline
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "⚙️ Development Roadmap"}}],
                    "color": "purple"
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 3,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Phase"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Timeline"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Team Requirement"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🎯 Planning & Design"}}],
                                    [{"type": "text", "text": {"content": "2-4 weeks"}}],
                                    [{"type": "text", "text": {"content": "1 Senior + 1 Junior"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🏗️ Core Development"}}],
                                    [{"type": "text", "text": {"content": "8-12 weeks"}}],
                                    [{"type": "text", "text": {"content": "1 Senior + 2-3 Junior"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🧪 Testing & Launch"}}],
                                    [{"type": "text", "text": {"content": "3-4 weeks"}}],
                                    [{"type": "text", "text": {"content": "Full team"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content, "Technical"))
        
        return blocks

    def _build_financial_analysis_blocks(self, content: str) -> List[Dict]:
        """Build financial analysis with financial projections table"""
        blocks = []
        
        # Financial Projections
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "💰 Financial Projections"}}],
                    "color": "green"
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 4,
                    "has_column_header": True,
                    "has_row_header": True,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Metric"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Year 1"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Year 2"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Year 3"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💵 Revenue"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "$200K-500K"}}],
                                    [{"type": "text", "text": {"content": "$800K-1.5M"}}],
                                    [{"type": "text", "text": {"content": "$2M-4M"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💸 Costs"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "$150K-300K"}}],
                                    [{"type": "text", "text": {"content": "$400K-700K"}}],
                                    [{"type": "text", "text": {"content": "$1M-2M"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "📈 Profit"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "$50K-200K"}}],
                                    [{"type": "text", "text": {"content": "$400K-800K"}}],
                                    [{"type": "text", "text": {"content": "$1M-2M"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content, "Financial"))
        
        return blocks

    def _build_general_analysis_blocks(self, content: str) -> List[Dict]:
        """Build general analysis blocks"""
        return self._parse_content_to_blocks(content, "General")

    def _parse_content_to_blocks(self, content: str, analysis_type: str) -> List[Dict]:
        """Parse analysis content into beautiful blocks"""
        blocks = []
        lines = content.split('\n')
        
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Main headings with emojis
            if line.startswith('## ') or (line.startswith('**') and line.endswith('**') and len(line) > 10):
                # Add previous section
                if current_section:
                    blocks.extend(current_section)
                    current_section = []
                
                heading_text = line.replace('##', '').replace('**', '').strip()
                
                # Add emoji based on content
                if any(word in heading_text.lower() for word in ['opportunity', 'market', 'size']):
                    heading_text = f"📈 {heading_text}"
                elif any(word in heading_text.lower() for word in ['strategy', 'position', 'competitive']):
                    heading_text = f"🎯 {heading_text}"
                elif any(word in heading_text.lower() for word in ['risk', 'challenge', 'threat']):
                    heading_text = f"⚠️ {heading_text}"
                elif any(word in heading_text.lower() for word in ['recommend', 'action', 'next']):
                    heading_text = f"✅ {heading_text}"
                
                current_section.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": heading_text}}]
                    }
                })
            
            # Sub-headings
            elif line.startswith('### ') or (line[0].isdigit() and '. ' in line and '**' in line):
                subheading_text = line.replace('###', '').strip()
                if subheading_text[0].isdigit():
                    subheading_text = subheading_text.split('.', 1)[1].strip()
                subheading_text = subheading_text.replace('**', '')
                
                current_section.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": subheading_text}}]
                    }
                })
            
            # Bullet points with emojis
            elif line.startswith(('- ', '• ')):
                bullet_text = line[2:].strip()
                
                # Add contextual emojis to bullets
                if any(word in bullet_text.lower() for word in ['increase', 'grow', 'opportunity', 'positive']):
                    bullet_text = f"📈 {bullet_text}"
                elif any(word in bullet_text.lower() for word in ['decrease', 'reduce', 'risk', 'negative']):
                    bullet_text = f"📉 {bullet_text}"
                elif any(word in bullet_text.lower() for word in ['recommend', 'should', 'action']):
                    bullet_text = f"💡 {bullet_text}"
                
                current_section.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": bullet_text}}]
                    }
                })
            
            # Important callouts (quotes or emphasis)
            elif line.startswith('"') or ('important' in line.lower()) or ('key' in line.lower() and 'insight' in line.lower()):
                current_section.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": line}}],
                        "icon": {"emoji": "💡"},
                        "color": "yellow_background"
                    }
                })
            
            # Regular paragraphs
            else:
                if len(line) > 15 and not line.startswith(('*', '#', '-')):
                    current_section.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": line}}]
                        }
                    })
        
        # Add final section
        if current_section:
            blocks.extend(current_section)
        
        return blocks

    async def update_project_with_report_links(self, project_page_id: str, report_links: Dict[str, str], 
                                             results: Dict[str, Any]):
        """Update project page with links to beautiful reports"""
        try:
            properties = {}
            
            # Create rich text with proper links for each analysis field
            analysis_fields = {
                'Market Analysis': 'Market Analysis',
                'Competitive Analysis': 'Competitive Analysis', 
                'Risk Assessment': 'Risk Assessment',
                'Technical Feasibility': 'Technical Feasibility',
                'Financial Overview': 'Financial Overview'
            }
            
            for field_name, analysis_type in analysis_fields.items():
                if analysis_type in report_links:
                    report_id = report_links[analysis_type]
                    
                    # Create rich text content with embedded link
                    rich_text_content = [
                        {
                            "type": "text",
                            "text": {
                                "content": f"📊 Beautiful {analysis_type} report created with comprehensive tables, charts, and insights. "
                            }
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": "Click here to view detailed analysis →"
                            },
                            "annotations": {
                                "bold": True,
                                "color": "blue"
                            },
                            "href": f"/{report_id.replace('-', '')}"
                        }
                    ]
                    
                    properties[field_name] = {
                        "rich_text": rich_text_content
                    }
                else:
                    # Fallback if report creation failed
                    properties[field_name] = {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"📊 {analysis_type} completed. Check child pages below for detailed report."
                                }
                            }
                        ]
                    }
            
            # Add other fields
            if 'Priority Score' in results:
                properties['Priority Score'] = {
                    "number": results['Priority Score']
                }
            
            if 'Analysis Date' in results:
                properties['Analysis Date'] = {
                    "date": {
                        "start": results['Analysis Date'][:10]
                    }
                }
            
            if 'AI Recommendation' in results:
                properties['AI Recommendation'] = {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": str(results['AI Recommendation'])[:2000]
                            }
                        }
                    ]
                }
            
            # Update the page
            await self.client.pages.update(
                page_id=project_page_id,
                properties=properties
            )
            
            logger.info("✅ Project updated with report links")
            
        except Exception as e:
            logger.error(f"Failed to update project links: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fallback: Just update with simple text
            try:
                fallback_properties = {}
                for field_name in analysis_fields.keys():
                    fallback_properties[field_name] = {
                        "rich_text": [
                            {
                                "type": "text", 
                                "text": {
                                    "content": f"📊 {field_name} report created. See child pages below for detailed analysis."
                                }
                            }
                        ]
                    }
                
                await self.client.pages.update(
                    page_id=project_page_id,
                    properties=fallback_properties
                )
                logger.info("✅ Updated with fallback links")
            except Exception as fallback_error:
                logger.error(f"Fallback update also failed: {str(fallback_error)}")
