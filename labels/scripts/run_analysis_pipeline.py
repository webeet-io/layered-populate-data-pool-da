from segmentation.orchestrator import SegmentationOrchestrator

import logging
import os
from dotenv import load_dotenv
import json
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

def get_segment_config():
    """Get segmentation configuration"""
    config_path = os.getenv("SEGMENT_CONFIG", "config/segment_config.json")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Segment configuration file not found: {config_path}")
    return config_path

def main():
    try:
        logging.info("Starting neighborhood analysis pipeline")
        
        # Get validated DB config
        db_url = get_db_config()

        # Load config
        segment_config = get_segment_config()
        with open(segment_config, "r") as f:
            config = json.load(f)

        
        # Initialize orchestrator
        orchestrator = SegmentationOrchestrator(db_url)

        for table_name, methods in config["tables"].items():
            orchestrator.add(table_name, methods)

        # Run pipeline
        results = orchestrator.run_pipeline()
        logging.info("Segmentation pipeline completed successfully")
        logging.info(f"Results: {results}")

        # Generate visualizations
        orchestrator.visualize_results(results, "viz")
        
        logging.info("Analysis pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Error in analysis pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()