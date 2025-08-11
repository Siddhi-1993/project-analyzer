import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class CompetitorAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Perform competitive landscape analysis"""
        
        prompt = f"""
        Analyze the competitive landscape for:
        
        Project: {project_name}
        Description: {description}
        
        Provide comprehensive competitive analysis covering:
        
        1. **Direct Competitors**
           - Identify 3-5 main direct competitors
           - Their market position and market share
           - Key features and offerings
        
        2. **Indirect Competitors**
           - Alternative solutions customers might choose
           - Substitute products or services
        
        3. **Competitive Advantages & Gaps**
           - Unique value propositions of competitors
           - Market gaps and opportunities
           - Areas where this project could differentiate
        
        4. **Pricing Analysis**
           - Competitor pricing strategies
           - Price points and models
           - Value perception in the market
        
        5. **SWOT vs Competitors**
           - Strengths this project can leverage
           - Weaknesses to address
           - Threats from competition
           - Opportunities for differentiation
        
        Focus on actionable insights for competitive positioning.
        """
        
        logger.info("Starting competitive analysis")
        result = await self.ai_client.generate_response(prompt)
        logger.info("Competitive analysis completed")
        
        return result
