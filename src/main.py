#!/usr/bin/env python3

import os
import sys
import logging

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
    logger.info("=== MINIMAL TEST - Starting ===")
    
    try:
        # Check environment variables
        page_id = os.getenv('PAGE_ID')
        logger.info(f"PAGE_ID: {page_id}")
        
        notion_token = os.getenv('NOTION_TOKEN')
        logger.info(f"NOTION_TOKEN: {'Set' if notion_token else 'Missing'}")
        
        notion_db_id = os.getenv('NOTION_DATABASE_ID')
        logger.info(f"NOTION_DATABASE_ID: {'Set' if notion_db_id else 'Missing'}")
        
        openai_key = os.getenv('OPENAI_API_KEY')
        logger.info(f"OPENAI_API_KEY: {'Set' if openai_key else 'Missing'}")
        
        logger.info("=== Environment variables checked ===")
        
        # Test basic imports
        logger.info("Testing basic imports...")
        import asyncio
        logger.info("✅ asyncio imported")
        
        from datetime import datetime
        logger.info("✅ datetime imported")
        
        logger.info("=== Basic imports successful ===")
        
        # Test Notion client import
        logger.info("Testing Notion client import...")
        try:
            from utils.notion_client import NotionClient
            logger.info("✅ NotionClient imported successfully")
        except Exception as e:
            logger.error(f"❌ NotionClient import failed: {str(e)}")
            return 1
        
        # Test AI client import
        logger.info("Testing AI client import...")
        try:
            from utils.ai_client import AIClient
            logger.info("✅ AIClient imported successfully")
        except Exception as e:
            logger.error(f"❌ AIClient import failed: {str(e)}")
            return 1
        
        logger.info("=== All imports successful ===")
        logger.info("=== MINIMAL TEST - Complete ===")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
