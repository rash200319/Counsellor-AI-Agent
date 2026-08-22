"""CLI entrypoint for the mental health assistant."""

from __future__ import annotations

import asyncio
import sys

from counsellor import config
from counsellor.agent import build_agent
from counsellor.chat import get_reply


async def main_chat_loop() -> None:
    # Eager init so missing keys / index errors surface before first message
    build_agent()

    print("--- Mental Health Assistant Initialized ---")
    print("Model:", config.MODEL_NAME)
    print("Demo only — not a substitute for professional care.")
    print("Type 'exit' or 'quit' to end the session.")
    print("-" * 40)

    while True:
        user_input = input("You: ")
        if user_input.lower().strip() in {"exit", "quit"}:
            break

        try:
            final_response = await get_reply(user_input)
            print("Counselor:", final_response)
        except Exception as e:
            print(f"An error occurred: {e}")
            print(
                "Counselor: I'm sorry, I'm having trouble connecting right now. "
                "Please try again."
            )


if __name__ == "__main__":
    try:
        asyncio.run(main_chat_loop())
    except KeyboardInterrupt:
        print("\nExiting chat loop.")
        sys.exit(0)
