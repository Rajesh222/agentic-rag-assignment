import os
import json
import openai
from src.config import LLM_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY
from src.tools.retrieve import RetrieveTool, GetDocumentMetadataTool, CheckContradictionsTool

openai.api_key = OPENAI_API_KEY

class LLMClient:
    def __init__(self):
        self.provider = LLM_PROVIDER.lower()
        if self.provider == "gemini":
            try:
                import google.genai as genai
            except ImportError:
                genai = None
            self.genai = genai
            if genai is not None:
                genai.configure(api_key=GEMINI_API_KEY)

    def generate(self, prompt_text: str) -> str:
        try:
            if self.provider == "gemini":
                if self.genai is None:
                    raise RuntimeError("Gemini provider requested but google.genai is not installed")
                response = self.genai.TextGeneration.create(
                    model="gemini-1.5-pro",
                    prompt=prompt_text,
                    temperature=0.2,
                    max_output_tokens=800
                )
                return response.candidates[0].output
            else:
                return self._openai_generate(prompt_text)
        except Exception as e:
            print(f"LLM API error: {e}")
            raise RuntimeError(f"Failed to generate response from {self.provider}: {e}")

    def _openai_generate(self, prompt_text: str) -> str:
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are an agentic corporate policy assistant."},
                          {"role": "user", "content": prompt_text}],
                temperature=0.2,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise

llm_client = LLMClient()

def ask_question(question):
    trace = []
    
    # Step 1: Plan
    plan_prompt = f"Break down this corporate policy question into steps to answer: {question}"
    plan_content = llm_client.generate(plan_prompt)
    trace.append(f"Plan: {plan_content}")
    
    # Step 2: Retrieve
    retrieve_tool = RetrieveTool()
    retrieve_result = retrieve_tool._run(question)
    chunks = json.loads(retrieve_result)
    trace.append(f"Retrieved {len(chunks)} chunks")
    
    # Step 2.5: Check if retrieval returned meaningful results
    if not chunks or len(chunks) == 0:
        trace.append("No relevant documents found in corpus")
        return {
            "answer": "I cannot find an authoritative answer in the policy corpus. Please consult with HR or Operations for assistance.",
            "trace": trace,
            "status": "no_information"
        }
    
    # Step 3: Check metadata
    metadata_tool = GetDocumentMetadataTool()
    metadata = {}
    for chunk in chunks:
        doc_id = chunk["doc_id"]
        meta = metadata_tool._run(doc_id)
        metadata[doc_id] = json.loads(meta)
    trace.append(f"Checked metadata for {len(metadata)} documents")
    
    # Step 4: Check contradictions
    contradictions = ""
    if len(chunks) > 1:
        doc_ids = list(metadata.keys())
        contradiction_tool = CheckContradictionsTool()
        contradictions = contradiction_tool._run(json.dumps(doc_ids))
        trace.append(f"Contradictions: {contradictions}")
    
    # Step 5: Generate answer
    answer_prompt = (
        "Answer this corporate policy question based on the retrieved information.\n"
        f"Question: {question}\n"
        f"Retrieved chunks: {json.dumps(chunks)}\n"
        f"Document metadata: {json.dumps(metadata)}\n"
        f"Potential contradictions: {contradictions}\n"
        "Provide a grounded answer with citations. If contradictions exist, surface them. If no information, refuse."
    )
    answer_content = llm_client.generate(answer_prompt)
    trace.append("Final answer generated")
    
    # Step 6: Self-critique
    critique_prompt = (
        "Review this answer for groundedness. Flag any claims not supported by the chunks.\n"
        f"Answer: {answer_content}\n"
        f"Chunks: {json.dumps(chunks)}"
    )
    critique_content = llm_client.generate(critique_prompt)
    trace.append(f"Critique: {critique_content}")
    
    return {
        "answer": answer_content,
        "trace": trace
    }