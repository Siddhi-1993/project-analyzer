#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging first thing
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point with comprehensive error handling"""
    logger.info("=== Starting Notion Project Analyzer ===")
    
    try:
        # Check environment variables first
        logger.info("Checking environment variables...")
        page_id = os.getenv('PAGE_ID')
        notion_token = os.getenv('NOTION_TOKEN')
        notion_db_id = os.getenv('NOTION_DATABASE_ID')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        logger.info(f"PAGE_ID: {'✅ Set' if page_id else '❌ Missing'}")
        logger.info(f"NOTION_TOKEN: {'✅ Set' if notion_token else '❌ Missing'}")
        logger.info(f"NOTION_DATABASE_ID: {'✅ Set' if notion_db_id else '❌ Missing'}")
        logger.info(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
        
        if not all([page_id, notion_token, notion_db_id, openai_key]):
            logger.error("Missing required environment variables")
            return 1
        
        logger.info("All environment variables are set ✅")
        
        # Try imports
        logger.info("Importing modules...")
        try:
            from utils.notion_client import NotionClient
            logger.info("✅ NotionClient imported")
        except Exception as e:
            logger.error(f"❌ Failed to import NotionClient: {str(e)}")
            return 1
            
        try:
            from utils.ai_client import AIClient
            logger.info("✅ AIClient imported")
        except Exception as e:
            logger.error(f"❌ Failed to import AIClient: {str(e)}")
            return 1
            
        try:
            from analyzers.market_analyzer import MarketAnalyzer
            from analyzers.competitor_analyzer import CompetitorAnalyzer
            from analyzers.technical_analyzer import TechnicalAnalyzer
            from analyzers.risk_analyzer import RiskAnalyzer
            from analyzers.financial_analyzer import FinancialAnalyzer
            logger.info("✅ All analyzers imported")
        except Exception as e:
            logger.error(f"❌ Failed to import analyzers: {str(e)}")
            return 1
        
        # Initialize clients one by one to isolate the issue
        logger.info("Initializing NotionClient...")
        try:
            notion_client = NotionClient(token=notion_token, database_id=notion_db_id)
            logger.info("✅ NotionClient initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize NotionClient: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 1
            
        logger.info("Initializing AIClient...")
        try:
            ai_client = AIClient(api_key=openai_key)
            logger.info("✅ AIClient initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AIClient: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 1
        
        # Initialize analyzers
        logger.info("Initializing analyzers...")
        try:
            analyzers = {
                'market': MarketAnalyzer(ai_client),
                'competitor': CompetitorAnalyzer(ai_client),
                'technical': TechnicalAnalyzer(ai_client),
                'risk': RiskAnalyzer(ai_client),
                'financial': FinancialAnalyzer(ai_client)
            }
            logger.info("✅ Analyzers initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize analyzers: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 1
        
        # Run async analysis
        logger.info("Starting async analysis...")
        analyzer = ProjectAnalyzer(notion_client, ai_client, analyzers)
        asyncio.run(analyzer.analyze_project(page_id))
        
        logger.info("=== Analysis Complete ===")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in main: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

class ProjectAnalyzer:
    def __init__(self, notion_client, ai_client, analyzers):
        self.notion_client = notion_client
        self.ai_client = ai_client
        self.analyzers = analyzers

    async def analyze_project(self, page_id: str) -> Dict[str, Any]:
        """Main analysis function with enhanced error handling"""
        try:
            logger.info(f"Starting analysis for page: {page_id}")
            
            # Update status to analyzing
            logger.info("Updating status to 'Analyzing'...")
            await self.notion_client.update_page_status(page_id, "Analyzing")
            logger.info("✅ Status updated to Analyzing")
            
            # Get project data
            logger.info("Fetching project data from Notion...")
            project_data = await self.notion_client.get_page_data(page_id)
            project_name = project_data.get('Project Name', 'Unknown Project')
            description = project_data.get('Description', 'No description available')
            
            logger.info(f"✅ Project data retrieved:")
            logger.info(f"   Project Name: {project_name}")
            logger.info(f"   Description: {description[:100]}...")
            
            # Run all analyses
            results = {}
            
            # Market Analysis
            logger.info("🔍 Running market analysis...")
            try:
                results['Market Analysis'] = await self.analyzers['market'].analyze(
                    project_name, description
                )
                logger.info("✅ Market analysis completed")
            except Exception as e:
                logger.error(f"❌ Market analysis failed: {str(e)}")
                results['Market Analysis'] = f"Analysis failed: {str(e)}"
            
            # Competitive Analysis
            logger.info("🔍 Running competitive analysis...")
            try:
                results['Competitive Analysis'] = await self.analyzers['competitor'].analyze(
                    project_name, description
                )
                logger.info("✅ Competitive analysis completed")
            except Exception as e:
                logger.error(f"❌ Competitive analysis failed: {str(e)}")
                results['Competitive Analysis'] = f"Analysis failed: {str(e)}"
            
            # Technical Feasibility
            logger.info("🔍 Running technical analysis...")
            try:
                results['Technical Feasibility'] = await self.analyzers['technical'].analyze(
                    project_name, description
                )
                logger.info("✅ Technical analysis completed")
            except Exception as e:
                logger.error(f"❌ Technical analysis failed: {str(e)}")
                results['Technical Feasibility'] = f"Analysis failed: {str(e)}"
            
            # Risk Assessment
            logger.info("🔍 Running risk analysis...")
            try:
                results['Risk Assessment'] = await self.analyzers['risk'].analyze(
                    project_name, description
                )
                logger.info("✅ Risk analysis completed")
            except Exception as e:
                logger.error(f"❌ Risk analysis failed: {str(e)}")
                results['Risk Assessment'] = f"Analysis failed: {str(e)}"
            
            # Financial Overview
            logger.info("🔍 Running financial analysis...")
            try:
                results['Financial Overview'] = await self.analyzers['financial'].analyze(
                    project_name, description
                )
                logger.info("✅ Financial analysis completed")
            except Exception as e:
                logger.error(f"❌ Financial analysis failed: {str(e)}")
                results['Financial Overview'] = f"Analysis failed: {str(e)}"
            
            # Generate overall recommendation and priority score
            logger.info("🔍 Generating recommendation...")
            try:
                recommendation, priority_score = await self._generate_recommendation(
                    project_name, description, results
                )
                results['AI Recommendation'] = recommendation
                results['Priority Score'] = priority_score
                results['Analysis Date'] = datetime.now().isoformat()
                logger.info(f"✅ Recommendation generated (Priority: {priority_score}/10)")
            except Exception as e:
                logger.error(f"❌ Recommendation generation failed: {str(e)}")
                results['AI Recommendation'] = f"Recommendation failed: {str(e)}"
                results['Priority Score'] = 5
                results['Analysis Date'] = datetime.now().isoformat()
            
            # Update Notion page with results
            logger.info("📝 Updating Notion page with results...")
            await self.notion_client.update_page_results(page_id, results)
            logger.info("✅ Results updated in Notion")
            
            # Update status to complete
            logger.info("Updating status to 'Complete'...")
            await self.notion_client.update_page_status(page_id, "Complete")
            logger.info("✅ Status updated to Complete")
            
            logger.info(f"🎉 Analysis completed successfully for: {project_name}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed with error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            try:
                await self.notion_client.update_page_status(page_id, "Error")
                logger.info("Status updated to 'Error'")
            except:
                logger.error("Failed to update status to Error")
            
            raise

    async def _generate_recommendation(self, name: str, description: str, analyses: Dict[str, str]) -> tuple[str, int]:
        """Generate overall recommendation and priority score"""
        try:
            combined_analysis = f"""
            Project: {name}
            Description: {description}
            
            Market Analysis: {analyses.get('Market Analysis', '')}
            Competitive Analysis: {analyses.get('Competitive Analysis', '')}
            Technical Feasibility: {analyses.get('Technical Feasibility', '')}
            Risk Assessment: {analyses.get('Risk Assessment', '')}
            Financial Overview: {analyses.get('Financial Overview', '')}
            """
            
            recommendation = await self.ai_client.generate_response(
                f"""Based on the comprehensive analysis above, provide:
                1. Executive summary (2-3 sentences)
                2. Key strengths and concerns
                3. Recommended next steps
                4. Go/No-Go recommendation with reasoning
                
                Keep it concise but actionable.""",
                combined_analysis
            )
            
            # Generate priority score (1-10)
            priority_response = await self.ai_client.generate_response(
                """Based on the analysis, rate this project's priority on a scale of 1-10 where:
                10 = High impact, low risk, strong market opportunity, technically feasible
                1 = Low impact, high risk, poor market fit, technically challenging
                
                Respond with just the number (1-10).""",
                combined_analysis
            )
            
            try:
                priority_score = int(priority_response.strip())
                priority_score = max(1, min(10, priority_score))  # Ensure 1-10 range
            except:
                priority_score = 5  # Default fallback
            
            return recommendation, priority_score
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}")
            return f"Failed to generate recommendation: {str(e)}", 5

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
