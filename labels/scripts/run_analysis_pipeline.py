from segmentation.orchestrator import SegmentationOrchestrator

import logging
import os
from dotenv import load_dotenv

# Load .env file from current directory
load_dotenv()

# Configuration
DB_URL = os.getenv("DB_URL", "postgresql://username:password@localhost:5432/dbname")

logging.basicConfig(level=logging.INFO)

def get_db_config():
    """Get database configuration with validation"""
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError(
            "Database connection string not found. "
            "Please set DB_URL environment variable or update config."
        )
    return db_url

def main():
    try:
        logging.info("Starting neighborhood analysis pipeline")
        
        # Get validated DB config
        db_url = get_db_config()
        
        # Initialize orchestrator
        orchestrator = SegmentationOrchestrator(db_url)
        orchestrator.add("green_spaces")
        
        # Run pipeline
        results = orchestrator.run_pipeline()        
        
        # Generate visualizations
        orchestrator.visualize_results(results)
        
        logging.info("Analysis pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Error in analysis pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()