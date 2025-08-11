#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

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
    """Main entry point for Cymbiotika analysis"""
    logger.info("=== Starting Cymbiotika Analysis ===")
    
    try:
        # Check environment variables
        logger.info("Checking environment variables...")
        page_id = os.getenv('PAGE_ID')
        notion_token = os.getenv('NOTION_TOKEN')
        notion_db_id = os.getenv('NOTION_DATABASE_ID')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        logger.info(f"PAGE_ID: {'Set' if page_id else 'Missing'}")
        logger.info(f"NOTION_TOKEN: {'Set' if notion_token else 'Missing'}")
        logger.info(f"NOTION_DATABASE_ID: {'Set' if notion_db_id else 'Missing'}")
        logger.info(f"OPENAI_API_KEY: {'Set' if openai_key else 'Missing'}")
        
        if not all([page_id, notion_token, notion_db_id, openai_key]):
            logger.error("Missing required environment variables")
            return 1
        
        logger.info("All environment variables set")
        
        # Import modules
        logger.info("Importing modules...")
        from utils.notion_client import NotionClient
        from utils.ai_client import AIClient
        from analyzers.market_analyzer import MarketAnalyzer
        from analyzers.competitor_analyzer import CompetitorAnalyzer
        from analyzers.technical_analyzer import TechnicalAnalyzer
        from analyzers.risk_analyzer import RiskAnalyzer
        from analyzers.financial_analyzer import FinancialAnalyzer
        
        logger.info("All modules imported")
        
        # Initialize clients
        logger.info("Initializing clients...")
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
            'financial': FinancialAnalyzer(ai_client)
        }
        
        logger.info("Clients and analyzers initialized")
        
        # Run analysis
        analyzer = CymbiotikaProjectAnalyzer(notion_client, ai_client, analyzers)
        asyncio.run(analyzer.create_analysis(page_id))
        
        logger.info("=== Analysis Complete ===")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

class CymbiotikaProjectAnalyzer:
    def __init__(self, notion_client, ai_client, analyzers):
        self.notion_client = notion_client
        self.ai_client = ai_client
        self.analyzers = analyzers

    async def create_analysis(self, page_id: str) -> Dict[str, Any]:
        """Create analysis reports"""
        try:
            logger.info(f"Starting analysis for project: {page_id}")
            
            # Update status
            await self.notion_client.update_page_status(page_id, "Analyzing")
            logger.info("Status updated to Analyzing")
            
            # Get project data
            project_data = await self.notion_client.get_page_data(page_id)
            project_name = project_data.get('Project Name', 'Unknown Project')
            description = project_data.get('Description', 'No description available')
            
            logger.info(f"Project: {project_name}")
            logger.info(f"Description: {description[:100]}...")
            
            # Run analyses and create reports
            results = {}
            report_links = {}
            
            # Market Analysis
            logger.info("Running Market Analysis...")
            try:
                market_analysis = await self.analyzers['market'].analyze(project_name, description)
                results['Market Analysis'] = market_analysis
                
                # Create beautiful report page
                market_report_id = await self.notion_client.create_beautiful_analysis_report(
                    project_name=project_name,
                    analysis_type="Market Analysis",
                    analysis_content=market_analysis,
                    parent_page_id=page_id
                )
                report_links['Market Analysis'] = market_report_id
                logger.info("Market Analysis report created")
            except Exception as e:
                logger.error(f"Market analysis failed: {str(e)}")
                results['Market Analysis'] = f"Analysis failed: {str(e)}"
            
            # Competitive Analysis
            logger.info("Running Competitive Analysis...")
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
                logger.info("Competitive Analysis report created")
            except Exception as e:
                logger.error(f"Competitive analysis failed: {str(e)}")
                results['Competitive Analysis'] = f"Analysis failed: {str(e)}"
            
            # Risk Assessment
            logger.info("Running Risk Assessment...")
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
                logger.info("Risk Assessment report created")
            except Exception as e:
                logger.error(f"Risk analysis failed: {str(e)}")
                results['Risk Assessment'] = f"Analysis failed: {str(e)}"
            
            # Technical Feasibility
            logger.info("Running Technical Analysis...")
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
                logger.info("Technical Feasibility report created")
            except Exception as e:
                logger.error(f"Technical analysis failed: {str(e)}")
                results['Technical Feasibility'] = f"Analysis failed: {str(e)}"
            
            # Financial Overview
            logger.info("Running Financial Analysis...")
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
                logger.info("Financial Overview report created")
            except Exception as e:
                logger.error(f"Financial analysis failed: {str(e)}")
                results['Financial Overview'] = f"Analysis failed: {str(e)}"
            
            # Generate executive summary
            logger.info("Generating Executive Summary...")
            try:
                recommendation, priority_score = await self._generate_summary(
                    project_name, description, results
                )
                results['AI Recommendation'] = recommendation
                results['Priority Score'] = priority_score
                results['Analysis Date'] = datetime.now().isoformat()
                logger.info(f"Executive summary generated (Priority: {priority_score}/10)")
            except Exception as e:
                logger.error(f"Summary failed: {str(e)}")
                results['AI Recommendation'] = f"Summary failed: {str(e)}"
                results['Priority Score'] = 5
                results['Analysis Date'] = datetime.now().isoformat()
            
            # Update project page
            logger.info("Updating project page...")
            await self.notion_client.update_project_with_report_links(page_id, report_links, results)
            logger.info("Project page updated with report links")
            
            # Complete
            await self.notion_client.update_page_status(page_id, "Complete")
            logger.info("Status updated to Complete")
            
            logger.info(f"Analysis complete for: {project_name}")
            logger.info(f"Created {len(report_links)} beautiful analysis reports")
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            try:
                await self.notion_client.update_page_status(page_id, "Error")
            except:
                pass
            
            raise

    async def _generate_summary(self, name: str, description: str, analyses: Dict[str, str]) -> tuple[str, int]:
        """Generate executive summary"""
        try:
            combined = f"""
            Project: {name}
            Description: {description}
            
            Market: {analyses.get('Market Analysis', '')[:300]}
            Competitive: {analyses.get('Competitive Analysis', '')[:300]}
            Risk: {analyses.get('Risk Assessment', '')[:300]}
            Technical: {analyses.get('Technical Feasibility', '')[:300]}
            Financial: {analyses.get('Financial Overview', '')[:300]}
            """
            
            summary = await self.ai_client.generate_response(
                """Create executive summary for Cymbiotika:
                
                ## EXECUTIVE SUMMARY
                [2-3 sentences on project viability]
                
                ## STRATEGIC IMPACT
                - Revenue potential for premium supplements
                - Competitive advantage vs Thorne/MaryRuth's/Pure Encapsulations
                - Brand alignment with bioavailability focus
                
                ## RECOMMENDATION
                [GO/NO-GO/CONDITIONAL] - [Clear rationale]
                
                Keep it executive-level and actionable.""",
                combined
            )
            
            priority_response = await self.ai_client.generate_response(
                """Rate project priority for Cymbiotika (1-10):
                Consider premium supplement market, competitive position, technical feasibility, ROI.
                Respond with just the number.""",
                combined
            )
            
            try:
                priority = int(priority_response.strip())
                priority = max(1, min(10, priority))
            except:
                priority = 6
            
            return summary, priority
            
        except Exception as e:
            logger.error(f"Summary error: {str(e)}")
            return f"Summary failed: {str(e)}", 5

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
