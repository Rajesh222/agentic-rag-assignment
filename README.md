# Agentic RAG Assistant for Corporate Policy Advisor

## Overview
This project implements an agentic RAG (Retrieval-Augmented Generation) assistant that helps employees navigate corporate policy documents. The system uses LangChain for orchestration, Pinecone for vector storage, and supports configurable LLMs (Gemini or OpenAI).

## Features
- Multi-step agentic workflow with planning, retrieval, and self-critique
- Hybrid retrieval combining dense embeddings and keyword search
- Handles contradictions, supersession, and out-of-scope questions
- Supports English and Arabic queries
- Citations and traceability
- Evaluation harness for testing

## Architecture
The system uses a multi-step agent workflow:
1. Planner: Decompose the question
2. Retriever: Get relevant chunks using hybrid search (dense + sparse)
3. Metadata Checker: Verify document versions and supersession
4. Contradiction Detector: Surface conflicts
5. Self-Critique: Ensure groundedness
6. Final Answer: With citations and trace

Vector Store: Pinecone with SentenceTransformers embeddings
Agent Framework: LangChain with OpenAI Functions
Tools: retrieve, get_document_metadata, check_contradictions

## Setup

### Prerequisites
- Python 3.11+
- Pinecone account and API key
- Gemini API key (or OpenAI)

### Installation
1. Clone the repository
### 1. Navigate to project
cd c:\newAssignment

### 2. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure (edit .env with your API keys)
copy .env.example .env
### Edit .env with: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_CLOUD, PINECONE_REGION

### 5. Verify health check
python health_check.py

### 6. Ingest corpus (one-time, ~2-5 min)
python src/ingest.py

### 7. Test a question
python ask.py "What is the standard notice period at Meridian?"

### 8. Run full evaluation
python evaluate.py
### → Generates results.json with 15 test questions

## Troubleshooting

### Common Issues

**Pinecone Index Creation Fails**
```
Pinecone index does not exist and cannot be auto-created without PINECONE_CLOUD and PINECONE_REGION
```
**Solution**: Set these environment variables in `.env`:
```
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```
Or create the index manually in Pinecone Console with dimension=384, metric=cosine.

**Index Already Exists Error**
```
HTTP response body: {"error":{"code":"ALREADY_EXISTS","message":"Resource already exists"},"status":409}
```
**Solution**: The system will automatically use the existing index. This is not an error.

**OpenAI API Errors**
```
You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0
```
**Solution**: The code uses the correct API. If you see this, check your OpenAI package version:
```bash
pip install --upgrade openai>=1.0.0
```

**Missing Environment Variables**
```
PINECONE_API_KEY environment variable is required
```
**Solution**: Copy `.env.example` to `.env` and fill in all required values.

**Arabic Questions Not Translated**
- Current limitation: Arabic retrieval works but responses stay in English
- **Future improvement**: Add Google Translate integration

### Health Check
Run `python health_check.py` to verify:
- ✅ Environment variables configured
- ✅ All dependencies installed
- ✅ Pinecone connection working
- ✅ LLM API accessible
- ✅ Index exists and is ready

### Performance Tips
- Use hybrid retrieval for better coverage of both semantic and keyword queries
- For large corpora, consider increasing chunk overlap or using smaller chunks
- Monitor Pinecone usage and costs for production deployment

## Design Decisions
- LangChain for agent framework due to flexibility and tool integration
- Pinecone for vector DB with hybrid search capability
- Hybrid retrieval: Dense embeddings for semantic similarity, BM25 for keyword matching
- Chunking: 1000 characters with 100 overlap for context preservation
- Metadata filtering: Post-retrieval filtering based on effective dates
- LLM: Configurable between Gemini (free tier) and OpenAI
- Agent steps: Enforced multi-step process with planning and critique
Hybrid retrieval not fully implemented - currently dense-only
2. Contradiction detection is simplistic - needs LLM-based analysis
3. Arabic support relies on LLM capabilities without dedicated translation
4. No advanced conflict resolution beyond detection
5. Evaluation harness is basic - no automated scoring
6. Performance not optimized for large corporation
3. Evaluation only on provided test set
4. Performance on very large corpora not tested
full hybrid retrieval with sparse vectors in Pinecone
- Add LLM-based contradiction analysis
- Implement translation layer for better Arabic support
- Add automated evaluation scoring
- Optimize chunking and retrieval for better performance
- Add user feedback loop for continuous improvement
- Support more document formats
- Improve Arabic retrieval with translation layer