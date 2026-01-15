#  Mental Health Assistant

A compassionate AI-powered mental health counselor built with LlamaIndex, Groq LLM, and ReAct Agent. This assistant provides mental health guidance, crisis support, and empathetic conversations.

---

##  Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Keys & Environment Variables](#api-keys--environment-variables)
- [How It Works](#how-it-works)
- [Crisis Detection](#crisis-detection)
- [Conversation Examples](#conversation-examples)
- [Troubleshooting](#troubleshooting)

---

##  Features

- **Compassionate AI Counselor**: Provides empathetic mental health guidance
- **ReAct Agent**: Uses reasoning and action-based approach for better responses
- **RAG System**: Retrieves mental health facts from knowledge base
- **Web Search**: Integrates Tavily for current mental health information
- **Memory Management**: Mem0 integration for conversation context and memory
- **Crisis Detection**: Identifies crisis keywords and provides immediate resources
- **Greeting & Thank You Detection**: Smart conversation flow management
- **Empathy Enforcement**: Ensures all responses include empathetic language

---

##  Prerequisites

- Python 3.8+
- pip (Python package manager)
- API Keys:
  - Groq API Key
  - Mem0 API Key
  - Tavily API Key

---

##  Installation

1. **Clone or download the project**:
   ```bash
   cd c:\Users\user\OneDrive\Desktop\myagent
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install required packages**:
   ```bash
   pip install llama-index llama-index-core llama-index-embeddings-huggingface llama-index-memory-mem0 llama-index-llms-groq llama-index-tools-tavily
   ```

---

##  Configuration

### API Keys

Update the following in `myagent.py`:

```python
os.environ["MeM0_API_KEY"] = "your_mem0_api_key_here"
os.environ["TAVILY_API_KEY"] = "your_tavily_api_key_here"
API_KEY = "your_groq_api_key_here"
```

**Get API Keys:**
- [Groq API](https://console.groq.com)
- [Mem0 API](https://mem0.ai)
- [Tavily API](https://tavily.com)

### Configuration Parameters

```python
MODEL_NAME = "llama-3.1-8b-instant"      # Groq model to use
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Embedding model
KNOWLEDGE_BASE = "./data/"               # Path to knowledge base documents
CHUNK_SIZE = 512                         # Size of text chunks
CHUNK_OVERLAP = 20                       # Overlap between chunks
OUTPUT_TOKENS = 512                      # Max output tokens
PERSIST_DIR = "./storage"                # Directory to persist index
```

### Knowledge Base Setup

1. Create a `data/` folder in the project directory
2. Add `.txt`, `.pdf`, or other document files with mental health information
3. The system will automatically index these documents on first run

```
myagent/
├── data/
│   ├── mental_health_tips.txt
│   ├── anxiety_guide.txt
│   └── depression_resources.txt
├── storage/              # Auto-generated index storage
├── myagent.py
├── README.md
└── .gitignore
```

---

##  Usage

### Running the Assistant

```bash
python myagent.py
```

### Example Conversations

**Greeting:**
```
You: hi
Counselor: Hello!  It's wonderful to meet you. How can I support you today?
```

**Thank You:**
```
You: thank you so much for your help
Counselor: You're very welcome!  I'm happy to help. Take care of yourself!
```

**Mental Health Question:**
```
You: How can I manage anxiety?
Counselor: I understand how you feel. [Uses mental_health_tips tool to provide guidance]
```

**Crisis Detection:**
```
You: I want to kill myself
Counselor:  **Immediate Crisis Notice** 
In the US, you can call or text 988.
```

**Exit:**
```
You: exit
```

---

##  Project Structure

```
myagent/
├── myagent.py              # Main application file
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── data/                   # Knowledge base documents (create this)
└── storage/                # Persisted index (auto-generated)
```

---

##  API Keys & Environment Variables

The assistant uses three main API services:

| Service | Purpose | Where to Get | Environment Variable |
|---------|---------|--------------|----------------------|
| Groq | LLM Model | console.groq.com | `API_KEY` |
| Mem0 | Memory Management | mem0.ai | `MeM0_API_KEY` |
| Tavily | Web Search | tavily.com | `TAVILY_API_KEY` |

---

##  How It Works

### 1. **Initialization**
- LLM, embeddings, and node parser are configured
- Knowledge base is indexed (or loaded from cache)
- Mem0 memory is initialized for conversation context
- ReAct Agent is created with mental health and search tools

### 2. **User Input Processing**
- **Greeting Detection**: If user says "hi", "hello", etc., responds with greeting
- **Thank You Detection**: If user says "thanks", responds with closing message
- **Regular Query**: Processes through ReAct Agent with tools
  - Retrieves mental health information from RAG
  - Can perform web searches if needed
  - Applies safety guidelines and empathy checks

### 3. **Response Generation**
- Agent reasons about user input
- Uses appropriate tools (mental_health_tips or web search)
- Applies guidelines:
  - Crisis detection
  - Empathy enforcement
  - Safety checks

### 4. **Memory Management**
- Mem0 stores conversation history
- Allows the assistant to remember context across sessions
- Improves personalization of responses

---

##  Crisis Detection

The assistant monitors for crisis keywords:
- "suicide"
- "kill myself"
- "end my life"

When detected, it immediately:
1. Stops normal processing
2. Shows crisis notice
3. Provides the 988 hotline (US)
4. Encourages seeking immediate help

**Crisis Keywords** (in `myagent.py`):
```python
crisis_keywords = ["suicide","kill myself","end my life"]
```

---

## 💬 Conversation Examples

### Example 1: Greeting
```
You: hello
Counselor: Hello! 👋 It's wonderful to meet you. How can I support you today?
```

### Example 2: Mental Health Advice
```
You: I'm feeling stressed at work
Counselor: I understand how you feel. [provides empathetic response with tips from knowledge base]
```

### Example 3: Thanks
```
You: thanks for your help!
Counselor: My pleasure! 💙 Remember, I'm always here if you need to talk.
```

### Example 4: Crisis
```
You: I want to hurt myself
Counselor: 🚨 **Immediate Crisis Notice** 🚨
I'm really concerned for your safety. Please call 988.
```

---

##  Troubleshooting

### Issue: "Index not found" error
**Solution**: Ensure `data/` folder exists with document files
```bash
mkdir data
# Add .txt or .pdf files to data/
```

### Issue: API Key errors
**Solution**: Verify all API keys are correctly set in `myagent.py`
```python
print(os.environ.get("MeM0_API_KEY"))  # Should not be None
```

### Issue: Module import errors
**Solution**: Reinstall packages
```bash
pip install --upgrade llama-index llama-index-core
```

### Issue: Slow responses
**Solution**: 
- Reduce `CHUNK_SIZE` for faster retrieval
- Check internet connection for web search
- Verify API rate limits

### Issue: Agent not responding to greetings
**Solution**: The greeting detection is built into the `main_chat_loop()`. Ensure you're running the latest version of `myagent.py`.

---

##  Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Groq API Docs](https://console.groq.com/docs)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [Tavily Search API](https://tavily.com/docs)
- [Mental Health Crisis Hotlines](https://988lifeline.org/)

---

##  License

This project is for educational and personal use.

---

##  Notes

- Always use the assistant responsibly for mental health support
- For serious mental health concerns, encourage users to seek professional help
- The assistant is NOT a replacement for professional mental health care
- Crisis resources should always be provided when needed

---

**Last Updated**: December 6, 2025
