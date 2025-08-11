import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Financial analysis and projections"""
        
        prompt = f"""
        Conduct financial analysis for:
        
        Project: {project_name}
        Description: {description}
        
        Provide financial assessment covering:
        
        1. **Cost Analysis**
           - Development costs (one-time)
           - Operational costs (ongoing)
           - Infrastructure and technology costs
           - Personnel costs
           - Marketing and sales costs
        
        2. **Revenue Projections**
           - Potential revenue streams
           - Revenue model recommendations
           - Market size-based revenue estimates
           - Pricing strategy suggestions
        
        3. **Financial Metrics**
           - Break-even analysis timeline
           - Return on Investment (ROI) projections
           - Payback period estimation
           - Net Present Value considerations
        
        4. **Funding Requirements**
           - Initial investment needed
           - Working capital requirements
           - Funding milestones
           - Potential funding sources
        
        5. **Financial Risks & Sensitivity**
           - Key financial assumptions
           - Sensitivity to market changes
           - Worst-case and best-case scenarios
           - Financial risk mitigation
        
        6. **Business Model Validation**
           - Revenue model feasibility
           - Unit economics analysis
           - Scalability of financial model
           - Monetization timeline
        
        Provide realistic estimates and ranges where appropriate.
        Focus on actionable financial insights.
        """
        
        logger.info("Starting financial analysis")
        result = await self.ai_client.generate_response(prompt)
        logger.info("Financial analysis completed")
        
        return result
