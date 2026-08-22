# Mental Health Assistant

A compassionate AI-powered mental health counselor **demo** built with LlamaIndex, Groq, and a ReAct agent. Chat via CLI or a Gradio web UI. Uses RAG over a local knowledge base, optional Tavily web search, and Mem0 conversation memory.

**Educational / portfolio use only.** Not a licensed therapist. Not a substitute for professional mental health care. If you are in crisis, call or text **988** (US) or local emergency services.

---

## Features

- Empathetic counselor-style replies (demo)
- ReAct agent with reasoning + tools
- RAG over `data/mental_health_tips.txt` (anxiety, stress, sleep, low mood, burnout, grounding, and more)
- Web search via Tavily
- Mem0 conversation memory (not cleared on startup)
- Crisis keyword detection **before** the agent runs
- Shared reply pipeline for CLI and Gradio
- Hostable Gradio UI (Hugging Face Spaces, Railway, Render, etc.)

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
| `PORT` | Gradio listen port | `7860` |

Never commit `.env` (it is gitignored).

### Other settings

Defined in `counsellor/config.py`:

| Setting | Default |
| --- | --- |
| Model | `openai/gpt-oss-20b` (override with `GROQ_MODEL`) |
| Embedding | `BAAI/bge-small-en-v1.5` |
| Knowledge base | `./data/` |
| Persist dir | `./storage/` |
| Chunk size / overlap | 512 / 20 |

### Knowledge base

Primary source: [`data/mental_health_tips.txt`](data/mental_health_tips.txt). Topics include:

- Everyday wellbeing (routine, movement, social connection, media limits)
- Anxiety, grounding, and panic support
- Stress, overwhelm, and low mood (self-help only — not diagnosis)
- Sleep, loneliness, work/burnout boundaries
- Self-compassion, CBT-style thought checks, wellness toolkit
- When to seek professional help / crisis resources

Add more `.txt` / `.pdf` files under `data/` as needed. On first run the index is built under `storage/`.

If you change documents after an index already exists, delete `storage/` so it rebuilds:

```bash
# Windows PowerShell
Remove-Item -Recurse -Force .\storage\*
```

```
Counsellor-AI-Agent/
├── app.py                 # Gradio UI (host entrypoint)
├── myagent.py             # CLI
├── counsellor/            # shared library
├── data/
│   └── mental_health_tips.txt
├── storage/               # auto-generated (do not commit secrets here)
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

### Gradio UI (local)

```bash
python app.py
```

Open the URL Gradio prints (usually `http://127.0.0.1:7860`).

---

## Hosting

Yes — you can host the Gradio app. Easiest path for this project: **Hugging Face Spaces**.

### Option A — Hugging Face Spaces (recommended)

1. Create a Space → SDK **Gradio** → Python 3.10+.
2. Upload / push this repo (`app.py`, `counsellor/`, `data/`, `requirements.txt`, etc.).
3. In Space **Settings → Variables and secrets**, add:
   - `GROQ_API_KEY`
   - `MEM0_API_KEY`
   - `TAVILY_API_KEY`
   - optional: `GROQ_MODEL`, `COUNSELLOR_USER_ID`
4. Space builds with `requirements.txt` and runs `app.py`.
5. First boot may be slow (downloads the embedding model). Prefer a Space with enough RAM/CPU (CPU basic can be tight with `torch`).

`app.py` already binds `0.0.0.0` and respects `PORT`, which Spaces/Railway need.

### Option B — Railway / Render / Fly.io

1. Deploy from GitHub as a Python web service.
2. Start command: `python app.py`
3. Set the same API keys as environment variables.
4. Expose the port Gradio uses (`PORT`, default `7860`).

Expect a larger slug/image because of `torch` + sentence-transformers.

### Option C — Temporary public link (no permanent host)

While running locally:

```python
# in a quick test you can pass share=True to chat.launch(...)
```

Gradio can print a temporary `*.gradio.live` URL. Fine for demos; not for a permanent portfolio link.

### Hosting caveats

- Keep API keys in platform secrets — never in the repo.
- This is a **demo**, not a clinical product. Show the disclaimer prominently.
- Mem0 memory is keyed by `COUNSELLOR_USER_ID` (default shared `1`). Multi-user prod would need per-user ids and auth (out of scope).
- Free tiers may sleep, rate-limit Groq/Mem0/Tavily, or struggle with cold starts + embeddings.

---

## How it works

1. Load API keys from `.env` (or host secrets) and initialize LLM, embeddings, Mem0, and tools.
2. For each user message:
   - **Crisis keywords** → immediate 988 / crisis notice (agent skipped)
   - **Greeting / thanks** → short canned reply
   - Otherwise → ReAct agent (RAG + optional Tavily), then a light empathy fallback
3. Mem0 keeps conversation context; it is **not** reset on startup.

---

## Crisis detection

Keywords include (among others): `suicide`, `kill myself`, `end my life`, `hurt myself`, `self-harm`, `want to die`.

When matched, the app returns crisis resources immediately and does not call the agent.

**Example**

```
You: I want to hurt myself
Counselor: **Immediate Crisis Notice**
...
**In the US, you can call or text 988.**
```

This is a simple keyword filter for a demo — not a clinical safety system.

---

## Troubleshooting

**Model not found (404)**  
`llama-3.1-8b-instant` was retired on Groq. Default is `openai/gpt-oss-20b`. Override with `GROQ_MODEL`.

**Mem0 `org_id` TypeError**  
Current `mem0ai` no longer accepts `org_id`. This project builds `MemoryClient` without those args in `counsellor/agent.py`.

**Missing API key**  
Copy `.env.example` to `.env` (or set host secrets).

**Stale RAG answers after editing `data/`**  
Delete `storage/` and restart so the index rebuilds.

**Import errors**  
```bash
pip install -r requirements.txt
```

**Slow first run / Space build**  
HuggingFace embedding model and PyTorch download on first use.

---

## Notes

- Use responsibly; encourage professional help for serious concerns.
- Crisis resources should always be offered when someone may be in danger.
- For educational and personal portfolio use.

**Last updated:** August 22, 2026
