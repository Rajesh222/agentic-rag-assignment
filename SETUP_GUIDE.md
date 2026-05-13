# Agentic RAG Assistant — Complete Setup Guide

This guide walks you through setting up and running the assignment from scratch.

---

## **PART 1: PREREQUISITES**

### Requirements
- **Python 3.11+** (tested on Python 3.11.0)
- **API Keys** (at least one):
  - OpenAI API key (`sk-...`)
  - OR Google Gemini API key
  - OR both (can switch via `.env`)
- **Pinecone Account** (free tier is fine)
  - API key
  - Cloud region (e.g., `aws`, `gcp`)
  - Region (e.g., `us-east-1`, `us-west-2`)

### Verify Python Installation
```bash
python --version
# Should output: Python 3.11.x or higher
```

If Python 3.11+ is not your default, use the full path:
```bash
C:\path\to\python3.11\python --version
```

---

## **PART 2: CLONE OR DOWNLOAD THE PROJECT**

If you don't have the project yet:
```bash
git clone <your-repo-url> newAssignment
cd newAssignment
```

Or if you have it already:
```bash
cd c:\newAssignment
```

---

## **PART 3: CREATE AND ACTIVATE VIRTUAL ENVIRONMENT**

### On Windows (PowerShell)
```bash
# Create venv
python -m venv .venv

# Activate venv
.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

### On macOS/Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

After activation, you should see `(.venv)` in your terminal prompt.

---

## **PART 4: INSTALL DEPENDENCIES**

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

This installs:
- LangChain (orchestration)
- Pinecone (vector DB)
- OpenAI (LLM client)
- sentence-transformers (embeddings)
- rank-bm25 (keyword search)
- PyPDF2, python-docx (document parsing)
- python-dotenv (config management)

**Expected output:**
```
Successfully installed langchain-1.3.0 pinecone-9.0.0 openai-2.36.0 ...
```

---

## **PART 5: CONFIGURE ENVIRONMENT VARIABLES**

### Step 1: Create `.env` file
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Or create manually:
```bash
# Windows
type .env.example > .env

# macOS/Linux
cat .env.example > .env
```

### Step 2: Edit `.env` with your credentials

**Option A: Use OpenAI (Recommended for testing)**
```env
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE

# Pinecone Configuration
PINECONE_API_KEY=pcsk_YOUR_PINECONE_KEY_HERE
PINECONE_INDEX_NAME=policy-assistant
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Optional (used if you download corpus automatically)
CORPUS_ZIP_URL=https://example.com/corpus.zip
```

**Option B: Use Gemini (Free tier available)**
```env
# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_YOUR_GEMINI_KEY_HERE

# Pinecone Configuration
PINECONE_API_KEY=pcsk_YOUR_PINECONE_KEY_HERE
PINECONE_INDEX_NAME=policy-assistant
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

### Step 3: Verify .env is loaded
```bash
python -c "from src.config import LLM_PROVIDER; print(f'Provider: {LLM_PROVIDER}')"
```

**Expected output:**
```
Provider: openai
# (or gemini, depending on your .env)
```

---

## **PART 6: VERIFY CORPUS IS PRESENT**

The corpus should be in `policy_corpus/` directory.

### Check what's there:
```bash
# Windows
dir policy_corpus | head -20

# macOS/Linux
ls policy_corpus | head -20
```

**Expected structure:**
```
policy_corpus/
  ├─ POL-HR-001.md
  ├─ POL-HR-002.md
  ├─ POL-TRAVEL-001.md
  ├─ POL-FIN-001.md
  ├─ metadata.json
  ├─ eval_questions.json
  └─ ... (43 total documents)
```

If files are missing, download from the link provided in the assessment email.

---

## **PART 7: RUN HEALTH CHECK (OPTIONAL BUT RECOMMENDED)**

Test that all dependencies and APIs are configured correctly:

```bash
python health_check.py
```

**Expected output:**
```
🏥 Agentic RAG Assistant - Health Check
==================================================
🔍 Checking environment configuration...
  ✅ PINECONE_API_KEY
  ✅ PINECONE_CLOUD
  ✅ PINECONE_REGION
  ✅ LLM_PROVIDER
  ✅ OPENAI_API_KEY

🔍 Checking dependencies...
  ✅ pinecone
  ✅ sentence_transformers
  ... (more checks)
```

If any check fails, fix the `.env` file before proceeding.

---

## **PART 8: INGEST CORPUS INTO PINECONE (ONE-TIME)**

This step indexes all 43 policy documents into Pinecone's vector DB.

```bash
python src/ingest.py
```

**What happens:**
1. Loads all `.md`, `.pdf`, `.docx` files from `policy_corpus/`
2. Chunks documents into 1000-char windows (100-char overlap)
3. Generates embeddings using sentence-transformers
4. Uploads to Pinecone index
5. **Takes ~2-5 minutes on first run**

**Expected output:**
```
Loading and chunking documents...
Loaded 43 documents
Creating vector store...
Initializing embeddings model...
Loading weights: 100%|███████| 103/103 [00:00<00:00, 2016.93it/s]
Connecting to Pinecone...
Using existing Pinecone index: policy-assistant
Upserting vectors... (batch 1/5)
Upserting vectors... (batch 2/5)
...
Ingestion complete
```

**If Pinecone index doesn't exist:**
The script will auto-create it if `PINECONE_CLOUD` and `PINECONE_REGION` are set.

Or create manually in Pinecone Console:
- Dimension: 384
- Metric: cosine
- Name: policy-assistant (or whatever you set in `.env`)

---

## **PART 9: TEST A SINGLE QUESTION (CLI)**

Now test the agent with a real question:

```bash
python ask.py "What is the standard notice period at Meridian?"
```

**First run initialization (only first time):**
- Loads embedding model (~30s, one-time download)
- Connects to Pinecone
- Builds in-memory BM25 index
- Then answers your question

**Expected output:**
```
Initializing embeddings model...
Loading weights: 100%|███████| 103/103 [00:00<00:00, 4360.20it/s]
Connecting to Pinecone...
Building BM25 index...

Answer: The standard notice period at Meridian is [answer from corpus]...

Trace: [
  "Plan: Break down the question...",
  "Retrieved 5 chunks",
  "Checked metadata for 5 documents",
  "Contradictions: Potential contradictions detected...",
  "Final answer generated",
  "Critique: ..."
]
```

**Test a few more questions:**
```bash
# Single-doc question
python ask.py "What is the hotel cap per night for business travel to Europe?"

# Composition question
python ask.py "If I travel from Dubai to Abu Dhabi for a meeting with a UAE government client, what approvals and expense rules apply?"

# Contradiction question (should surface conflict)
python ask.py "How many days of paternity leave am I entitled to?"

# Out-of-scope (should refuse)
python ask.py "What is Meridian's stock ticker symbol?"
```

---

## **PART 10: RUN FULL EVALUATION (15 TEST QUESTIONS)**

This evaluates the system across all 15 test questions and generates `results.json`:

```bash
python evaluate.py
```

**Expected output:**
```
Running evaluation on 15 questions...
Start time: 2026-05-13 14:30:00

[ 1/15] Q01 (single_doc  ) - What is the standard notice period... ✓ 7.2s (2 citations)
[ 2/15] Q02 (single_doc  ) - What is the hotel cap per night... ✓ 6.8s (1 citation)
[ 3/15] Q03 (single_doc  ) - What is the procurement approval... ✓ 7.5s (3 citations)
...
[14/15] Q14 (supersession) - How far in advance do I need... ✓ 8.1s (2 citations)
[15/15] Q15 (out_of_scope) - What is Meridian's stock ticker... ✓ 6.9s (0 citations)

======================================================================
EVALUATION SUMMARY
======================================================================
Total Questions: 15
Successful: 15 | Failed: 0
Total Time: 112.3s
Average Response Time: 7.5s

By Type:
  - Single Doc: 5
  - Composition: 4
  - Contradiction: 3
  - Supersession: 2
  - Out of Scope: 1

Results saved to results.json
End time: 2026-05-13 14:32:00
======================================================================
```

### Check results:
```bash
# View full results (pretty-printed)
python -m json.tool results.json | head -100

# Or open in editor:
# Windows
notepad results.json
# macOS/Linux
cat results.json
```

**Expected `results.json` structure:**
```json
{
  "metadata": {
    "timestamp": "2026-05-13 14:30:00",
    "total_questions": 15,
    "total_time_seconds": 112.3,
    "metrics": {
      "total": 15,
      "single_doc": 5,
      "composition": 4,
      "contradiction": 3,
      "supersession": 2,
      "out_of_scope": 1,
      "successful": 15,
      "failed": 0,
      "avg_response_time": 7.5
    }
  },
  "results": [
    {
      "id": "Q01",
      "type": "single_doc",
      "question": "What is the standard notice period at Meridian?",
      "answer": "The standard notice period at Meridian is 30 days...",
      "citations": ["POL-HR-001", "POL-HR-003"],
      "contradictions_detected": false,
      "response_time_seconds": 7.2,
      "trace_length": 6,
      "status": "success"
    },
    ...
  ]
}
```

---

## **PART 11: INTERPRET RESULTS**

### Success Metrics

**Good signs:**
- ✅ All 15 questions answered without errors
- ✅ Single-doc questions have 1-3 citations
- ✅ Composition questions cite 2+ documents
- ✅ Contradiction questions flag conflicts (status shows `contradiction_surface: true`)
- ✅ Out-of-scope returns "cannot find"
- ✅ Average response time 5-10s per question

**Red flags:**
- ❌ Consistent failure on specific question types
- ❌ Single citations for composition questions (should cite multiple docs)
- ❌ Contradiction questions don't show conflict detection
- ❌ Out-of-scope questions return fabricated answers
- ❌ Response time >30s (embedding model or API timeout issue)

---

## **PART 12: TROUBLESHOOTING**

### Issue: "PINECONE_API_KEY environment variable is required"
**Solution:** Check `.env` file has `PINECONE_API_KEY=pcsk_...` (not empty)
```bash
# Verify
grep PINECONE_API_KEY .env
```

### Issue: "Index 'policy-assistant' does not exist"
**Solution:** Run ingestion:
```bash
python src/ingest.py
```

### Issue: "The official Pinecone python package has been renamed..."
**Solution:** Clean install:
```bash
pip uninstall -y pinecone-client pinecone
pip install pinecone
```

### Issue: Slow embedding model download (first run takes 30s+)
**Solution:** This is normal. Subsequent runs are cached. On next import, it's instant.

### Issue: "No module named 'X'"
**Solution:** Reinstall requirements:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "Execution policy" error (Windows PowerShell)
**Solution:**
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

### Issue: API quota exceeded / Rate limited
**Solution:**
- OpenAI: Check API credits at https://platform.openai.com/account/usage/overview
- Gemini: Free tier has 60 RPM limit; add delays between calls
- Pinecone: Free tier has 5 million vectors; check usage in Console

---

## **PART 13: OPTIONAL — SWITCH LLM PROVIDER**

### Change from OpenAI to Gemini

**Edit `.env`:**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_YOUR_KEY_HERE
```

**Test:**
```bash
python ask.py "What is the standard notice period?"
```

The system auto-detects and uses the right LLM client.

---

## **PART 14: OPTIONAL — BUILD AND RUN DOCKER**

If you want to containerize the system:

```bash
# Build image
docker build -t agentic-rag-assistant .

# Run container (replace with your keys)
docker run -e OPENAI_API_KEY=sk-... \
           -e PINECONE_API_KEY=pcsk_... \
           -e PINECONE_CLOUD=aws \
           -e PINECONE_REGION=us-east-1 \
           -e LLM_PROVIDER=openai \
           agentic-rag-assistant \
           python ask.py "Your question here"
```

---

## **PART 15: FULL WORKFLOW CHECKLIST**

Use this checklist to verify everything is set up:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated (`.venv`)
- [ ] `requirements.txt` installed successfully
- [ ] `.env` file created with all API keys
- [ ] Health check passes (`python health_check.py`)
- [ ] Corpus files present in `policy_corpus/` (43 documents)
- [ ] Ingestion completes (`python src/ingest.py`)
- [ ] Single question works (`python ask.py "What is the standard notice period?"`)
- [ ] Full evaluation passes (`python evaluate.py`)
- [ ] `results.json` generated and readable
- [ ] At least 14/15 questions successful
- [ ] README.md reviewed for architecture details

---

## **PART 16: NEXT STEPS FOR INTERVIEW PREP**

1. **Test manually:** Try Q10 (contradiction), Q06 (composition), Q15 (out-of-scope)
2. **Review traces:** Open `results.json` and read the trace for each question type
3. **Understand architecture:** Read [README.md](README.md) (section 2-8)
4. **Prepare talking points:** See "Interview Walkthrough" section in the README
5. **Know limitations:** Review "Known weaknesses" in the README
6. **Time yourself:** How long does `python evaluate.py` take? (~2-3 minutes)

---

## **PART 17: QUICK REFERENCE COMMANDS**

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Test import
python -c "from src.agent import ask_question; print('✅ Ready')"

# Single question
python ask.py "Your question here"

# Full evaluation
python evaluate.py

# Health check
python health_check.py

# Ingest corpus
python src/ingest.py

# Deactivate venv
deactivate
```

---

## **DONE!**

Your system is now fully configured and tested. You can:

1. **Answer questions interactively:** `python ask.py "..."`
2. **Evaluate on test set:** `python evaluate.py` → `results.json`
3. **Explain the architecture** to interviewers using the traces and README

**Good luck with your interview!**

---

*Last updated: May 13, 2026*
*Assignment: Agentic RAG Assistant for Corporate Policy Advisor*
