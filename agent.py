import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from neatlogs_tracer import TraceSession, send_trace

# Load environment configuration
load_dotenv()

def run_agent(task_prompt: str) -> str:
    """Entry point for the PatchPilot AI Agent with Neatlogs tracing."""
    session = TraceSession(
        workflow_name="patchpilot-agent",
        task_input={"prompt": task_prompt}
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        mock_output = (
            "[DEMO / MOCK RESULT] OpenAI API Key is not set in .env. "
            f"Simulated analysis for: '{task_prompt}' completed."
        )
        # Record a demo span so you can see the trace in Neatlogs immediately
        session.record_llm_call(
            name="patchpilot-code-analyzer",
            model="gpt-4o",
            input_data=task_prompt,
            output_data=mock_output,
            prompt_tokens=25,
            completion_tokens=20,
        )
        session.finish(final_output=mock_output)
        return mock_output

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are PatchPilot AI, an autonomous software engineering agent that analyzes "
                    "code, detects issues, and produces reliable code patches."
                ),
            },
            {"role": "user", "content": task_prompt},
        ],
    )

    content = response.choices[0].message.content or ""
    usage = response.usage

    session.record_llm_call(
        name="patchpilot-code-analyzer",
        model="gpt-4o",
        input_data=task_prompt,
        output_data=content,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
    )

    session.finish(final_output=content)
    return content


if __name__ == "__main__":
    task = "Analyze potential performance bottlenecks in a Python web service and recommend fixes."
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])

    print(f"Running PatchPilot Agent task: '{task}'...")
    result = run_agent(task)
    print("\nResult:\n")
    print(result)
