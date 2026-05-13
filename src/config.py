import os
from dotenv import load_dotenv

load_dotenv()

# Required environment variables with validation
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is required. Please set it in your .env file.")

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") or os.getenv("PINECONE_INDEX") or "policy-assistant"
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD")
PINECONE_REGION = os.getenv("PINECONE_REGION")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_HOST = os.getenv("PINECONE_HOST")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate LLM configuration
if LLM_PROVIDER.lower() == "gemini" and not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required when LLM_PROVIDER is set to 'gemini'")
elif LLM_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required when LLM_PROVIDER is set to 'openai'")

CORPUS_ZIP_URL = os.getenv("CORPUS_ZIP_URL")