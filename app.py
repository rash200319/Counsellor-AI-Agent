"""Gradio web UI for the mental health assistant."""

from __future__ import annotations

import os

import gradio as gr

from counsellor.agent import build_agent
from counsellor.chat import get_reply

DISCLAIMER = (
    "**Educational demo only.** This assistant is not a licensed therapist "
    "and is not a substitute for professional mental health care. "
    "If you are in crisis, call or text **988** (US) or local emergency services."
)


async def respond(message: str, history: list) -> str:
    try:
        return await get_reply(message)
    except Exception as e:
        print(f"An error occurred: {e}")
        return (
            "I'm sorry, I'm having trouble connecting right now. Please try again."
        )


def main() -> None:
    build_agent()

    chat = gr.ChatInterface(
        fn=respond,
        title="Mental Health Assistant",
        description=DISCLAIMER,
        examples=[
            "Hi",
            "How can I manage anxiety?",
            "I'm feeling stressed at work",
        ],
    )
    # 0.0.0.0 + PORT makes local Docker / Hugging Face Spaces / Railway work
    chat.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860"))),
    )


if __name__ == "__main__":
    main()
