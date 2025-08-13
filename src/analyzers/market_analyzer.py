import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Perform market analysis for technical projects/features focusing on supplement + subscription/ecommerce markets"""
        
        prompt = f"""
You are a market analyst for CYMBIOTIKA, analyzing the market opportunity for this technical project/feature.

PROJECT TO ANALYZE:
Project Name: {project_name}
Description: {description}

CYMBIOTIKA CONTEXT:
- Premium bioavailable supplement company ($40-100+ products)
- Direct-to-consumer model with subscription options
- Target customers: Health-conscious consumers, 25-55 years, income $75K+
- Current channels: Website, mobile app, customer portal
- Average order value: $80-120
- Monthly active subscribers: Growing D2C business
- Key differentiators: Liposomal delivery, premium ingredients, scientific backing

MARKET ANALYSIS FRAMEWORK:

## 🎯 CUSTOMER IMPACT ANALYSIS
**SUPPLEMENT CUSTOMER PERSPECTIVE:**
- How will this technical feature improve the supplement buying experience?
- Customer pain points in supplement shopping/subscription management
- Expected impact on customer retention and lifetime value
- Relevance to health-conscious, premium supplement customers

**CROSS-INDUSTRY INSIGHTS:**
- How do leading subscription companies (Netflix, Spotify, Dollar Shave Club) handle similar features?
- Best practices from premium ecommerce brands (Glossier, Away, Allbirds)
- Customer experience innovations from D2C leaders (Warby Parker, Casper, Peloton)

## 📊 BUSINESS METRICS IMPACT
**SUPPLEMENT INDUSTRY METRICS:**
- Potential impact on supplement conversion rates (industry avg: 2-4%)
- Expected effect on supplement AOV (current premium range: $80-120)
- Subscription retention improvements (industry benchmark: 85% monthly retention)
- Customer acquisition cost changes for supplement customers

**SUBSCRIPTION/ECOMMERCE BENCHMARKS:**
- Conversion rate improvements seen in subscription businesses
- AOV increases from similar features in premium ecommerce
- Retention metrics from best-performing subscription companies
- Customer lifetime value optimization strategies from D2C leaders

## 🚀 MARKET POSITIONING ADVANTAGE
**SUPPLEMENT MARKET POSITIONING:**
- How this differentiates us in the premium supplement space
- Reinforcement of bioavailability and scientific positioning
- Appeal to affluent health enthusiasts and biohackers
- Premium brand perception enhancement vs mass-market supplements

**ECOMMERCE POSITIONING LEARNINGS:**
- Premium positioning strategies from luxury D2C brands
- Technical sophistication as competitive advantage
- Customer experience differentiation from subscription leaders
- Brand loyalty drivers from successful ecommerce companies

## 📈 GROWTH POTENTIAL ANALYSIS
**SUPPLEMENT MARKET GROWTH:**
- Scalability for growing supplement subscriber base
- Cross-selling opportunities with existing supplement products
- Market expansion to new supplement customer segments
- Premium supplement market trends and growth projections

**SUBSCRIPTION/ECOMMERCE GROWTH INSIGHTS:**
- Growth strategies from successful subscription companies
- Market expansion tactics from D2C leaders
- Customer segment expansion opportunities
- International growth potential based on ecommerce benchmarks

## 💡 MARKET VALIDATION & TRENDS
**SUPPLEMENT INDUSTRY VALIDATION:**
- Similar features in supplement/health industry success stories
- Consumer demand indicators for health and wellness features
- Regulatory considerations and market acceptance
- Timing alignment with supplement market trends

**CROSS-INDUSTRY VALIDATION:**
- Success metrics from comparable ecommerce/subscription features
- Customer adoption patterns from leading D2C companies
- Technology adoption rates in premium consumer markets
- Market readiness based on subscription economy trends

## 🎲 MARKET OPPORTUNITY SIZING
**SUPPLEMENT MARKET OPPORTUNITY:**
- Addressable market size for premium supplement customers
- Revenue potential from improved customer experience
- Market share capture opportunity vs supplement competitors
- Premium segment growth in supplement industry

**SUBSCRIPTION/ECOMMERCE MARKET LEARNINGS:**
- Market size benchmarks from successful subscription companies
- Revenue impact estimates from similar ecommerce innovations
- Customer acquisition and retention value improvements
- Market expansion potential based on D2C success stories

## 📋 STRATEGIC MARKET RECOMMENDATIONS
- How to position this feature for maximum market impact
- Customer communication strategy for supplement audience
- Pricing strategy considerations for premium market
- Launch timing and market entry recommendations
- Marketing channels and customer acquisition strategies

Focus on both SUPPLEMENT INDUSTRY specifics and BEST-IN-CLASS SUBSCRIPTION/ECOMMERCE examples. Provide specific, quantitative insights where possible (conversion rates, revenue impact, customer metrics, etc.).

Analyze this technical project/feature as it relates to enhancing CYMBIOTIKA's position in the premium supplement D2C market while learning from subscription and ecommerce industry leaders.
"""
        
        logger.info("Starting market analysis for technical project")
        result = await self.ai_client.generate_response(prompt, f"Market analysis context for {project_name}")
        logger.info("Market analysis completed")
        
        return result
