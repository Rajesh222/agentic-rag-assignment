# 1. Navigate to project
cd c:\newAssignment

# 2. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (edit .env with your API keys)
copy .env.example .env
# Edit .env with: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_CLOUD, PINECONE_REGION

# 5. Verify health check
python health_check.py

# 6. Ingest corpus (one-time, ~2-5 min)
python src/ingest.py

# 7. Test a question
python ask.py "What is the standard notice period at Meridian?"

# 8. Run full evaluation
python evaluate.py
# → Generates results.json with 15 test questions