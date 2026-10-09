# Autonomous Web Browsing Agent with RAG, Self-Correction, and Evidence-Based Research

An industrial-grade, Python-first autonomous research and browser automation agent. Accepts natural-language tasks, formulates structured execution plans, searches the web across multiple providers, navigates deep into destination websites with Playwright, extracts structured facts (specs, prices, ratings, tables), indexes content in a persistent hybrid RAG vector store, self-corrects on failures, audits completion criteria, and synthesizes evidence-grounded answers with clickable markdown source citations.

---

## 🏗️ Architecture Overview

The application follows a modular decoupled architecture:

```
+-------------------------------------------------------------------------------------------------+
|                                      STREAMLIT UI (app.py)                                       |
|  [Goal Input] [Controls: Headless / Model / Max Pages] [Progress] [Logs] [Evidence] [Answer]  |
+------------------------------------------------+------------------------------------------------+
                                                 |
                                                 v
+-------------------------------------------------------------------------------------------------+
|                                    AUTONOMOUS AGENT ORCHESTRATOR                                |
|                                       (agent/agent.py)                                          |
+------------------------------------------------+------------------------------------------------+
     |                    |                      |                        |
     v                    v                      v                        v
+------------+     +--------------+      +---------------+      +-------------------+
|  PLANNER   |     |   EXECUTOR   |      |   OBSERVER    |      |  SELF-CORRECTION  |
|  - Parse   |     |  - Step-by-  |      |  - Dom State  |      |  - Retry strategies|
|  - Sub-task|     |    step exec |      |  - CAPTCHA det|      |  - Alternative URLs|
|  - Classify|     |  - Risk gate |      |  - Obstacles  |      |  - Locator fallback|
+------------+     +--------------+      +---------------+      +-------------------+
                          |                      |                        |
                          v                      v                        v
            +--------------------------------------------------------------------+
            |                      BROWSER AUTOMATION LAYER                      |
            |      (browser/playwright_browser.py, locators.py, navigation.py)   |
            |   - Chromium headless/headed instance                              |
            |   - Smart wait (domcontentloaded + content heuristics)             |
            |   - Anti-bot / login wall detection                                |
            +--------------------------------------------------------------------+
                          |
                          v
            +--------------------------------------------------------------------+
            |                    SEARCH & FILTERING ENGINE                       |
            |   (search/search_manager.py, providers.py, relevance_filter.py)   |
            |   - DuckDuckGo / Bing / Google / Wikipedia / Direct URL engine     |
            |   - URL sanitization, SSRF prevention, deduplication               |
            |   - Token overlap + semantic similarity + domain rank scoring      |
            +--------------------------------------------------------------------+
                          |
                          v
            +--------------------------------------------------------------------+
            |                       EXTRACTION ENGINE                            |
            |  (extraction/page_extractor.py, content_cleaner.py, structured.py) |
            |  - Article text, table/list data, headings, timestamps, pricing    |
            |  - Boilerplate / ad / cookie banner cleaning                       |
            +--------------------------------------------------------------------+
                          |
                          v
            +--------------------------------------------------------------------+
            |                    RAG & SYNTHESIS PIPELINE                        |
            |  (rag/document_processor.py, chunker.py, vector_store.py, etc.)    |
            |  - SentenceTransformers (all-MiniLM-L6-v2) / SQLite Vector Store   |
            |  - Hybrid dense + BM25 keyword retrieval                           |
            |  - Ollama (llama3.2:3b) answer generator with source citations     |
            +--------------------------------------------------------------------+
                          |
                          v
            +--------------------------------------------------------------------+
            |                    VERIFIER & EXPERIENCE MEMORY                    |
            |    (agent/verifier.py, memory/experience_memory.py, task_history)  |
            |  - Verifies claim support, page depth, completion vs partial       |
            |  - SQLite stores query strategies, locator rules, error patterns   |
            +--------------------------------------------------------------------+
```

---

## 📁 Project Structure

```
web-browsing-agent/
├── app.py                     # Streamlit web application & control dashboard
├── config.py                  # Pydantic BaseSettings with typed environment defaults
├── requirements.txt           # Pinned dependency requirements
├── .env.example               # Template environment configuration file
├── .gitignore                 # Standard Python/IDE/temporary file ignore list
├── README.md                  # Complete documentation and setup manual
├── agent/
│   ├── __init__.py
│   ├── agent.py               # Master autonomous research orchestrator
│   ├── executor.py            # Action dispatch and telemetry collector
│   ├── observer.py            # DOM state inspector and barrier detector
│   ├── planner.py             # Natural-language goal parser and plan builder
│   ├── self_correction.py     # Diagnostic recovery engine & alternative retries
│   ├── task_state.py          # Pydantic models for tasks, plans, actions, and metrics
│   └── verifier.py            # Strict criteria auditor (verifies page depth and evidence)
├── browser/
│   ├── __init__.py
│   ├── locators.py            # Accessible selectors with site-specific fallbacks
│   ├── navigation.py          # Bounded content waits, cookie dismissals, redirect resolution
│   └── playwright_browser.py  # Playwright browser lifecycle manager & diagnostic screenshots
├── search/
│   ├── __init__.py
│   ├── providers.py           # DuckDuckGo, Bing, Google, Wikipedia, Amazon India providers
│   ├── relevance_filter.py    # Deduplication, lexical + semantic scoring, explanation generator
│   ├── result_parser.py       # Search page parser with tracking redirect unwrapping
│   └── search_manager.py      # Search coordinator with multi-provider fallback
├── extraction/
│   ├── __init__.py
│   ├── content_cleaner.py     # Boilerplate, script, ad, and navigation stripper
│   ├── page_extractor.py      # Article body, metadata, headings, and table parser
│   └── structured_extractor.py# Price, rating, and hardware/course specification regex parser
├── rag/
│   ├── __init__.py
│   ├── answer_generator.py    # Evidence-grounded synthesis using Ollama or fallback
│   ├── chunker.py             # Sliding window chunker with metadata preservation
│   ├── document_processor.py  # Bridges extracted pages into vector embeddings
│   ├── embeddings.py          # Lazy-loaded SentenceTransformers with deterministic fallback
│   ├── retriever.py           # Hybrid dense + lexical retrieval with deduplication
│   └── vector_store.py        # Persistent SQLite-backed vector store with cosine search
├── memory/
│   ├── __init__.py
│   ├── experience_memory.py   # SQLite persistence of successful locator and search strategies
│   └── task_history.py        # Complete execution trajectory repository
├── safety/
│   ├── __init__.py
│   ├── human_intervention.py  # CAPTCHA, Cloudflare, and login wall detection
│   ├── risk_assessor.py       # Low/Medium/High risk action gate & read-only enforcement
│   └── url_validator.py       # SSRF protection, loopback/private subnet blocking
├── ui/
│   ├── __init__.py
│   └── components.py          # Custom styled metrics, tables, evidence cards, and status badges
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Ephemeral local HTTP test fixture server and mock pages
│   ├── test_end_to_end.py     # Full autonomous research loop and step ceiling tests
│   ├── test_extraction.py     # HTML cleaning, table formatting, and spec extraction tests
│   ├── test_navigation.py     # Playwright navigation, timeouts, and CAPTCHA detection
│   ├── test_planner.py        # Task classification and plan construction tests
│   ├── test_rag.py            # Chunking, vector indexing, retrieval, and synthesis tests
│   ├── test_result_filtering.py # Link extraction, redirect unwrapping, and ranking tests
│   ├── test_safety.py         # URL validation, SSRF blocking, and risk gate tests
│   └── test_verifier.py       # Criteria verification and search vs content page distinction
├── data/                      # Persistent databases and diagnostic screenshots
└── logs/                      # Structured operational logs
```

---

## 🚀 Key Features

1. **Multi-Source Autonomous Exploration**:
   - Classifies requests as `SEARCH_ONLY`, `RESEARCH`, `COMPARISON`, `NAVIGATION`, or `EXTRACTION`.
   - Dispatches queries to DuckDuckGo, Bing, Google, Wikipedia, or Amazon India.
   - Decodes search redirects (e.g. `/url?q=...`, `uddg` parameters).
2. **Deep Content Navigation (Beyond Search Pages)**:
   - Does **not** stop at search results; navigates into destination URLs.
   - Uses bounded content heuristics (`domcontentloaded` + content polling), avoiding arbitrary fixed sleeps.
   - Automatically handles cookie banners and modal overlays.
3. **Structured Spec Extraction**:
   - Parses prices (₹, $, Free), ratings (`4.5 out of 5 stars`), hardware specs (RAM, Storage, Processor), and course syllabi.
   - Converts HTML `<table>` elements into Markdown tables.
4. **Hybrid RAG Pipeline**:
   - Uses `all-MiniLM-L6-v2` SentenceTransformers with sliding-window chunking.
   - Persistent SQLite vector store with exact NumPy cosine distance.
   - Task-scoped collections prevent cross-task contamination.
   - Grounded synthesis with clickable source citations `[Source Title](URL)`.
   - Transparent deterministic fallback if Ollama is unreachable.
5. **Self-Correction & Recovery**:
   - Diagnoses failed actions (navigation timeout, empty page, 0 results).
   - Generates alternative actions (broadened queries, next candidate URLs).
   - Enforces max-retry and step limits.
6. **Strict Task Verification**:
   - Rejects false completion if only search results were viewed.
   - Evaluates evidence volume, comparable entities, and source depth.
   - Emits confidence scores and explicit disclosures of limitations.
7. **Safety & Security**:
   - Rejects dangerous schemes (`javascript:`, `file:`, `data:`).
   - Blocks private subnets (SSRF protection: 127.0.0.1, 10.0.0.0/8, 192.168.0.0/16, AWS metadata 169.254.169.254).
   - Read-only browsing by default; gates high-risk operations (purchases, password fills).
8. **Experience Memory**:
   - Persists successful strategies and failure patterns in SQLite across runs.

---

## 💻 Windows Setup & Installation

### Step 1: Clone and Enter the Project Directory
```powershell
cd C:\Users\ADILAKSHMI\web-browsing-agent
```

### Step 2: Set Up Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Install Playwright Chromium Browser
```powershell
playwright install chromium
```

### Step 5: Start Ollama (Local LLM Backend)
1. Install [Ollama for Windows](https://ollama.com/download/windows).
2. Open a terminal or start the Ollama service:
```powershell
ollama serve
```
3. Pull the configured model:
```powershell
ollama pull llama3.2:3b
```
*(Note: If Ollama is not installed or offline, the agent automatically and transparently uses its built-in deterministic synthesizer.)*

### Step 6: Configure Environment (Optional)
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

---

## 🧪 Running Automated Tests

The project includes 30 automated tests in `pytest` spanning all required modules and featuring an ephemeral local HTTP test fixture server for deterministic, offline testing.

Run all tests:
```powershell
pytest -v
```

Expected result:
```
======================= 30 passed in 129s =======================
```

### Test Suite Coverage Breakdown:
| Test File | Covered Functionality | Status |
|-----------|------------------------|--------|
| `test_planner.py` | Query parsing, domain detection, completion criteria | ✅ PASSED |
| `test_result_filtering.py` | Link extraction, redirect unwrapping, ranking, deduplication | ✅ PASSED |
| `test_navigation.py` | Playwright launch, smart wait, timeouts, CAPTCHA detection | ✅ PASSED |
| `test_extraction.py` | Boilerplate removal, markdown tables, pricing/specs extraction | ✅ PASSED |
| `test_rag.py` | Chunking, vector indexing, hybrid retrieval, answer generator | ✅ PASSED |
| `test_verifier.py` | Task completion verification, search vs article distinction | ✅ PASSED |
| `test_safety.py` | SSRF prevention, scheme rejection, risk gating, SQLite memory | ✅ PASSED |
| `test_end_to_end.py` | Full autonomous research flow, self-correction, step ceilings | ✅ PASSED |

---

## 🖥️ Launching the Streamlit Application

Start the interactive dashboard:
```powershell
streamlit run app.py
```

The browser will open at `http://localhost:8501`.

### Interactive UI Features:
- **Natural-Language Task Box**: Enter any research goal or select one of the built-in quick templates.
- **Agent Controls**: Toggle visible vs headless browser, configure Ollama model, choose search engine, and adjust page limits.
- **Live Action Log**: Stream real-time step execution directly to the screen.
- **Grounded Answer Tab**: Evidence-based answer with clickable source citations and audit verdict.
- **Collected Evidence Tab**: View extracted text snippets, price tags, star ratings, and specifications.
- **Search Candidates Tab**: Inspect candidate URLs with relevance scores and selection rationales.
- **Experience Memory Tab**: Inspect learned strategies and clear memory.

---

## 🔍 Verified Functionality vs Disclosed Limitations

- **Verified Working**:
  - Full autonomous research loop on local and accessible public web pages.
  - Multi-provider search query building (DuckDuckGo, Bing, Google, Wikipedia, Amazon).
  - Deep navigation into actual destination web pages via Playwright.
  - Spec extraction (prices, ratings, technical details, tables).
  - SentenceTransformers vector embedding and persistent SQLite vector storage.
  - Grounded answer generation with clickable links via Ollama (`llama3.2:3b`) and deterministic fallback.
  - Self-correction recovering from failed navigations.
  - SSRF protection and risk classification.
  - All 30 unit, integration, and end-to-end tests passing.
- **External Limitations Disclosed**:
  - Live search engines (Google, Amazon) frequently display Cloudflare/CAPTCHA challenges to automated browsers. When encountered, the agent flags an obstacle, requests human intervention, or self-corrects to fallback providers.
  - On low-spec Windows machines running Ollama on CPU, local LLM generation may take 30–60 seconds. A default 90-second timeout with deterministic fallback prevents hangs.
