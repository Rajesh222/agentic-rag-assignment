#!/usr/bin/env python3
import sys
import re
from src.agent import ask_question
import json

def detect_language(text):
    """Simple language detection: if Arabic script detected, return 'ar', else 'en'."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    if arabic_pattern.search(text):
        return 'ar'
    return 'en'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ask.py 'your question'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    
    # Detect input language
    input_language = detect_language(question)
    
    # Get answer from agent
    result = ask_question(question)
    
    # If question was in Arabic, note that response should be in Arabic
    if input_language == 'ar':
        print(f"[Input language: Arabic]")
        print(f"[Response language: Arabic (English text provided below)]\n")
    
    print("Answer:", result["answer"])
    print("\nTrace:", json.dumps(result["trace"], indent=2))
    
    if "citations" in result:
        print("\nCitations:", result["citations"])
