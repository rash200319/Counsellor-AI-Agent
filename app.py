"""Streamlit web UI for the mental health assistant."""

from __future__ import annotations

import asyncio
import concurrent.futures
import os

import streamlit as st

from counsellor.chat import get_reply

DISCLAIMER = (
    "**Educational demo only.** This assistant is not a licensed therapist "
    "and is not a substitute for professional mental health care. "
    "If you are in crisis, call or text **988** (US) or local emergency services."
)

_SECRET_KEYS = (
    "GROQ_API_KEY",
    "MEM0_API_KEY",
    "TAVILY_API_KEY",
    "GROQ_MODEL",
    "COUNSELLOR_USER_ID",
)


def _inject_streamlit_secrets() -> None:
    """Map Streamlit Cloud secrets into env vars for counsellor.config."""
    try:
        for key in _SECRET_KEYS:
            if key in st.secrets and not os.getenv(key):
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass


def _run_async(coro):
    """Run async code from Streamlit (handles existing event loops)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


@st.cache_resource
def _get_agent():
    from counsellor.agent import build_agent

    return build_agent()


st.set_page_config(page_title="Mental Health Assistant", page_icon="💬", layout="centered")
_inject_streamlit_secrets()

st.title("Mental Health Assistant")
st.info(DISCLAIMER)

try:
    _get_agent()
except SystemExit:
    st.error("Missing API keys. Set GROQ_API_KEY, MEM0_API_KEY, and TAVILY_API_KEY.")
    st.stop()
except Exception as e:
    st.error(f"Failed to start the assistant: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What's on your mind?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = _run_async(get_reply(prompt))
            except Exception as e:
                print(f"An error occurred: {e}")
                reply = (
                    "I'm sorry, I'm having trouble connecting right now. Please try again."
                )
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
