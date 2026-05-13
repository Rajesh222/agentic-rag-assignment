
SENIOR AI ENGINEER
Interview Technical Assessment
Agentic RAG Assistant — Corporate Policy Advisor
Assessment reference: AIE-2026-01
Role under consideration	Senior AI Engineer
Time budget	1 to 2 days of focused effort (roughly 14 to 16 hours)
Deadline	Thursday 07 May 2026 (3 days from receipt)
Submission	GitHub repository link and video walkthrough, replied to the assessment email
 
1 Scenario
You are joining as a Senior AI Engineer. Your first task is to build a prototype of a product the business team is scoping: an agentic assistant that helps employees navigate corporate policy documents.
A mid-sized consulting firm has 40-50 internal policy and SOP documents — HR, travel and expenses, procurement, IT security, vendor onboarding, client engagement rules, leave policy, remote work, code of conduct, data protection, and so on. These documents contradict each other in places, use inconsistent terminology, were written by different authors over several years, and are updated irregularly. Employees currently ask HR and Operations the same twenty questions every month. HR estimates that 30-40 percent of their ticket volume is questions that could be answered from the existing documents if anyone could actually find them.
A naive RAG chatbot has been tried. It failed for three reasons. First, policies overlap — asking about “parental leave” returns chunks from the leave policy, the HR handbook, and the employee benefits SOP, and the chatbot confidently merges them without noticing that two of them contradict. Second, policies change over time and employees need to know which version of a policy applied when — the bot returned an answer from a 2022 document when a 2024 update existed. Third, some questions require composing information across documents (“if I travel to the UAE for a client meeting, what expense category applies, what approvals do I need, and what is the per diem?”) — the naive bot could only retrieve fragments from single documents.
The business wants a working prototype that demonstrates how an agentic approach improves on naive RAG. The prototype will be demonstrated to the head of HR and the COO.
2 Objective
Build an agentic RAG assistant that answers employee questions about corporate policy correctly, cites its sources, handles the three failure modes above, and knows when to refuse or escalate.
The assistant must be genuinely agentic, not a single-shot retrieval call. We expect the system to plan how to answer a question (decompose, retrieve, cross-check, compose), use tools deliberately (at minimum: a retrieval tool, a metadata-filter tool, and a self-critique step), and produce answers that are traceable back to specific document spans. Where policies contradict, the assistant must surface the contradiction rather than pick one silently. Where the answer requires composing across documents, the assistant must show its reasoning. Where the available documents do not contain the answer, the assistant must say so rather than guess.
The deliverable is a runnable service with a simple text interface (CLI or web), a provided evaluation harness that scores the assistant against a held-out set of 15 test questions we supply, and a README that explains the architecture, the design decisions, and where the system is weak.
3 Provided corpus and evaluation harness
You will be supplied with a corpus of 43 fictional corporate policy documents as a ZIP file linked in the assessment email. The corpus includes:
 	29 Markdown policy documents ranging from 300 to 1,200 words each
 	10 PDF documents
 	4 DOCX files representing recently updated policies
 	A metadata.json file mapping each document to its category, effective date, superseded-by relationships, and author department
 	3 deliberate contradictions between documents (documented in a SOLUTIONS.md that only the reviewer has)
 	6 policies with newer-version replacements (the old version is still in the corpus; employees sometimes reference it)
The corpus is deliberately small enough to keep the whole project runnable on Gemini free tier but large enough that you cannot stuff everything into a single prompt — retrieval must actually work.

You will be supplied with `eval_questions.json` — a held-out set of 15 test questions covering the failure modes above. Your repository must include a runnable script `python evaluate.py` that feeds each question through your agent and produces a `results.json` with the agent’s answer, citations, confidence, and trace per question.
The test questions are distributed as follows:
 	5 single-document questions (e.g., “what is the standard notice period?”)
 	4 multi-document composition questions (e.g., the UAE business travel example in the scenario)
 	3 contradiction questions (designed to hit the known contradictions — the correct behavior is to surface the conflict, not pick one)
 	2 supersession questions (asking about a policy that has a newer version)
 	1 out-of-scope question (the answer is not in the corpus — correct behavior is to refuse)
Do not try to reverse-engineer the answer key. The test set provided to you deliberately does not match the scoring set exactly — the reviewer runs your system against a similar but different set when evaluating. Building to pass a specific set of questions will hurt your score.
4 Functional requirements
 	Ingest the supplied corpus on first run. Index it into a vector store of your choice. Re-running the ingest must be idempotent.
 	Accept a natural-language question via CLI or HTTP POST. Return (a) a final answer in plain text, (b) a list of citations pointing to specific document IDs and section locations, (c) a confidence signal, and (d) the trace of agent steps that produced the answer.
 	When the question can be answered from a single policy document, the assistant uses retrieval and answers directly.
 	When the question requires composing information from 2 or more documents, the assistant must plan the decomposition, retrieve from each relevant document, and compose a single coherent answer with citations to all sources used.
 	When two retrieved documents contradict, the assistant must detect the contradiction, surface it to the user (“Policy A says X, but Policy B says Y — please consult [department] for the authoritative answer”), and must NOT silently pick one.
 	When multiple versions of the same policy exist, the assistant must respect the metadata.json supersession chain and answer from the current version by default, while mentioning the prior version if the user’s question references it explicitly (for example, “what was the policy last year?”).
 	When the corpus does not contain the answer, the assistant must say “I cannot find an authoritative answer in the policy corpus” rather than produce a guess. No hallucinated citations.
 	Support at least English and Arabic question input. Answers should be returned in the same language the question was asked in. Retrieval must work across English-indexed policies when the question is in Arabic (the corpus itself is English; cross-lingual retrieval is the test).
5 Technical requirements
 	The orchestration must be genuinely multi-step. A single LLM call with retrieved context stuffed into the prompt does not meet the bar — we will detect this in the trace output and score it low. At minimum, your agent must have a planner step, a retrieval step, and a self-critique step before answering.
 	Use an agent framework of your choice (LangGraph, CrewAI, AutoGen, Semantic Kernel, OpenAI Agents SDK, or a framework you build yourself if you justify it). You must not hard-code the routing between tools — the LLM must decide which tool to call.
 	Implement at minimum these three tools the agent can call: `retrieve(query, top_k)` — returns top-k chunks with metadata; `get_document_metadata(doc_id)` — returns the document’s effective date, category, and supersession info; `check_contradictions(doc_ids)` — given a list of retrieved documents, determine whether their content conflicts on the user’s question.
 	Retrieval must be hybrid: combine dense embeddings with a keyword/BM25 signal. Pure semantic search will miss exact policy-name matches; pure keyword will miss rephrasings. Document the blend in the README.
 	Every claim in the final answer must be grounded in a retrieved chunk. Your critique step must flag any sentence in the draft answer that is not supported by a retrieved chunk, and the agent must revise before returning. Unsupported sentences in the final output will be scored as hallucinations.
 	Metadata filtering must be a first-class concern. If the user asks “what’s the current travel policy?” the retrieval must filter out superseded versions. Implement this as either a pre-retrieval filter or a post-retrieval reranker, but the behavior must be correct and traceable.
 	The system must produce a structured trace for every query that shows: the agent’s initial plan, each tool call with its arguments and returned data, the draft answer, the critique, and any revisions. The trace is both for the user’s transparency and for the reviewer’s evaluation.
6 Frameworks and tools
The stack below is a recommendation, not a prescription. You may deviate if you have a defensible reason — document that reason in the README.
 	Language: Python 3.11 or later (strongly preferred so we can actually run your code)
 	LLM: Gemini via Google AI Studio. The reviewer will use the free tier to evaluate. If you develop against a different provider (OpenAI, Anthropic, a local model), the LLM client must be configurable via a single environment variable so the reviewer can swap in GEMINI_API_KEY without changing code. Provide a working .env.example.
 	Agent orchestration: LangGraph, CrewAI, AutoGen, Semantic Kernel, OpenAI Agents SDK, PydanticAI, or a homegrown framework you can defend
 	Embeddings: any (sentence-transformers, Gemini embeddings, OpenAI embeddings, BGE). If you use Gemini embeddings to stay on one provider, note the rate-limit behavior in the README
 	Vector store: Chroma, FAISS, Qdrant, pgvector, LanceDB, or SQLite with sqlite-vec. Local and embedded is fine; nothing needs to run in the cloud
 	Keyword search for hybrid retrieval: whoosh, rank-bm25, or Postgres full-text
 	PDF/DOCX parsing: pdfplumber, PyMuPDF, python-docx, or Unstructured. The corpus includes both native and OCR-text PDFs; surface any parsing losses in the README
 	Containerization: a working Dockerfile. Docker Compose is welcome if your solution needs more than one service
 	Interface: a CLI that accepts `python ask.py “your question”` is sufficient. A FastAPI endpoint is welcome but not required
7 Technical guidelines
Please read these carefully before you start. They set the ground rules for what a good submission looks like.
 	Time budget: 1-2 days of focused effort, roughly 14-16 hours. This is an interview assessment, not a free consulting gig — spend the time on the parts of the problem that show judgment, not on polish.
 	You may use any AI coding assistant you work with normally (Copilot, Claude Code, Cursor, Continue). We care about your judgment, not your typing speed. Do not hand in code you cannot explain — we will ask about specific lines in the interview.
 	LLM usage: the reviewer runs evaluate.py against Gemini free tier. Your default code path must work with Gemini. You may use a different provider during development if you prefer, but the env-variable switch must be tested and documented.
 	Do not call Anthropic, OpenAI, or any paid API from your default configuration. Any feature that depends on a paid service must be optional, with a clearly documented free alternative.
 	Do not reach out to the hiring team for clarifications during the assessment. If a requirement is genuinely ambiguous, document your assumption in the README and proceed. How you handle ambiguity is part of the test.
 	Do not over-engineer. A clean, working 80 percent solution beats a broken 100 percent attempt. If you run out of time, ship what you have and add a “what I would do next” section to the README.
 	Be honest about limitations. The README must include a “Known weaknesses” section where you list at least 3 failure modes of your current system and what you would do to fix them. A blank or superficial weaknesses section is a red flag.
8 Deliverables
Submit exactly three items by replying to the assessment email with their links:
 	A GitHub repository (public, or private with read access granted to the reviewer email provided in the assignment). It must contain all source code, the ingestion pipeline, the agent implementation, the evaluate.py harness, the Dockerfile, and a working .env.example. It must NOT contain the corpus — re-download that from the link provided.
 	A README.md that explains your solution in depth. It must cover: what the system does and how to run it; the architecture, with a diagram (ASCII or embedded image); your model choices and the reasoning; how to switch the LLM to Gemini free tier; how to run evaluate.py; a walk-through of how the agent handles one contradiction question and one composition question from the provided test set; your decisions on retrieval blend, chunking, and metadata filtering; at least 3 known weaknesses; and what you would build next with another week.
 	A video (5 to 10 minutes, Loom or YouTube unlisted or Drive link) walking through the architecture for 2 minutes and then demonstrating the system answering at least 4 questions end-to-end: one single-doc, one composition, one contradiction, and one out-of-scope. Narrate what the agent is doing at each step.
9 How your submission will be evaluated
Two reviewers will independently score your submission using the rubric below and converge on a final score. Expect the total to sit between 60 and 95 points for submissions that complete the core requirements — the rubric intentionally separates good from great work.
 	Correctness on the held-out test set — does the agent answer the questions a reasonable employee would accept? Scored quantitatively by the reviewer running evaluate.py on their test set
 	Handling of contradictions — does the system detect conflicting documents and surface them, or does it silently pick one? A single silent pick on a contradiction question is a significant penalty
 	Handling of supersession — does the system respect the metadata and answer from the current version of a policy by default?
 	Groundedness — is every sentence in the answer traceable to a retrieved chunk? Hallucinated citations or unsupported claims are scored heavily
 	Agent design — is the orchestration genuinely multi-step, with the LLM deciding tool routing, or is it a single-shot call dressed up? Traces make this visible
 	Refusal behavior — does the agent refuse out-of-scope questions or confabulate?
 	Cross-lingual retrieval — does an Arabic question successfully retrieve from the English corpus and return an Arabic answer?
 	Engineering quality — does the code read cleanly, is it tested where it matters (at minimum the retrieval layer and the contradiction detector), is configuration managed properly?
 	Honesty in the README — does the Known Weaknesses section demonstrate self-awareness? Candidates who list real limitations score higher than candidates who claim their system is perfect
10 Scoring breakdown
The 100 points are distributed as follows:
Correctness on the 15 held-out questions	30 points — 2 points per question graded by the reviewer
Contradiction detection (3 questions)	15 points — a silent pick scores 0, a surfaced conflict scores 5
Supersession handling (2 questions)	10 points — 5 points each
Groundedness — no unsupported claims or hallucinated citations	10 points — reviewer audits the answers to the 15 questions
Agent architecture — multi-step, tool-routing, self-critique visible in traces	10 points
Cross-lingual retrieval — Arabic question returns correct Arabic answer with English citations	5 points
Engineering quality — code, tests, configurability, Docker works out of the box	10 points
README depth and honesty — architecture, decisions, known weaknesses	10 points
Total	100 points
11 What we are not testing
To help you scope the 14 to 16 hours, here is what we explicitly do not want you to spend time on:
 	You do not need to build a polished UI. A CLI that takes a question and returns an answer plus trace is sufficient.
 	You do not need to fine-tune any model. Off-the-shelf Gemini with good prompting beats a clumsy fine-tune for this assessment.
 	You do not need to handle production scale. Running well on a corpus of 43 documents is the target.
 	You do not need to implement authentication, multi-tenancy, or cloud deployment. A Docker container running locally is the deployment target.
 	You do not need to write a management report. We have the scenario; skip restating it.
