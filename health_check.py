#!/usr/bin/env python3
"""
Health check script for the Agentic RAG Assistant
Verifies all dependencies and configurations before running the main application.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def check_environment():
    """Check environment variables and configuration."""
    print("🔍 Checking environment configuration...")

    try:
        from src.config import (
            PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_CLOUD, PINECONE_REGION,
            LLM_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY
        )

        checks = [
            ("PINECONE_API_KEY", PINECONE_API_KEY is not None),
            ("PINECONE_CLOUD", PINECONE_CLOUD is not None),
            ("PINECONE_REGION", PINECONE_REGION is not None),
            ("LLM_PROVIDER", LLM_PROVIDER in ["openai", "gemini"]),
        ]

        if LLM_PROVIDER == "gemini":
            checks.append(("GEMINI_API_KEY", GEMINI_API_KEY is not None))
        elif LLM_PROVIDER == "openai":
            checks.append(("OPENAI_API_KEY", OPENAI_API_KEY is not None))

        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        return all(passed for _, passed in checks)

    except Exception as e:
        print(f"❌ Environment check failed: {e}")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        ("pinecone", "pinecone"),
        ("sentence_transformers", "sentence_transformers"),
        ("openai", "openai"),
        ("langchain", "langchain"),
        ("rank_bm25", "rank_bm25"),
        ("PyPDF2", "PyPDF2"),
        ("docx", "docx"),
        ("dotenv", "dotenv")
    ]

    failed_packages = []

    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name}")
            failed_packages.append(package_name)

    if failed_packages:
        print(f"\n❌ Missing packages: {', '.join(failed_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    return True

def check_pinecone_connection():
    """Test Pinecone connection and index access."""
    print("\n🔍 Checking Pinecone connection...")

    try:
        from pinecone import Pinecone
        from src.config import PINECONE_API_KEY, PINECONE_INDEX_NAME

        pc = Pinecone(api_key=PINECONE_API_KEY)
        indexes = pc.list_indexes()

        if any(idx['name'] == PINECONE_INDEX_NAME for idx in indexes):
            print(f"  ✅ Index '{PINECONE_INDEX_NAME}' exists")
            return True
        else:
            print(f"  ⚠️  Index '{PINECONE_INDEX_NAME}' not found")
            print("  Run: python src/ingest.py")
            return False

    except Exception as e:
        print(f"  ❌ Pinecone connection failed: {e}")
        return False

def check_llm_connection():
    """Test LLM API connection."""
    print("\n🔍 Checking LLM connection...")

    try:
        from src.agent import llm_client

        # Simple test prompt
        response = llm_client.generate("Say 'Hello' if you can read this.")
        if response and len(response.strip()) > 0:
            print("  ✅ LLM connection successful")
            return True
        else:
            print("  ❌ LLM returned empty response")
            return False

    except Exception as e:
        print(f"  ❌ LLM connection failed: {e}")
        return False

def main():
    """Run all health checks."""
    print("🏥 Agentic RAG Assistant - Health Check")
    print("=" * 50)

    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Pinecone", check_pinecone_connection),
        ("LLM", check_llm_connection),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All checks passed! System is ready.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())