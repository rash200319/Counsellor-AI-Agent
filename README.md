# Mental Health Assistant

A compassionate AI-powered mental health counselor **demo** built with LlamaIndex, Groq, and a ReAct agent. Chat via CLI or a **Streamlit** web UI. Uses lightweight keyword RAG over a local knowledge base, optional Tavily web search, and Mem0 conversation memory.

**Educational / portfolio use only.** Not a licensed therapist. Not a substitute for professional mental health care. If you are in crisis, call or text **988** (US) or local emergency services.

---

## Features

- Empathetic counselor-style replies (demo)
- ReAct agent with reasoning + tools
- Lightweight keyword RAG over `data/mental_health_tips.txt` (no torch / local embeddings — lower memory for free hosts)
- Web search via Tavily
- Mem0 conversation memory (not cleared on startup)
- Crisis keyword detection **before** the agent runs
- Counselling-only scope guardrail for unrelated requests
- Prompt-injection and secret/code disclosure protection
- Shared reply pipeline for CLI and Streamlit

---

## Prerequisites

- Python 3.10+
- API keys:
  - [Groq](https://console.groq.com)
  - [Mem0](https://mem0.ai)
  - [Tavily](https://tavily.com)

---

## Installation

```bash
cd Counsellor-AI-Agent
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
```

If you previously installed `torch` / Gradio for an older version, use a fresh venv so those heavy packages are gone.

---

## Configuration

1. Copy the example env file and fill in keys:

```bash
# Windows
copy .env.example .env

# macOS / Linux
# cp .env.example .env
```

2. Edit `.env`:

```
GROQ_API_KEY=your_groq_api_key
MEM0_API_KEY=your_mem0_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Optional:

| Variable | Purpose | Default |
| --- | --- | --- |
| `GROQ_MODEL` | Groq model id | `openai/gpt-oss-20b` |
| `COUNSELLOR_USER_ID` | Mem0 user partition | `1` |
| `PORT` | Streamlit listen port (hosts set this) | `8501` locally |

Never commit `.env` (it is gitignored).

### Other settings

Defined in `counsellor/config.py`:

| Setting | Default |
| --- | --- |
| Model | `openai/gpt-oss-20b` (override with `GROQ_MODEL`) |
| Knowledge base | `./data/` |

### Knowledge base

Primary source: [`data/mental_health_tips.txt`](data/mental_health_tips.txt). Topics include anxiety, grounding, stress, sleep, low mood, burnout, loneliness, self-compassion, and when to seek help.

Add more `.txt` / `.md` files under `data/` as needed. Sections split on `---` are searched with keyword overlap (no vector DB).

```
Counsellor-AI-Agent/
├── app.py                 # Streamlit UI
├── myagent.py             # CLI
├── counsellor/            # shared library
├── data/
│   └── mental_health_tips.txt
├── Procfile               # Render start command
├── .env.example
├── requirements.txt
└── README.md
```

---

## Usage

### CLI

```bash
python myagent.py
```

Type `exit` or `quit` to leave.

### Streamlit UI (local)

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

---

## Hosting

### Why this version fits free tiers better

Older builds used **PyTorch + HuggingFace embeddings**, which often exceed Render / free RAM limits. This version uses **keyword RAG** and **Streamlit** instead of Gradio + torch.

### Render

1. Push the repo to GitHub (no `.env`).
2. Create a **Web Service** from that repo.
3. Runtime: Python 3.
4. Build: `pip install -r requirements.txt`
5. Start: uses [`Procfile`](Procfile)  
   `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
6. Add env vars / secrets:
   - `GROQ_API_KEY`
   - `MEM0_API_KEY`
   - `TAVILY_API_KEY`
   - optional: `GROQ_MODEL`, `COUNSELLOR_USER_ID`

### Streamlit Community Cloud

1. Push to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select repo, main file `app.py`.
4. In **Secrets**, add the same API keys (TOML format), e.g.:

```toml
GROQ_API_KEY = "..."
MEM0_API_KEY = "..."
TAVILY_API_KEY = "..."
```

Note: Streamlit Cloud secrets are not automatically env vars unless you map them. This project reads `os.environ` / `.env`. On Streamlit Cloud, either set secrets as environment variables in the dashboard if available, or we can add a small secrets bridge — locally `.env` works as usual.

For Streamlit Cloud, add this pattern is already supported if you paste secrets into the app's Secrets and also expose them — Streamlit injects `st.secrets`. A tiny bridge is included in `counsellor/config.py` via dotenv only; for Community Cloud, set the keys in **Advanced settings → Secrets** using environment-style if your plan supports it, or put them in `.streamlit/secrets.toml` locally (never commit).

**Practical tip:** Prefer **Render** with normal environment variables for this project — it matches `_require_env` with no extra wiring.

### Hugging Face

Free **Static** Spaces cannot run Python. Gradio Spaces may require paid access on your account. Use Render or Streamlit Community Cloud instead.

### Hosting caveats

- Keep API keys in platform secrets — never in the repo.
- Demo only — show the disclaimer.
- Mem0 defaults to shared `COUNSELLOR_USER_ID=1` (not multi-user auth).

---

## How it works

1. Load API keys and initialize Groq LLM, Mem0, and tools (no local embedding model).
2. For each user message:
   - **Crisis keywords** → immediate 988 / crisis notice (agent skipped)
   - **Prompt/code/secret requests** → privacy refusal (agent skipped)
   - **Clear unrelated requests** → scope refusal (agent skipped)
   - **Greeting / thanks** → short canned reply
   - Otherwise → ReAct agent (`mental_health_tips` keyword search + optional Tavily), then light empathy fallback
3. Mem0 keeps conversation context; it is **not** reset on startup.

## Guardrails

The shared `counsellor.chat.get_reply` pipeline checks every message before it
reaches the LLM. It refuses obvious programming and general-purpose requests,
as well as requests for system/developer prompts, source code, environment
variables, credentials, API keys, or hidden tool/memory details. The agent's
system prompt repeats these restrictions, and responses are checked for common
prompt/secret leakage markers before being shown to the user.

These are application guardrails, not a security boundary: keep `.env` out of
version control, use platform secret storage, and never place real credentials
in prompts, logs, or the knowledge base.

---

## Crisis detection

Keywords include (among others): `suicide`, `kill myself`, `end my life`, `hurt myself`, `self-harm`, `want to die`.

When matched, the app returns crisis resources immediately and does not call the agent.

This is a simple keyword filter for a demo — not a clinical safety system.

---

## Troubleshooting

**Model not found (404)**  
Default is `openai/gpt-oss-20b`. Override with `GROQ_MODEL`.

**Mem0 `org_id` TypeError**  
Fixed by building `MemoryClient` without `org_id` in `counsellor/agent.py`.

**Out of memory on Render**  
Confirm `requirements.txt` has **no** `torch` / `sentence-transformers`. Use a fresh deploy after the slim update.

**Missing API key**  
Copy `.env.example` to `.env`, or set host env vars.

**Import errors**  
```bash
pip install -r requirements.txt
```

---

## Notes

- Use responsibly; encourage professional help for serious concerns.
- For educational and personal portfolio use.

**Last updated:** August 22, 2026
