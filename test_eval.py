#!/usr/bin/env python3
"""Minimal test to verify evaluation harness works"""

import json
import os
from src.agent import ask_question

# Test with a single question
questions_path = "policy_corpus/eval_questions.json"

with open(questions_path, "r") as f:
    data = json.load(f)

questions = data.get("questions", [])
print(f"Loaded {len(questions)} questions")

# Run just the first question
q = questions[0]
print(f"\nTesting Q1: {q['question']}")

try:
    answer_result = ask_question(q["question"])
    print(f"✓ Answer received: {answer_result['answer'][:200]}...")
    print(f"✓ Trace items: {len(answer_result['trace'])}")
    
    # Try to save a test results file
    with open("test_results.json", "w") as f:
        json.dump({"test": "success", "answer": answer_result}, f, indent=2)
    print("✓ Test results saved to test_results.json")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
