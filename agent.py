import json
import os
from datetime import date
from build_site import build


# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from groq import Groq

from prompt import SYSTEM_PROMPT
from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

MAX_STEPS = 25   # safety limit, so the agent can't loop forever


def run_agent():
    load_dotenv(override=True)
    client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=5)
    model = os.environ["GROQ_MODEL"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Today is {date.today().isoformat()}. "
                                    "Find the important AI news from the last 2 days and save it for the website."},
    ]

    article_positions = {}   # positions of fetch_article results in messages
    for step in range(1, MAX_STEPS + 1):
                # Keep only the newest article text; replace older ones with a short note
        
        response = client.chat.completions.create(
            model=model, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto"
        )
        message = response.choices[0].message

        # No tool calls means the model is done: print its final report
        if not message.tool_calls:
            print("\n=== Agent report ===\n")
            print(message.content)
            build()
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
    build()


if __name__ == "__main__":
    run_agent()