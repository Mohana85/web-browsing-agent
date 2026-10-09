# Web Browsing Agent with RAG

A Python-based web research agent that searches the internet, opens relevant websites, collects information, and generates answers with source links.

## Features

- Search the web using different search providers.
- Open websites and extract useful content.
- Use RAG to find relevant information from collected pages.
- Generate answers using Ollama.
- Retry failed actions and try alternative search results.
- Show source links along with answers.
- Detect CAPTCHA and login pages.
- Store task history and useful search strategies.
- Provide a simple Streamlit interface.

## Technologies Used

- Python
- Streamlit
- Playwright
- Ollama
- Sentence Transformers
- SQLite
- Pytest

## Project Setup


### 1.Clone the Repository
Make sure Git is installed on your computer. Open Command Prompt (CMD) or PowerShell and run:
```bash
git clone https://github.com/Mohana85/web-browsing-agent
```
Move into the project folder:
```bash
cd web-browsing-agent
```
### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set up Ollama

Install Ollama from [ollama.com](https://ollama.com/) and download the model:

```bash
ollama pull llama3.2:3b
```

### 5. Run the application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Run Tests

```bash
pytest -v
```

## How It Works

1. Enter a research task in the application.
2. The agent searches for relevant websites.
3. It opens pages and extracts their content.
4. RAG retrieves useful information from the collected content.
5. The agent generates an answer with source links.
6. If an action fails, it can retry or use another result.

## Project Structure

- `agent/` – Task planning and execution
- `browser/` – Browser automation
- `search/` – Web search and result filtering
- `extraction/` – Website content extraction
- `rag/` – Document retrieval and answer generation
- `memory/` – Task history and stored strategies
- `safety/` – URL validation and risk checks
- `tests/` – Automated tests
- `ui/` – Interface components
- `app.py` – Main application

## Limitations

- Some websites may block automated browsing or show CAPTCHAs.
- Answer quality depends on the available website content.
- Local model responses may take longer on slower computers.
