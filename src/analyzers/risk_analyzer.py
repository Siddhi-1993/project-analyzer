import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Comprehensive risk assessment"""
        
        prompt = f"""
        Perform comprehensive risk analysis for:
        
        Project: {project_name}
        Description: {description}
        
        Identify and analyze risks across these categories:
        
        1. **Market Risks**
           - Market adoption challenges
           - Timing risks
           - Customer demand uncertainty
           - Economic factors
        
        2. **Technical Risks**
           - Technology failures or limitations
           - Development complexity
           - Integration challenges
           - Security vulnerabilities
        
        3. **Operational Risks**
           - Resource availability
           - Team capacity and skills
           - Timeline pressures
           - Process breakdowns
        
        4. **Financial Risks**
           - Budget overruns
           - Revenue shortfalls
           - Funding challenges
           - ROI uncertainty
        
        5. **Strategic Risks**
           - Competitive responses
           - Strategic fit with goals
           - Opportunity costs
           - Reputation impacts
        
        For each risk category, provide:
        - Risk probability (Low/Medium/High)
        - Impact severity (Low/Medium/High)
        - Mitigation strategies
        - Contingency plans
        
        Prioritize risks and provide overall risk assessment.
        """
        
        logger.info("Starting risk analysis")
        result = await self.ai_client.generate_response(prompt)
        logger.info("Risk analysis completed")
        
        return result
