import logging
from utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def analyze(self, project_name: str, description: str) -> str:
        """Project-specific risk assessment for technical features/projects at Cymbiotika"""
        
        prompt = f"""
You are a risk analyst evaluating the specific risks of this technical project for CYMBIOTIKA.

PROJECT TO ANALYZE:
Project Name: {project_name}
Description: {description}

CYMBIOTIKA CONTEXT:
- Premium supplement company with D2C ecommerce model
- Tech Stack: JavaScript/React frontend, Python backend, PostgreSQL, Shopify, AWS/Heroku
- Team: Mostly junior developers + 1 senior developer
- Business: $40-100+ premium supplements, subscription model

ANALYZE PROJECT-SPECIFIC RISKS:

## 🎯 PROJECT IMPLEMENTATION RISKS
**TECHNICAL EXECUTION RISKS:**
- What could go wrong during development of THIS specific project?
- Code complexity vs. junior developer capabilities
- Integration challenges with existing Shopify/React/Python systems
- Specific technical dependencies and failure points
- Database schema changes or PostgreSQL performance impacts
- AWS/Heroku deployment and scaling risks for this feature

**TIMELINE & RESOURCE RISKS:**
- Senior developer bottleneck for this project's complex parts
- Junior developer skill gaps for specific technical requirements
- Realistic development timeline risks and delays
- Testing and QA challenges specific to this feature
- Rollback complexity if this project fails

## ⚡ BUSINESS IMPACT RISKS
**CUSTOMER EXPERIENCE RISKS:**
- How could this specific project negatively impact supplement customers?
- User experience failures and customer confusion scenarios
- Impact on subscription retention if feature doesn't work properly
- Customer support burden increase from this specific feature

**REVENUE & CONVERSION RISKS:**
- Could this project hurt conversion rates or AOV?
- Subscription churn risks from poor implementation
- Impact on existing customer workflows and satisfaction
- Competition risks if project delays give competitors advantage

## 🔧 OPERATIONAL RISKS
**SYSTEM INTEGRATION RISKS:**
- Breaking existing Shopify functionality
- Conflicts with current React portal or Vue.js pages
- PostgreSQL database performance degradation
- Impact on existing Python backend services
- AWS/Heroku infrastructure strain or failures

**MAINTENANCE & SUPPORT RISKS:**
- Long-term maintenance burden with mostly junior team
- Documentation gaps leading to future problems
- Security vulnerabilities specific to this implementation
- Performance monitoring and optimization requirements

## 📊 PROJECT-SPECIFIC RISK SCENARIOS
**WORST-CASE SCENARIOS FOR THIS PROJECT:**
- What happens if this specific feature completely fails?
- Customer impact of bugs or poor performance in this feature
- Business continuity if this project needs to be rolled back
- Data integrity risks specific to this implementation

**MODERATE RISK SCENARIOS:**
- Partial feature failures and their specific impacts
- Performance issues under load for this feature
- Integration problems with specific Cymbiotika systems
- User adoption challenges for this particular feature

## 🛡️ MITIGATION STRATEGIES
**PROJECT-SPECIFIC MITIGATIONS:**
- Technical safeguards and fallback plans for this project
- Testing strategies appropriate for this feature's complexity
- Gradual rollout plan to minimize risk exposure
- Monitoring and alerting specific to this project's success metrics

**TEAM & RESOURCE MITIGATIONS:**
- Senior developer involvement strategy for critical decisions
- Junior developer mentorship and code review processes
- External expertise requirements (if any) for this specific project
- Training or skill development needed for this implementation

## ⚠️ RISK PRIORITY MATRIX
For each identified risk, provide:
- **Probability**: High/Medium/Low (specific to this project)
- **Impact**: High/Medium/Low (on Cymbiotika's business)
- **Priority**: Critical/Important/Monitor
- **Specific Actions**: Concrete steps to mitigate this exact risk

## 🎯 PROJECT SUCCESS RISK FACTORS
**CRITICAL SUCCESS FACTORS:**
- What must go right for this specific project to succeed?
- Key dependencies and single points of failure
- Success metrics and early warning indicators
- Rollback triggers and criteria

Focus entirely on risks specific to THIS PROJECT, not generic business risks. Analyze concrete scenarios, technical challenges, and business impacts related to implementing this exact feature/project at Cymbiotika.

Provide actionable, project-specific risk management recommendations.
"""
        
        logger.info("Starting project-specific risk analysis")
        result = await self.ai_client.generate_response(prompt, f"Risk analysis context for {project_name}")
        logger.info("Project-specific risk analysis completed")
        
        return result
