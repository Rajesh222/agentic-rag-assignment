import json
import os
import re
import time
from src.agent import ask_question

def extract_citations(answer_text):
    """Extract document citations from answer text (doc_id patterns and document references)."""
    citations = []
    
    # Pattern 1: Direct doc_id mentions like "POL-HR-001"
    doc_pattern = r'POL-[A-Z]+-\d{3}(?:-v\d+)?'
    for match in re.finditer(doc_pattern, answer_text):
        doc_id = match.group()
        if doc_id not in citations:
            citations.append(doc_id)
    
    # Pattern 2: Parenthetical references like "(Document ID: POL-HR-002)"
    paren_pattern = r'\((?:Document ID|ID|Document|document ID):\s*([A-Z\d-]+)\)'
    for match in re.finditer(paren_pattern, answer_text):
        doc_id = match.group(1)
        if doc_id not in citations:
            citations.append(doc_id)
    
    return citations


def extract_contradictions(trace):
    """Extract contradiction detections from agent trace."""
    contradictions = []
    for trace_item in trace:
        if "Contradictions:" in trace_item:
            contradictions.append(trace_item)
    return contradictions


def evaluate():
    """Run evaluation on all questions in eval_questions.json."""
    questions_path = "policy_corpus/eval_questions.json"
    
    if not os.path.exists(questions_path):
        print(f"Questions file not found at {questions_path}")
        return
    
    with open(questions_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])

    # Remove any legacy interim result files to keep output single-file only
    for filename in os.listdir("."):
        if filename.startswith("results_interim_") and filename.endswith(".json"):
            try:
                os.remove(filename)
            except OSError:
                pass
    results = []
    metrics = {
        "total": len(questions),
        "single_doc": 0,
        "composition": 0,
        "contradiction": 0,
        "supersession": 0,
        "out_of_scope": 0,
        "successful": 0,
        "failed": 0,
        "avg_response_time": 0
    }
    
    print(f"Running evaluation on {len(questions)} questions...")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_time = 0
    for idx, q in enumerate(questions, 1):
        question_id = q.get("id", f"Q{idx:02d}")
        question_text = q.get("question", "")
        q_type = q.get("type", "unknown")
        expected_lang = q.get("expected_language", "en")
        
        # Update metrics by type
        if q_type in metrics:
            metrics[q_type] += 1
        
        q_preview = question_text[:50].replace("\n", " ")
        print(f"[{idx:2d}/{len(questions)}] {question_id} ({q_type:12s}) - {q_preview}...", end="", flush=True)
        
        try:
            start_time = time.time()
            answer_result = ask_question(question_text)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            answer_text = answer_result.get("answer", "")
            trace = answer_result.get("trace", [])
            
            citations = extract_citations(answer_text)
            contradictions = extract_contradictions(trace)
            
            result = {
                "id": question_id,
                "type": q_type,
                "question": question_text,
                "expected_language": expected_lang,
                "answer": answer_text[:500],  # Truncate for brevity
                "citations": citations,
                "contradictions_detected": len(contradictions) > 0,
                "response_time_seconds": round(elapsed, 2),
                "trace_length": len(trace),
                "status": "success"
            }
            
            # For contradiction questions, check if contradictions were detected
            if q_type == "contradiction" and contradictions:
                result["contradiction_surface"] = True
            
            results.append(result)
            metrics["successful"] += 1
            print(f" ✓ {elapsed:.1f}s ({len(citations)} citations)")
            
        except Exception as e:
            result = {
                "id": question_id,
                "type": q_type,
                "question": question_text,
                "error": str(e)[:200],
                "status": "failed"
            }
            results.append(result)
            metrics["failed"] += 1
            print(f" ✗ {str(e)[:50]}")
        
    # Calculate average response time
    if metrics["successful"] > 0:
        metrics["avg_response_time"] = round(total_time / metrics["successful"], 2)

    # Save single final result file
    output_file = "results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_questions": len(questions),
                "total_time_seconds": round(total_time, 2),
                "metrics": metrics
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    print(f"Total Questions: {metrics['total']}")
    print(f"Successful: {metrics['successful']} | Failed: {metrics['failed']}")
    print(f"Total Time: {round(total_time, 2)}s")
    print(f"Average Response Time: {metrics['avg_response_time']}s")
    print(f"\nBy Type:")
    print(f"  - Single Doc: {metrics['single_doc']}")
    print(f"  - Composition: {metrics['composition']}")
    print(f"  - Contradiction: {metrics['contradiction']}")
    print(f"  - Supersession: {metrics['supersession']}")
    print(f"  - Out of Scope: {metrics['out_of_scope']}")
    print(f"\nResults saved to {output_file}")
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    evaluate()