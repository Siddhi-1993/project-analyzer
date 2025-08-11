import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Perform comprehensive market analysis"""
        
        prompt = f"""
        Conduct a thorough market analysis for the following project:
        
        Project Name: {project_name}
        Description: {description}
        
        Provide analysis covering:
        
        1. **Market Size & Opportunity**
           - Total Addressable Market (TAM) estimation
           - Serviceable Available Market (SAM)
           - Market growth trends and projections
        
        2. **Target Market Segmentation**
           - Primary target demographics
           - Customer personas and pain points
           - Market segments with highest potential
        
        3. **Market Timing**
           - Current market readiness
           - Trending factors supporting/hindering adoption
           - Optimal market entry timing
        
        4. **Demand Validation**
           - Evidence of market demand
           - Unmet needs this project addresses
           - Potential barriers to adoption
        
        5. **Revenue Opportunities**
           - Potential revenue streams
           - Pricing strategy considerations
           - Monetization models
        
        Format as a structured analysis with clear sections and actionable insights.
        Keep it professional and data-driven where possible.
        """
        
        logger.info("Starting market analysis")
        result = await self.ai_client.generate_response(prompt)
        logger.info("Market analysis completed")
        
        return result
