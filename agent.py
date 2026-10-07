import json
import os
from datetime import date

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from groq import BadRequestError, Groq

from build_site import build
from prompt import SYSTEM_PROMPT
from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

MAX_STEPS = 25        # safety limit, so the agent can't loop forever
MAX_BAD_CALLS = 3     # how many invalid tool calls we tolerate

MAX_CONTEXT_CHARS = 20000   # about 5,000 tokens, safely under Groq's 8,000 limit


def context_size(messages: list[dict]) -> int:
    """Rough size of the conversation, counted in characters."""
    total = 0
    for message in messages:
        total += len(str(message.get("content") or ""))
        total += len(json.dumps(message.get("tool_calls", "")))
    return total


def trim_context(messages: list[dict], article_positions: dict):
    """Replace the oldest article texts until the conversation is small enough."""
    for url, position in list(article_positions.items()):
        if context_size(messages) <= MAX_CONTEXT_CHARS:
            break
        messages[position]["content"] = (
            "[Article text removed to save space. Fetch it again if you still need it.]"
        )
        del article_positions[url]


def run_agent():
    load_dotenv(override=True)
    client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=5)
    model = os.environ["GROQ_MODEL"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Today is {date.today().isoformat()}. "
                                    "Find the important AI news from the last day and save it for the website."},
    ]
    article_positions = {}   # url -> position of its text in messages
    bad_calls = 0

    try:
        for step in range(1, MAX_STEPS + 1):
            trim_context(messages, article_positions)
            try:
                response = client.chat.completions.create(
                    model=model, messages=messages, tools=TOOL_SCHEMAS,
                    tool_choice="auto", temperature=0.3,
                )
            except BadRequestError:
                # The model produced a tool call that isn't valid JSON
                bad_calls += 1
                print(f"[step {step}] Invalid tool call from the model ({bad_calls}/{MAX_BAD_CALLS}).")
                if bad_calls >= MAX_BAD_CALLS:
                    print("Stopped: too many invalid tool calls.")
                    return
                messages.append({"role": "user", "content":
                                 "Your last tool call was not valid. Try again with a valid tool call."})
                continue

            message = response.choices[0].message

            # No tool calls means the model is done
            if not message.tool_calls:
                print("\n=== Agent report ===\n")
                print(message.content)
                return

            # Remember what the model asked for
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [call.model_dump() for call in message.tool_calls],
            })

            # Run each tool the model asked for, and send back the result
            for call in message.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments or "{}")
                print(f"[step {step}] {name}({str(args)[:80]})")
                try:
                    result = TOOL_FUNCTIONS[name](**args)
                except Exception as e:
                    result = f"Error: {e}"
                if not isinstance(result, str):
                    result = json.dumps(result, ensure_ascii=False)
                if name == "fetch_article":
                    article_positions[args.get("url")] = len(messages)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

                # Once an item is saved, its article text is no longer needed
                if name == "save_item":
                    url = args.get("item", {}).get("source_url")
                    position = article_positions.pop(url, None)
                    if position is not None:
                        messages[position]["content"] = "[Article text removed: this article is already saved.]"

        print("Stopped: reached the maximum number of steps.")

    finally:
        build()   # runs however the agent ends: finished, stopped, or crashed


if __name__ == "__main__":
    run_agent()