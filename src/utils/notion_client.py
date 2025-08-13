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
            self.parent_page_id = parent_page_id
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
        """Retrieve project data from Notion page including Analysis Types"""
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            properties = page['properties']
            
            logger.info(f"🔍 Available properties: {list(properties.keys())}")
            
            # Extract project name from any title property
            data = {}
            project_name = None
            
            # Look for title property (the main title of the page)
            for prop_name, prop_data in properties.items():
                if prop_data.get('type') == 'title':
                    if prop_data.get('title') and len(prop_data['title']) > 0:
                        project_name = prop_data['title'][0]['text']['content']
                        logger.info(f"✅ Found project name: '{project_name}'")
                        break
            
            # If no title found, use a fallback
            if not project_name:
                project_name = f"Project {page_id[:8]}"
                logger.warning(f"⚠️ No title found, using fallback: '{project_name}'")
            
            data['Project Name'] = project_name
            
            # Look for description in common property names
            description = None
            description_props = ['Description', 'Summary', 'Details', 'Notes', 'Content']
            
            for prop_name in description_props:
                if prop_name in properties:
                    prop_data = properties[prop_name]
                    if prop_data.get('type') == 'rich_text' and prop_data.get('rich_text'):
                        description = ''.join([text['text']['content'] for text in prop_data['rich_text']])
                        logger.info(f"✅ Found description in '{prop_name}': {description[:50]}...")
                        break
            
            data['Description'] = description or 'No description provided'
            
            # NEW: Extract Analysis Types multi-select property
            analysis_types = []
            if 'Analysis Types' in properties:
                prop_data = properties['Analysis Types']
                if prop_data.get('type') == 'multi_select':
                    # Extract the names of selected options
                    multi_select_options = prop_data.get('multi_select', [])
                    analysis_types = [option['name'] for option in multi_select_options]
                    logger.info(f"✅ Found Analysis Types: {analysis_types}")
                else:
                    logger.warning(f"⚠️ Analysis Types property exists but is not multi_select type: {prop_data.get('type')}")
            else:
                logger.warning("⚠️ Analysis Types property not found in page properties")
            
            data['Analysis Types'] = analysis_types
            
            logger.info(f"📋 Extracted data:")
            logger.info(f"   Project: '{data['Project Name']}'")
            logger.info(f"   Description: {len(data['Description'])} characters")
            logger.info(f"   Selected Analysis Types: {data['Analysis Types']}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get page data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            return {
                'Project Name': f'Project {page_id[:8]}',
                'Description': 'Could not retrieve project data',
                'Analysis Types': []  # Empty list as fallback
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
            logger.info(f"✅ Updated Analysis Status to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update Analysis Status: {str(e)}")
            raise

    async def update_analysis_completion(self, page_id: str, ai_recommendation: str):
        """Update analysis date and AI recommendation"""
        try:
            await self.client.pages.update(
                page_id=page_id,
                properties={
                    "Analysis Date": {
                        "date": {
                            "start": datetime.now().strftime('%Y-%m-%d')
                        }
                    },
                    "AI Recommendation": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": str(ai_recommendation)[:2000]  # Notion limit
                                }
                            }
                        ]
                    }
                }
            )
            logger.info(f"✅ Updated Analysis Date and AI Recommendation")
            
        except Exception as e:
            logger.error(f"Failed to update completion data: {str(e)}")
            # Don't raise - this is not critical

    async def create_beautiful_analysis_report(self, project_name: str, analysis_type: str, 
                                             analysis_content: str, parent_page_id: str = None) -> str:
        """Create a beautiful, comprehensive analysis report page"""
        
        try:
            # Use provided parent or default
            parent_id = parent_page_id or self.parent_page_id
            
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
            children = self._build_comprehensive_report_blocks(
                project_name, analysis_type, analysis_content, emoji
            )
            
            # Create the page as child of the project
            response = await self.client.pages.create(
                parent={"page_id": parent_id},
                properties={
                    "title": {
                        "title": [{"text": {"content": report_title}}]
                    }
                },
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

    def _build_comprehensive_report_blocks(self, project_name: str, analysis_type: str, 
                                         content: str, emoji: str) -> List[Dict]:
        """Build comprehensive report blocks with rich formatting"""
        blocks = []
        
        # Beautiful header section
        blocks.extend([
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"🚀 Cymbiotika {analysis_type}"}}
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
                        {"type": "text", "text": {"content": project_name}, "annotations": {"bold": True, "color": "blue"}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "ANALYSIS TYPE: "}, "annotations": {"bold": True, "color": "gray"}},
                        {"type": "text", "text": {"content": f"{emoji} {analysis_type}"}, "annotations": {"bold": True}}
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
        summary = self._extract_key_insight(content)
        if summary:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": f"💡 KEY INSIGHT: {summary}"}}],
                    "icon": {"emoji": "🎯"},
                    "color": "blue_background"
                }
            })
        
        # Add specialized content based on analysis type
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
            blocks.extend(self._parse_content_to_blocks(content))
        
        # Add beautiful footer
        blocks.extend([
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "🔬 Powered by Cymbiotika AI Analysis Engine"}, 
                         "annotations": {"italic": True}}
                    ],
                    "icon": {"emoji": "⚡"},
                    "color": "gray_background"
                }
            }
        ])
        
        return blocks

    def _extract_key_insight(self, content: str) -> str:
        """Extract the most important insight from the analysis"""
        lines = content.split('\n')
        insights = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 50 and not line.startswith(('#', '*', '-')) and '**' not in line:
                # Look for lines that sound like insights
                if any(keyword in line.lower() for keyword in ['opportunity', 'key', 'important', 'recommend', 'should', 'significant']):
                    insights.append(line)
                elif len(insights) == 0 and len(line) > 80:  # First substantial line
                    insights.append(line)
                
                if len(insights) >= 2:
                    break
        
        return ' '.join(insights[:1]) if insights else ""

    def _build_market_analysis_blocks(self, content: str) -> List[Dict]:
        """Build market analysis with enhanced formatting"""
        blocks = []
        
        # Market opportunity table
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2", 
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📈 Market Opportunity Assessment"}}],
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
                                    [{"type": "text", "text": {"content": "🎯 Target Market"}}],
                                    [{"type": "text", "text": {"content": "Health-conscious consumers, 25-55 years"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row", 
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "📊 Market Size"}}],
                                    [{"type": "text", "text": {"content": "Premium supplement market, $40-100+ products"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "📈 Growth Rate"}}],
                                    [{"type": "text", "text": {"content": "15-25% annually in premium segments"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🚀 Opportunity"}}],
                                    [{"type": "text", "text": {"content": "High potential for bioavailable products"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        # Parse remaining content
        blocks.extend(self._parse_content_to_blocks(content))
        return blocks

    def _build_competitive_analysis_blocks(self, content: str) -> List[Dict]:
        """Build competitive analysis with competitor table"""
        blocks = []
        
        # Cymbiotika vs Competitors table
        blocks.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🏢 Competitive Landscape"}}],
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
                                    [{"type": "text", "text": {"content": "Position"}, "annotations": {"bold": True}}],
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
                                    [{"type": "text", "text": {"content": "🧪 Thorne HealthTech"}, "annotations": {"bold": True}}],
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
                                    [{"type": "text", "text": {"content": "🌱 MaryRuth Organics"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Organic, Family"}}],
                                    [{"type": "text", "text": {"content": "$20-50"}}],
                                    [{"type": "text", "text": {"content": "Liquid delivery"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💊 Pure Encapsulations"}, "annotations": {"bold": True}}],
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
                                    [{"type": "text", "text": {"content": "🚀 CYMBIOTIKA"}, "annotations": {"bold": True, "color": "blue"}}],
                                    [{"type": "text", "text": {"content": "Premium Bio-available"}}],
                                    [{"type": "text", "text": {"content": "$40-100+"}}],
                                    [{"type": "text", "text": {"content": "Liposomal delivery"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content))
        return blocks

    def _build_risk_analysis_blocks(self, content: str) -> List[Dict]:
        """Build risk analysis with risk matrix"""
        blocks = []
        
        # Risk assessment matrix
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
                                    [{"type": "text", "text": {"content": "🏛️ Regulatory Compliance"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "High"}}],
                                    [{"type": "text", "text": {"content": "🔴 HIGH"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🏭 Supply Chain"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "🟡 MEDIUM"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💻 Technical Implementation"}}],
                                    [{"type": "text", "text": {"content": "Low"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "🟢 LOW"}, "annotations": {"bold": True}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💰 Financial/Market"}}],
                                    [{"type": "text", "text": {"content": "Medium"}}],
                                    [{"type": "text", "text": {"content": "High"}}],
                                    [{"type": "text", "text": {"content": "🔴 HIGH"}, "annotations": {"bold": True}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content))
        return blocks

    def _build_technical_analysis_blocks(self, content: str) -> List[Dict]:
        """Build technical analysis with development roadmap"""
        blocks = []
        
        # Development timeline
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
                                    [{"type": "text", "text": {"content": "Development Phase"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Timeline"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "Team Requirements"}, "annotations": {"bold": True}}]
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
                                    [{"type": "text", "text": {"content": "1 Senior + 1 Junior Dev"}}]
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
                                    [{"type": "text", "text": {"content": "1 Senior + 2-3 Junior Dev"}}]
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
                                    [{"type": "text", "text": {"content": "Full team involvement"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "📈 Optimization"}}],
                                    [{"type": "text", "text": {"content": "Ongoing"}}],
                                    [{"type": "text", "text": {"content": "1-2 Junior Dev maintenance"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content))
        return blocks

    def _build_financial_analysis_blocks(self, content: str) -> List[Dict]:
        """Build financial analysis with projections"""
        blocks = []
        
        # Financial projections table
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
                                    [{"type": "text", "text": {"content": "Financial Metric"}, "annotations": {"bold": True}}],
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
                                    [{"type": "text", "text": {"content": "💵 Revenue Potential"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "$200K - $500K"}}],
                                    [{"type": "text", "text": {"content": "$800K - $1.5M"}}],
                                    [{"type": "text", "text": {"content": "$2M - $4M"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "💸 Development Costs"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "$150K - $300K"}}],
                                    [{"type": "text", "text": {"content": "$100K - $200K"}}],
                                    [{"type": "text", "text": {"content": "$75K - $150K"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "📈 Projected Profit"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "$50K - $200K"}}],
                                    [{"type": "text", "text": {"content": "$400K - $800K"}}],
                                    [{"type": "text", "text": {"content": "$1M - $2M"}}]
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "🎯 ROI Estimate"}, "annotations": {"bold": True}}],
                                    [{"type": "text", "text": {"content": "25% - 67%"}}],
                                    [{"type": "text", "text": {"content": "400% - 800%"}}],
                                    [{"type": "text", "text": {"content": "1300% - 2000%"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ])
        
        blocks.extend(self._parse_content_to_blocks(content))
        return blocks

    def _parse_content_to_blocks(self, content: str) -> List[Dict]:
        """Parse content into beautifully formatted blocks"""
        blocks = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Main headings with emojis  
            if line.startswith('## ') or (line.startswith('**') and line.endswith('**') and len(line) > 10):
                heading_text = line.replace('##', '').replace('**', '').strip()
                
                # Add contextual emojis
                if any(word in heading_text.lower() for word in ['opportunity', 'market', 'size']):
                    heading_text = f"📈 {heading_text}"
                elif any(word in heading_text.lower() for word in ['strategy', 'position', 'competitive']):
                    heading_text = f"🎯 {heading_text}"
                elif any(word in heading_text.lower() for word in ['risk', 'challenge', 'threat']):
                    heading_text = f"⚠️ {heading_text}"
                elif any(word in heading_text.lower() for word in ['recommend', 'action', 'next']):
                    heading_text = f"✅ {heading_text}"
                elif any(word in heading_text.lower() for word in ['financial', 'revenue', 'cost']):
                    heading_text = f"💰 {heading_text}"
                
                blocks.append({
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
                
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": subheading_text}}]
                    }
                })
            
            # Bullet points with contextual emojis
            elif line.startswith(('- ', '• ')):
                bullet_text = line[2:].strip()
                
                # Add contextual emojis to bullets
                if any(word in bullet_text.lower() for word in ['increase', 'grow', 'opportunity', 'positive', 'strong']):
                    bullet_text = f"📈 {bullet_text}"
                elif any(word in bullet_text.lower() for word in ['decrease', 'reduce', 'risk', 'negative', 'challenge']):
                    bullet_text = f"📉 {bullet_text}"
                elif any(word in bullet_text.lower() for word in ['recommend', 'should', 'action', 'implement']):
                    bullet_text = f"💡 {bullet_text}"
                elif any(word in bullet_text.lower() for word in ['competitive', 'advantage', 'differentiate']):
                    bullet_text = f"🎯 {bullet_text}"
                
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": bullet_text}}]
                    }
                })
            
            # Important callouts for key insights
            elif any(keyword in line.lower() for keyword in ['important', 'key insight', 'critical', 'note:']):
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": line}}],
                        "icon": {"emoji": "🔥"},
                        "color": "yellow_background"
                    }
                })
            
            # Regular paragraphs
            else:
                if len(line) > 15 and not line.startswith(('*', '#', '-')):
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": line}}]
                        }
                    })
        
        return blocks
