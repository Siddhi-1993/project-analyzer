import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Comprehensive risk assessment customized for Cymbiotika's healthcare supplement business"""
        
        prompt = f"""
        You are analyzing risks for Cymbiotika, a premium ecommerce healthcare supplement company. Consider the unique challenges of the supplement industry, FDA regulations, and D2C ecommerce.

        Project to Analyze:
        Project Name: {project_name}
        Description: {description}

        Identify and analyze risks across these categories:

        1. **Regulatory & Compliance Risks**
           - FDA regulations and health claim restrictions
           - State-specific supplement regulations
           - International shipping compliance (Canada, EU, etc.)
           - Labeling requirements and accuracy
           - Third-party testing and quality assurance needs
           - cGMP manufacturing compliance
           - Risk Level: High/Medium/Low + Mitigation strategies

        2. **Supply Chain & Manufacturing Risks**
           - Raw material sourcing reliability and quality
           - Supplier dependency (single vs. multiple sources)
           - Manufacturing capacity constraints
           - Quality control failures and batch recalls
           - Ingredient cost volatility
           - Lead times and inventory management
           - Risk Level: High/Medium/Low + Mitigation strategies

        3. **Market & Consumer Risks**
           - Consumer safety concerns or adverse reactions
           - Negative reviews impacting brand reputation
           - Market saturation in supplement category
           - Changes in consumer wellness trends
           - Competition from Thorne, MaryRuth's, Pure Encapsulations
           - Economic downturn affecting premium supplement purchases
           - Risk Level: High/Medium/Low + Mitigation strategies

        4. **Ecommerce & Technology Risks**
           - Website downtime during peak sales periods
           - Cybersecurity and customer data protection
           - Payment processing issues
           - Subscription billing and churn management
           - Mobile optimization for supplement purchases
           - Integration with existing Cymbiotika systems
           - Junior developer team handling complex ecommerce features
           - Risk Level: High/Medium/Low + Mitigation strategies

        5. **Financial & Business Model Risks**
           - High customer acquisition costs in supplement space
           - Subscription model churn and lifetime value erosion
           - Inventory carrying costs for supplements
           - Return/refund rates for health products
           - Cash flow impact of seasonal sales patterns
           - Investment recovery timeline (12-24 months typical)
           - Risk Level: High/Medium/Low + Mitigation strategies

        6. **Brand & Reputation Risks**
           - Product efficacy claims and customer expectations
           - Social media backlash or negative publicity
           - Influencer partnership risks and authenticity concerns
           - Competition with established clinical brands (Thorne)
           - Premium pricing justification challenges
           - Risk Level: High/Medium/Low + Mitigation strategies

        7. **Operational Risks**
           - Team capacity with mostly junior developers
           - Single senior developer dependency
           - Customer service scaling for health product inquiries
           - Fulfillment and shipping accuracy
           - International expansion complexity
           - Risk Level: High/Medium/Low + Mitigation strategies

        For each risk category, provide:
        - Specific risk scenarios for this project
        - Probability assessment (High/Medium/Low)
        - Impact severity (High/Medium/Low)
        - Detailed mitigation strategies
        - Contingency plans
        - Monitoring and early warning indicators

        Prioritize risks based on Cymbiotika's business model and the supplement industry's unique challenges. Focus on actionable risk management strategies.
        """
        
        logger.info("Starting Cymbiotika-specific risk analysis")
        result = await self.ai_client.generate_response(prompt)
        logger.info("Risk analysis completed")
        
        return result
