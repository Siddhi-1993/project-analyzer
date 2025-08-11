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
    """Main entry point for beautiful Cymbiotika reports"""
    logger.info("=== 🎨 Starting Cymbiotika Beautiful Report Generator ===")
    
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
        
        logger.info("All environment variables are set ✅")
        
        # Import modules
        logger.info("Importing modules...")
        try:
            from utils.notion_client import NotionClient
            logger.info("✅ Beautiful NotionClient imported")
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
            logger.info("✅ All Cymbiotika analyzers imported")
        except Exception as e:
            logger.error(f"❌ Failed to import analyzers: {str(e)}")
            return 1
        
        # Initialize clients
        logger.info("Initializing NotionClient for beautiful reports...")
        try:
            # Use the project page as parent for reports (no separate database needed)
            notion_client = NotionClient(
                token=notion_token, 
                database_id=notion_db_id,
                parent_page_id=page_id  # Reports will be created as child pages
            )
            logger.info("✅ NotionClient initialized for beautiful reports")
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
        logger.info("Initializing Cymbiotika analyzers...")
        try:
            analyzers = {
                'market': MarketAnalyzer(ai_client),
                'competitor': CompetitorAnalyzer(ai_client),
                'technical': TechnicalAnalyzer(ai_client),
                'risk': RiskAnalyzer(ai_client),
                'financial': FinancialAnalyzer(ai_client)
            }
            logger.info("✅ Cymbiotika analyzers initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize analyzers: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 1
        
        # Run beautiful report generation
        logger.info("🎨 Starting beautiful report generation...")
        analyzer = BeautifulCymbiotikaPr​ojectAnalyzer(notion_client, ai_client, analyzers)
        asyncio.run(analyzer.create_beautiful_analysis(page_id))
        
        logger.info("=== 🎉 Beautiful Cymbiotika Reports Complete ===")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in main: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

class BeautifulCymbiotikaPr​ojectAnalyzer:
    def __init__(self, notion_client, ai_client, analyzers):
        self.notion_client = notion_client
        self.ai_client = ai_client
        self.analyzers = analyzers

    async def create_beautiful_analysis(self, page_id: str) -> Dict[str, Any]:
        """Create beautiful analysis reports with rich formatting"""
        try:
            logger.info(f"🎨 Starting beautiful Cymbiotika analysis for project: {page_id}")
            
            # Update status
            logger.info("📝 Updating project status to 'Analyzing'...")
            await self.notion_client.update_page_status(page_id, "Analyzing")
            logger.info("✅ Status updated to Analyzing")
            
            # Get project data
            logger.info("📋 Fetching project data from Notion...")
            project_data = await self.notion_client.get_page_data(page_id)
            project_name = project_data.get('Project Name', 'Unknown Project')
            description = project_data.get('Description', 'No description available')
            
            logger.info(f"✅ Project data retrieved:")
            logger.info(f"   🏷️ Project: {project_name}")
            logger.info(f"   📖 Description: {description[:100]}...")
            
            # Generate analyses and create beautiful reports
            results = {}
            report_links = {}
            
            # 📊 Market Analysis Report
            logger.info("📊 Creating beautiful Market Analysis report...")
            try:
                market_analysis = await self.analyzers['market'].analyze(project_name, description)
                results['Market Analysis'] = market_analysis
                
                market_report_id = await self.notion_client.create_beautiful_analysis_report(
                    project_name=project_name,
                    analysis_type="Market Analysis",
                    analysis_content=market_analysis,
                    parent_page_id=page_id
                )
                report_links['Market Analysis'] = market_report_id
                logger.info("✅ Beautiful Market Analysis report created with tables & charts")
            except Exception as e:
                logger.error(f"❌ Market analysis failed: {str(e)}")
                results['Market Analysis'] = f"Analysis failed: {str(e)}"
            
            # 🏢 Competitive Analysis Report
            logger.info("🏢 Creating beautiful Competitive Analysis report...")
            try:
                competitive_analysis = await self.analyzers['competitor'].analyze(project_name, description)
                results['Competitive Analysis'] = competitive_analysis
                
                competitive_report_id = await self.notion_client.create_beautiful_analysis_report(
                    project_name=project_name,
                    analysis_type="Competitive Analysis",
                    analysis_content=competitive_analysis,
                    parent_page_id=page_id
                )
                report_links['Competitive Analysis'] = competitive_report_id
                logger.info("✅ Beautiful Competitive Analysis report created with competitor comparison table")
            except Exception as e:
                logger.error(f"❌ Competitive analysis failed: {str(e)}")
                results['Competitive Analysis'] = f"Analysis failed: {str(e)}"
            
            # ⚠️ Risk Assessment Report
            logger.info("⚠️ Creating beautiful Risk Assessment report...")
            try:
                risk_analysis = await self.analyzers['risk'].analyze(project_name, description)
                results['Risk Assessment'] = risk_analysis
                
                risk_report_id = await self.notion_client.create_beautiful_analysis_report(
                    project_name=project_name,
                    analysis_type="Risk Assessment",
                    analysis_content=risk_analysis,
                    parent_page_id=page_id
                )
                report_links['Risk Assessment'] = risk_report_id
                logger.info("✅ Beautiful Risk Assessment report created with risk matrix")
            except Exception as e:
                logger.error(f"❌ Risk analysis failed: {str(e)}")
                results['Risk Assessment'] = f"Analysis failed: {str(e)}"
            
            # ⚙️ Technical Feasibility Report
            logger.info("⚙️ Creating beautiful Technical Feasibility report...")
            try:
                technical_analysis = await self.analyzers['technical'].analyze(project_name, description)
                results['Technical Feasibility'] = technical_analysis
                
                technical_report_id = await self.notion_client.create_beautiful_analysis_report(
                    project_name=project_name,
                    analysis_type="Technical Feasibility",
                    analysis_content=technical_analysis,
                    parent_page_id=page_id
                )
                report_links['Technical Feasibility'] = technical_report_id
                logger.info("✅ Beautiful Technical Feasibility report created with development timeline")
            except Exception as e:
                logger.error(f"❌ Technical analysis failed: {str(e)}")
                results['Technical Feasibility'] = f"Analysis failed: {str(e)}"
            
            # 💰 Financial Overview Report
            logger.info("💰 Creating beautiful Financial Overview report...")
            try:
                financial_analysis = await self.analyzers['financial'].analyze(project_name, description)
                results['Financial Overview'] = financial_analysis
                
                financial_report_id = await self.notion_client.create_beautiful_analysis_report(
                    project_name=project_name,
                    analysis_type="Financial Overview",
                    analysis_content=financial_analysis,
                    parent_page_id=page_id
                )
                report_links['Financial Overview'] = financial_report_id
                logger.info("✅ Beautiful Financial Overview report created with projection tables")
            except Exception as e:
                logger.error(f"❌ Financial analysis failed: {str(e)}")
                results['Financial Overview'] = f"Analysis failed: {str(e)}"
            
            # 🎯 Generate Cymbiotika Executive Summary
            logger.info("🎯 Generating executive recommendation...")
            try:
                recommendation, priority_score = await self._generate_executive_summary(
                    project_name, description, results
                )
                results['AI Recommendation'] = recommendation
                results['Priority Score'] = priority_score
                results['Analysis Date'] = datetime.now().isoformat()
                logger.info(f"✅ Executive summary generated (Priority: {priority_score}/10)")
            except Exception as e:
                logger.error(f"❌ Executive summary failed: {str(e)}")
                results['AI Recommendation'] = f"Summary failed: {str(e)}"
                results['Priority Score'] = 5
                results['Analysis Date'] = datetime.now().isoformat()
            
            # 📝 Update project with beautiful report links
            logger.info("📝 Updating project page with links to beautiful reports...")
            await self.notion_client.update_project_with_report_links(page_id, report_links, results)
            logger.info("✅ Project updated with links to beautiful analysis reports")
            
            # ✅ Complete
            logger.info("✅ Updating project status to 'Complete'...")
            await self.notion_client.update_page_status(page_id, "Complete")
            logger.info("✅ Status updated to Complete")
            
            logger.info(f"🎉 Beautiful analysis complete for: {project_name}")
            logger.info(f"📊 Created {len(report_links)} stunning analysis reports with:")
            logger.info(f"   📈 Tables and charts")
            logger.info(f"   🎨 Rich formatting with colors and emojis")
            logger.info(f"   📋 Structured layouts")
            logger.info(f"   💡 Executive callouts and insights")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Beautiful analysis failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            try:
                await self.notion_client.update_page_status(page_id, "Error")
                logger.info("Status updated to 'Error'")
            except:
                logger.error("Failed to update status to Error")
            
            raise

    async def _generate_executive_summary(self, name: str, description: str, analyses: Dict[str, str]) -> tuple[str, int]:
        """Generate executive summary for Cymbiotika leadership"""
        try:
            combined_analysis = f"""
            CYMBIOTIKA EXECUTIVE ANALYSIS
            Project: {name}
            Description: {description}
            
            Market Analysis Summary: {analyses.get('Market Analysis', '')[:500]}...
            Competitive Position Summary: {analyses.get('Competitive Analysis', '')[:500]}...
            Risk Profile Summary: {analyses.get('Risk Assessment', '')[:500]}...
            Technical Assessment Summary: {analyses.get('Technical Feasibility', '')[:500]}...
            Financial Outlook Summary: {analyses.get('Financial Overview', '')[:500]}...
            """
            
            summary = await self.ai_client.generate_response(
                """Create an executive summary for Cymbiotika leadership. Format as:
                
                ## 🎯 EXECUTIVE SUMMARY
                [2-3 sentences on overall project viability]
                
                ## 💼 STRATEGIC IMPACT
                - Revenue potential for premium supplement business
                - Competitive advantage vs Thorne/MaryRuth's/Pure Encapsulations
                - Brand alignment with Cymbiotika's bioavailability focus
                
                ## ⚡ KEY INSIGHTS
                - Top market opportunity
                - Major competitive differentiator  
                - Primary risk to mitigate
                
                ## 🚀 RECOMMENDATION
                **[GO/NO-GO/CONDITIONAL]** - [Clear rationale]
                
                ## 📊 INVESTMENT SUMMARY
                - Estimated investment: [Range]
                - Timeline to revenue: [Months]
                - Expected ROI: [Projection]
                
                Keep it executive-level: strategic, concise, actionable.""",
                combined_analysis
            )
            
            # Priority score for Cymbiotika context
            priority_response = await self.ai_client.generate_response(
                """Rate this project's strategic priority for Cymbiotika (1-10):
                
                Consider:
                - Premium supplement market opportunity ($40-100+ products)
                - Competitive positioning vs major players
                - Technical feasibility for junior developer team
                - Healthcare supplement regulatory environment
                - ROI potential for D2C business model
                
                10 = Strategic imperative, exceptional opportunity
                7-9 = High priority, strong business case
                4-6 = Medium priority, some challenges
                1-3 = Low priority, significant concerns
                
                Just respond with the number (1-10).""",
                combined_analysis
            )
            
            try:
                priority = int(priority_response.strip())
                priority = max(1, min(10, priority))
            except:
                priority = 6  # Default for supplement projects
            
            return summary, priority
            
        except Exception as e:
            logger.error(f"Executive summary error: {str(e)}")
            return f"Executive summary failed: {str(e)}", 5

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
