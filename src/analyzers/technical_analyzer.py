import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Assess technical feasibility and requirements"""
        
        prompt = f"""
        Conduct technical feasibility analysis for:
        
        Project: {project_name}
        Description: {description}
        
        Analyze the following technical aspects:
        
        1. **Technology Stack Assessment**
           - Recommended technologies and frameworks
           - Infrastructure requirements
           - Third-party integrations needed
        
        2. **Development Complexity**
           - Complexity rating (Low/Medium/High)
           - Key technical challenges
           - Critical technical decisions
        
        3. **Resource Requirements**
           - Team size and skill requirements
           - Development timeline estimation
           - Required expertise and roles
        
        4. **Scalability Considerations**
           - Performance requirements
           - Scaling challenges and solutions
           - Architecture recommendations
        
        5. **Technical Risks**
           - Technology-related risks
           - Dependencies and limitations
           - Mitigation strategies
        
        6. **Implementation Approach**
           - Recommended development phases
           - MVP vs full feature set
           - Testing and deployment strategy
        
        Provide practical, actionable technical guidance.
        """
        
        logger.info("Starting technical analysis")
        result = await self.ai_client.generate_response(prompt)
        logger.info("Technical analysis completed")
        
        return result
