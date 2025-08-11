# Notion Project Analyzer

AI-powered project analysis automation for Notion databases.

## Features

- 🔍 **Market Analysis**: Market size, trends, and opportunities
- 🏢 **Competitive Analysis**: Competitor research and positioning
- ⚙️ **Technical Feasibility**: Technology stack and complexity assessment
- ⚠️ **Risk Assessment**: Comprehensive risk identification and mitigation
- 💰 **Financial Analysis**: Cost estimation and ROI projections
- 🎯 **AI Recommendations**: Overall project scoring and next steps

## Setup

1. **Clone this repository**
2. **Set up Notion integration** (see setup guide)
3. **Configure GitHub secrets**:
   - `NOTION_TOKEN`
   - `NOTION_DATABASE_ID` 
   - `OPENAI_API_KEY`
4. **Create Notion database** with required properties
5. **Test the workflow**

## Usage

### Manual Trigger (Recommended for testing)
1. Go to GitHub Actions tab
2. Select "Analyze Project" workflow
3. Click "Run workflow"
4. Enter the Notion page ID

### Automated Trigger (Production)
Set up Zapier integration to trigger on new database entries.

## Cost

- GitHub Actions: Free (2,000 minutes/month)
- OpenAI API: ~$0.10-0.50 per analysis
- Total: Very low cost for moderate usage

## Support

For issues or questions, please create a GitHub issue.
