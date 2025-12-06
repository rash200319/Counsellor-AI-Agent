# pip install llama-index llama-index-core llama-index-embeddings-huggingface llama-index-memory-mem0 llama-index-llms-groq
import os
import sys
import asyncio
try:
    from llama_index.llms.groq import Groq
    from llama_index.core.agent import ReActAgent
    from llama_index.core.tools import FunctionTool
    from llama_index.core import Settings
    from llama_index.core.tools import QueryEngineTool
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.memory.mem0 import Mem0Memory
    from llama_index.core.chat_engine import SimpleChatEngine
    from llama_index.tools.tavily_research import TavilyToolSpec
    from llama_index.core.storage import StorageContext
    from llama_index.core import load_index_from_storage
except ImportError:
    print("One or more required LlamaIndex packages are missing.")
    print("# pip install llama-index llama-index-core llama-index-embeddings-huggingface llama-index-memory-mem0 llama-index-llms-groq llama-index-tools-tavily")
    sys.exit(1)


os.environ["MeM0_API_KEY"] = "m0-ymzlsDGGZpvPtu9arGk9yWgR3xcPcIC512ThJbOV"  # Replace with your actual API key
os.environ["TAVILY_API_KEY"] = "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"

MODEL_NAME = "llama-3.1-8b-instant"
API_KEY = "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" # Replace with your actual API key
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5" 
KNOWLEDGE_BASE = "./data/"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 20
OUTPUT_TOKENS = 512 
PERSIST_DIR = "./storage"
crisis_keywords = ["suicide","kill myself","end my life"]

def get_llm(model_name, api_key):
    return Groq(model=model_name, api_key=api_key, temperature=0.7)

def initialize_settings():
    Settings.llm = get_llm(MODEL_NAME, API_KEY)
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    Settings.num_output = OUTPUT_TOKENS 
    Settings.node_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP) 

def apply_guidelines(user_input, generated_response):
    # crisis check
    if any(keyword in user_input.lower() for keyword in crisis_keywords):
        return (
            "\n🚨 **Immediate Crisis Notice** 🚨\n"
            "I’m really concerned for your safety. You deserve help right now. "
            "Please talk to someone you trust or call a hotline immediately.\n\n"
            "**In the US, you can call or text 988.**"
        )

    text = generated_response.lower()

    is_failure_message = "i'm not able to respond" in text or "i'm having trouble connecting" in text

    # empathy check
    empathy_phrases = [
        "i understand how you feel",
        "i'm sorry to hear that",
        "that sounds really tough",
        "i'm here to help",
        "i care about your well-being"
    ]
    shows_empathy = any(phrase in text for phrase in empathy_phrases)
    if not shows_empathy and not is_failure_message:
        generated_response = "I want you to know that I care about your well-being. " + generated_response
    return generated_response

import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
# NOTE: Settings must be initialized before this function is called
# from llama_index.core import Settings 

def load_index(folder_path: str, persist_dir: str):
    """Loads a persisted index or creates a new one if not found."""
    
    # --- Part 1: Create and Persist Index ---
    if not os.path.exists(persist_dir):
        print(f"Index not found at {persist_dir}. Creating and persisting new index...")
        os.makedirs(persist_dir, exist_ok=True) 

        if not os.path.exists(folder_path) or not os.listdir(folder_path):
            print(f"Error: Knowledge base directory '{folder_path}' is empty or does not exist.")
            # Return an empty query engine to prevent crashing
            return VectorStoreIndex([]).as_query_engine() 
            
        # Documents are loaded and index is built
        documents = SimpleDirectoryReader(folder_path).load_data()
        index = VectorStoreIndex.from_documents(documents)
        
        # Save the index to disk
        index.storage_context.persist(persist_dir=persist_dir)
        
    # --- Part 2: Load Persisted Index ---
    else:
        print(f"Loading index from persisted directory: {persist_dir}")
        
        # Load storage context using the version-compatible method
        # This loads all components (vector store, index store, etc.)
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        
        # Load the index from the storage context
        index = load_index_from_storage(storage_context)
    
    # --- Final Step: Return Query Engine ---
    return index.as_query_engine()

initialize_settings()

context = {"user_id": "1"}
memory_from_client = Mem0Memory.from_client(
    context=context,
    api_key=os.environ["MeM0_API_KEY"],
    search_msg_limit=10,  # Default is 10
)

query_engine = load_index(KNOWLEDGE_BASE,PERSIST_DIR) 
mental_health_tool = QueryEngineTool.from_defaults(query_engine,
                                             name = "mental_health_tips"
                                            ,description="A RAG tool engine with some basic facts regarding mental health") 

tavily_tool = TavilyToolSpec(api_key=os.environ["TAVILY_API_KEY"])

# Line 89 (Corrected code)
react_agent = ReActAgent(
    tools=[mental_health_tool] + tavily_tool.to_tool_list(),
    llm=Settings.llm,
    memory=memory_from_client,
    verbose=True,
    system_prompt=(
        "**CRITICAL START:** You are a friendly, compassionate, and responsible mental health counselor. "
        "Your first and most important rule is: **If the user's input is ONLY a greeting (like 'hi', 'hello', 'hey', 'good morning', etc.), you MUST respond with a warm greeting and ask how you can help, and you MUST NOT use any tools.**"
        
        "**RULES FOR COMPLEX QUERIES:** "
        "1. Prioritize using the `mental_health_tips` tool only when the user asks for specific advice, facts, or information related to mental health. "
        "2. Use the web search tool (`tavily_search`) only for current events or external information not in your knowledge base. "
        "3. You MUST always respond with empathy and NEVER provide a medical diagnosis. "
        "4. If you detect that the user may be in crisis, provide them with appropriate resources and urge them to seek immediate help. "
    ),
    max_iterations=50,
)
memory_from_client.reset()


print("--- 💬 Mental Health Assistant Initialized ---")
print("Model:", MODEL_NAME)
print("Type 'exit' or 'quit' to end the session.")
print("-" * 40)


async def main_chat_loop():
    print("--- 💬 Mental Health Assistant Initialized ---")
    print("Model:", MODEL_NAME)
    print("Type 'exit' or 'quit' to end the session.")
    print("-" * 40)

    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "sup", "yo", "hii", "hiii", "hey there"]
    
    thank_you_keywords = ["thank you", "thanks", "thank u", "appreciate", "appreciate it", "appreciate your help", "thanks for helping", "thanks for your help", "thx"]
    
    closing_responses = [
        "You're very welcome! 😊 I'm happy to help. Take care of yourself!",
        "My pleasure! 💙 Remember, I'm always here if you need to talk.",
        "You're so welcome! Take good care, and be kind to yourself.",
        "Happy to help! 🌟 Wishing you all the best on your journey.",
        "Glad I could assist! Remember, your well-being matters. 💪"
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # Check if input is just a greeting
            user_lower = user_input.lower().strip()
            is_greeting = (
                user_lower in greeting_keywords or
                all(word in greeting_keywords for word in user_lower.split() if word)
            )
            
            # Check if input is a thank you
            is_thank_you = any(keyword in user_lower for keyword in thank_you_keywords)

            if is_greeting:
                final_response = "Hello! 👋 It's wonderful to meet you. How can I support you today?"
            elif is_thank_you:
                import random
                final_response = random.choice(closing_responses)
            else:
                # 1. Use asynchronous run method
                result = await react_agent.run(user_input)
                
                # The result object contains the final response
                raw_response_object = result.response 

                # 2. Extract the actual text content from the response object
                if hasattr(raw_response_object, "message"):
                    raw_text = raw_response_object.message
                elif hasattr(raw_response_object, "content"):
                    raw_text = raw_response_object.content
                else:
                    raw_text = str(raw_response_object)
                    
                # 3. Apply safety guidelines using the extracted raw_text string
                final_response = apply_guidelines(user_input, raw_text)
            
            print("Counselor:", final_response)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Counselor: I'm sorry, I'm having trouble connecting right now. Please try again.")

if __name__ == "__main__":
    # Ensure the code runs the main async function
    try:
        asyncio.run(main_chat_loop())
    except KeyboardInterrupt:
        print("\nExiting chat loop.")