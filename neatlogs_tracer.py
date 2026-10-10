"""
Neatlogs HTTP Injection Tracer for Python
Direct integration with Neatlogs regional ingest endpoint: https://ingest.neatlogs.com/v1/trace
"""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_INGEST_URL = "https://ingest.neatlogs.com/v1/trace"
PROJECT_ID = "b0860223-3c80-445d-a3f1-3002c0643197"


def get_api_key() -> str:
    key = os.getenv("NEATLOGS_API_KEY", "")
    return key.strip()


def send_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends a complete nested trace to the Neatlogs ingest endpoint.
    """
    api_key = get_api_key()
    if not api_key or api_key == "<your-project-api-key>":
        print("[Neatlogs Tracer] WARNING: NEATLOGS_API_KEY is not configured in .env!")
        return {"success": False, "error": "NEATLOGS_API_KEY missing"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if "project" not in trace:
        trace["project"] = PROJECT_ID

    try:
        res = requests.post(BASE_INGEST_URL, json=trace, headers=headers, timeout=10.0)
        if res.status_code == 200:
            data = res.json()
            print(f"[Neatlogs Tracer] [SUCCESS] Trace sent! Trace ID: {data.get('trace_id')} ({data.get('spans', 0)} spans)")
            return data
        else:
            print(f"[Neatlogs Tracer] [ERROR] Status {res.status_code}: {res.text}")
            return {"success": False, "status_code": res.status_code, "error": res.text}
    except Exception as e:
        print(f"[Neatlogs Tracer] [ERROR] Exception while sending trace: {e}")
        return {"success": False, "error": str(e)}


class TraceSession:
    """Helper to collect spans and submit them as one workflow trace."""

    def __init__(self, workflow_name: str, task_input: Any = None):
        self.workflow_name = workflow_name
        self.task_input = task_input
        self.children: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def record_llm_call(
        self,
        name: str,
        model: str,
        input_data: Any,
        output_data: Any,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ):
        span = {
            "name": name,
            "kind": "LLM",
            "model": model,
            "input": input_data,
            "output": output_data,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
            },
        }
        self.children.append(span)

    def record_tool_call(self, name: str, tool_input: Any, tool_output: Any):
        span = {
            "name": name,
            "kind": "TOOL",
            "input": tool_input,
            "output": tool_output,
        }
        self.children.append(span)

    def finish(self, final_output: Any = None) -> Dict[str, Any]:
        trace = {
            "name": self.workflow_name,
            "project": PROJECT_ID,
            "input": self.task_input,
            "output": final_output,
            "children": self.children,
        }
        return send_trace(trace)
