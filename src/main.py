#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

# Setup logging
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
    """Main entry point - creates only child pages based on selected analysis types"""
    logger.info("=== 🚀 Starting Selective Cymbiotika Analysis ===")
    
    try:
        # Check environment variables
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
        
        logger.info("All environment variables set ✅")
        
        # Import modules
        logger.info("Importing modules...")
        from utils.notion_client import NotionClient
        from utils.ai_client import AIClient
        from analyzers.market_analyzer import MarketAnalyzer
        from analyzers.competitor_analyzer import CompetitorAnalyzer
        from analyzers.technical_analyzer import TechnicalAnalyzer
        from analyzers.risk_analyzer import RiskAnalyzer
        from analyzers.financial_analyzer import FinancialAnalyzer
        from analyzers.solution_recommendations_analyzer import SolutionRecommendationsAnalyzer
        
        logger.info("All modules imported ✅")
        
        # Initialize clients
        logger.info("Initializing selective clients...")
        notion_client = NotionClient(
            token=notion_token, 
            database_id=notion_db_id,
            parent_page_id=page_id
        )
        ai_client = AIClient(api_key=openai_key)
        
        # Initialize analyzers
        analyzers = {
            'market': MarketAnalyzer(ai_client),
            'competitor': CompetitorAnalyzer(ai_client),
            'technical': TechnicalAnalyzer(ai_client),
            'risk': RiskAnalyzer(ai_client),
            'financial': FinancialAnalyzer(ai_client),
            'solution': SolutionRecommendationsAnalyzer(ai_client)
        }
        
        logger.info("Selective system initialized ✅")
        
        # Run selective analysis (child pages only for selected types)
        analyzer = SelectiveCymbiotikaProjectAnalyzer(notion_client, ai_client, analyzers)
        asyncio.run(analyzer.create_selective_analysis(page_id))
        
        logger.info("=== ✨ Selective Analysis Complete ===")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

class SelectiveCymbiotikaProjectAnalyzer:
    def __init__(self, notion_client, ai_client, analyzers):
        self.notion_client = notion_client
        self.ai_client = ai_client
        self.analyzers = analyzers

    async def get_selected_analysis_types(self, page_id: str) -> List[str]:
        """Get selected analysis types from Notion multi-select property"""
        try:
            logger.info("🔍 Reading selected analysis types...")
            project_data = await self.notion_client.get_page_data(page_id)
            
            # Get the Analysis Types multi-select property
            analysis_types = project_data.get('Analysis Types', [])
            
            if isinstance(analysis_types, list):
                selected = analysis_types
            else:
                # Handle different data formats
                selected = []
            
            logger.info(f"✅ Selected analysis types: {selected}")
            
            if not selected:
                logger.warning("⚠️ No analysis types selected, defaulting to all analyses")
                return ["Market Analysis", "Competitive Analysis", "Risk Analysis", 
                       "Technical Feasibility", "Financial Overview", "Solution Recommendations"]
            
            return selected
            
        except Exception as e:
            logger.error(f"❌ Error reading analysis types: {str(e)}")
            logger.info("🔄 Falling back to all analysis types")
            return ["Market Analysis", "Competitive Analysis", "Risk Analysis", 
                   "Technical Feasibility", "Financial Overview", "Solution Recommendations"]

    async def create_selective_analysis(self, page_id: str) -> Dict[str, Any]:
        """Create analysis reports only for selected types"""
        try:
            logger.info(f"🎯 Starting selective analysis for: {page_id}")
            
            # Get selected analysis types first
            selected_types = await self.get_selected_analysis_types(page_id)
            logger.info(f"📊 Will run {len(selected_types)} analysis types")
            
            # Update status to analyzing
            logger.info("📝 Updating Analysis Status to 'Analyzing'...")
            await self.notion_client.update_page_status(page_id, "Analyzing")
            logger.info("✅ Analysis Status: Analyzing")
            
            # Get project data
            logger.info("📋 Retrieving project information...")
            project_data = await self.notion_client.get_page_data(page_id)
            project_name = project_data.get('Project Name', 'Unknown Project')
            description = project_data.get('Description', 'No description available')
            
            logger.info(f"✅ Project Name: '{project_name}'")
            logger.info(f"✅ Description Length: {len(description)} characters")
            
            # Run only selected analyses
            analysis_results = []
            
            # Market Analysis (if selected)
            if "Market Analysis" in selected_types:
                logger.info("📊 Creating Market Analysis child page...")
                try:
                    market_analysis = await self.analyzers['market'].analyze(project_name, description)
                    
                    market_page_id = await self.notion_client.create_beautiful_analysis_report(
                        project_name=project_name,
                        analysis_type="Market Analysis",
                        analysis_content=market_analysis,
                        parent_page_id=page_id
                    )
                    
                    analysis_results.append("Market Analysis")
                    logger.info("✅ Beautiful Market Analysis child page created")
                    
                except Exception as e:
                    logger.error(f"❌ Market analysis failed: {str(e)}")
            
            # Competitive Analysis (if selected)
            if "Competitive Analysis" in selected_types:
                logger.info("🏢 Creating Competitive Analysis child page...")
                try:
                    competitive_analysis = await self.analyzers['competitor'].analyze(project_name, description)
                    
                    competitive_page_id = await self.notion_client.create_beautiful_analysis_report(
                        project_name=project_name,
                        analysis_type="Competitive Analysis",
                        analysis_content=competitive_analysis,
                        parent_page_id=page_id
                    )
                    
                    analysis_results.append("Competitive Analysis")
                    logger.info("✅ Beautiful Competitive Analysis child page created")
                    
                except Exception as e:
                    logger.error(f"❌ Competitive analysis failed: {str(e)}")
            
            # Risk Analysis (if selected)
            if "Risk Analysis" in selected_types:
                logger.info("⚠️ Creating Risk Assessment child page...")
                try:
                    risk_analysis = await self.analyzers['risk'].analyze(project_name, description)
                    
                    risk_page_id = await self.notion_client.create_beautiful_analysis_report(
                        project_name=project_name,
                        analysis_type="Risk Assessment", 
                        analysis_content=risk_analysis,
                        parent_page_id=page_id
                    )
                    
                    analysis_results.append("Risk Assessment")
                    logger.info("✅ Beautiful Risk Assessment child page created")
                    
                except Exception as e:
                    logger.error(f"❌ Risk analysis failed: {str(e)}")
            
            # Technical Feasibility (if selected)
            if "Technical Feasibility" in selected_types:
                logger.info("⚙️ Creating Technical Feasibility child page...")
                try:
                    technical_analysis = await self.analyzers['technical'].analyze(project_name, description)
                    
                    technical_page_id = await self.notion_client.create_beautiful_analysis_report(
                        project_name=project_name,
                        analysis_type="Technical Feasibility",
                        analysis_content=technical_analysis,
                        parent_page_id=page_id
                    )
                    
                    analysis_results.append("Technical Feasibility")
                    logger.info("✅ Beautiful Technical Feasibility child page created")
                    
                except Exception as e:
                    logger.error(f"❌ Technical analysis failed: {str(e)}")
            
            # Financial Overview (if selected)
            if "Financial Overview" in selected_types:
                logger.info("💰 Creating Financial Overview child page...")
                try:
                    financial_analysis = await self.analyzers['financial'].analyze(project_name, description)
                    
                    financial_page_id = await self.notion_client.create_beautiful_analysis_report(
                        project_name=project_name,
                        analysis_type="Financial Overview",
                        analysis_content=financial_analysis,
                        parent_page_id=page_id
                    )
                    
                    analysis_results.append("Financial Overview")
                    logger.info("✅ Beautiful Financial Overview child page created")
                    
                except Exception as e:
                    logger.error(f"❌ Financial analysis failed: {str(e)}")
            
            # Solution Recommendations (if selected)
            if "Solution Recommendations" in selected_types:
                logger.info("💡 Creating Solution Recommendations child page...")
                try:
                    solution_analysis = await self.analyzers['solution'].analyze(project_name, description)
                    
                    solution_page_id = await self.notion_client.create_beautiful_analysis_report(
                        project_name=project_name,
                        analysis_type="Solution Recommendations",
                        analysis_content=solution_analysis,
                        parent_page_id=page_id
                    )
                    
                    analysis_results.append("Solution Recommendations")
                    logger.info("✅ Beautiful Solution Recommendations child page created")
                    
                except Exception as e:
                    logger.error(f"❌ Solution recommendations analysis failed: {str(e)}")
            
            # Check if any analyses were completed successfully
            if not analysis_results:
                logger.error("❌ No analyses completed successfully")
                await self.notion_client.update_page_status(page_id, "Error")
                logger.info("Status updated to 'Error' - No successful analyses")
                return {
                    'project_name': project_name,
                    'selected_types': selected_types,
                    'analysis_results': analysis_results,
                    'total_reports': len(analysis_results),
                    'status': 'Error'
                }
            
            # Generate executive AI recommendation
            logger.info("🎯 Generating Executive AI Recommendation...")
            try:
                recommendation = await self._generate_executive_recommendation(
                    project_name, description, analysis_results, selected_types
                )
                logger.info("✅ Executive AI Recommendation generated")
            except Exception as e:
                logger.error(f"❌ AI Recommendation failed: {str(e)}")
                recommendation = f"Analysis complete. {len(analysis_results)} detailed reports created as child pages."
            
            # Update analysis date and AI recommendation
            logger.info("📅 Updating Analysis Date and AI Recommendation...")
            try:
                await self.notion_client.update_analysis_completion(page_id, recommendation)
            except Exception as e:
                logger.error(f"❌ Failed to update analysis completion: {str(e)}")
                # Continue to status update even if this fails
            
            # Update final status
            logger.info("✅ Updating Analysis Status to 'Complete'...")
            try:
                await self.notion_client.update_page_status(page_id, "Complete")
                logger.info("✅ Analysis Status: Complete")
            except Exception as e:
                logger.error(f"❌ Failed to update status to Complete: {str(e)}")
                # Don't raise here as analysis was successful
            
            logger.info(f"🎉 Selective analysis complete for: '{project_name}'")
            logger.info(f"📊 Created {len(analysis_results)} beautiful child page reports:")
            for result in analysis_results:
                logger.info(f"   ✨ {result}")
            
            logger.info("🔍 Check the bottom of your project page for child page reports!")
            
            return {
                'project_name': project_name,
                'selected_types': selected_types,
                'analysis_results': analysis_results,
                'total_reports': len(analysis_results),
                'status': 'Complete'
            }
            
        except Exception as e:
            logger.error(f"❌ Selective analysis failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Always try to update status to error when the main analysis fails
            try:
                await self.notion_client.update_page_status(page_id, "Error")
                logger.info("✅ Status updated to 'Error'")
            except Exception as status_error:
                logger.error(f"❌ Failed to update status to Error: {str(status_error)}")
            
            # Re-raise the original exception
            raise

    async def _generate_executive_recommendation(self, project_name: str, description: str, 
                                               analysis_results: list, selected_types: list) -> str:
        """Generate executive summary for AI Recommendation property"""
        try:
            context = f"""
            CYMBIOTIKA PROJECT ANALYSIS SUMMARY
            Project: {project_name}
            Description: {description}
            
            Requested Analyses: {', '.join(selected_types)}
            Completed Analyses: {', '.join(analysis_results)}
            
            This is a premium healthcare supplement company analysis.
            Competitors: Thorne HealthTech, MaryRuth Organics, Pure Encapsulations
            Focus: Bioavailable, premium supplements ($40-100+ price range)
            Team: Mostly junior developers with one senior developer
            """
            
            recommendation = await self.ai_client.generate_response(
                f"""Create a concise executive recommendation for Cymbiotika leadership based on the {len(analysis_results)} completed analysis reports:
                
                ## 🎯 EXECUTIVE SUMMARY
                [2-3 sentences on overall project viability based on completed analyses]
                
                ## 💼 STRATEGIC IMPACT
                - Revenue potential for premium supplement business
                - Competitive positioning vs Thorne/MaryRuth's/Pure Encapsulations  
                - Brand alignment with bioavailability focus
                
                ## 🚀 RECOMMENDATION
                **[GO/NO-GO/CONDITIONAL]** - [Clear rationale based on available analysis]
                
                ## 📊 NEXT STEPS
                - Priority 1: [Most important action]
                - Priority 2: [Second priority]
                
                Note: Base recommendations only on the {len(analysis_results)} completed analyses: {', '.join(analysis_results)}
                Keep it executive-level, strategic, and actionable.""",
                context
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Executive recommendation error: {str(e)}")
            return f"Analysis complete for {project_name}. {len(analysis_results)} comprehensive reports created as child pages. Review detailed analysis for strategic insights."

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
