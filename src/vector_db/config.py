"""
Configuration Module for Vector Database Operations

This module handles configuration loading from environment variables and
provides default values for vector database operations.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class VectorDBConfig:
    """
    Configuration class for vector database operations.
    
    This class loads configuration from environment variables and provides
    default values for all required settings.
    """
    
    def __init__(self):
        """Initialize configuration with default values and environment overrides."""
        # Qdrant configuration
        self.QDRANT_URL = os.getenv("QDRANT_URL", "")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
        
        # Collection names
        self.PRODUCT_COLLECTION = os.getenv("PRODUCT_COLLECTION", "sutra_db")
        self.FAQ_COLLECTION = os.getenv("FAQ_COLLECTION", "faq")
        
        # Embedding models
        self.FAQ_EMBEDDING_MODEL = os.getenv("FAQ_EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
        self.PRODUCT_EMBEDDING_MODEL = os.getenv("PRODUCT_EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
        
        # Vector dimensions (based on the embedding models)
        self.FAQ_VECTOR_SIZE = int(os.getenv("FAQ_VECTOR_SIZE", "384"))
        self.PRODUCT_VECTOR_SIZE = int(os.getenv("PRODUCT_VECTOR_SIZE", "1024"))
        
        # Batch processing
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))


# Global configuration instance
config = VectorDBConfig()