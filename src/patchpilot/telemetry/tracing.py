"""
Neatlogs Observability & Tracing Integration.
Provides workflow-level tracing, span recording, and graceful flush for PatchPilot AI.
Follows official Neatlogs specification (https://docs.neatlogs.com/sdk/http-injection).
"""

import time
import requests
from typing import Dict, Any, List, Optional
from patchpilot.config import config


class NeatlogsTracer:
    def __init__(
        self,
        project_id: Optional[str] = None,
        api_key: Optional[str] = None,
        ingest_url: Optional[str] = None,
        enabled: bool = True
    ):
        self.project_id = project_id or config.neatlogs_project_id
        self.api_key = api_key if api_key is not None else config.neatlogs_api_key
        self.ingest_url = ingest_url or config.neatlogs_ingest_url
        self.enabled = enabled

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_neatlogs_project_api_key_here")

    def create_workflow_trace(
        self,
        workflow_name: str,
        run_id: str,
        issue_id: str,
        input_data: Any,
        output_data: Any,
        spans: List[Dict[str, Any]],
        duration_seconds: float = 0.0
    ) -> Optional[str]:
        """
        Submits a full workflow trace to Neatlogs.
        Returns the trace_id if successful, or None.
        """
        if not self.enabled or not self.is_configured():
            return "simulated-trace-" + run_id

        payload = {
            "name": workflow_name,
            "project": self.project_id,
            "input": {
                "run_id": run_id,
                "issue_id": issue_id,
                "summary": str(input_data)[:500]
            },
            "output": {
                "summary": str(output_data)[:500],
                "duration_seconds": duration_seconds
            },
            "attributes": {
                "neatlogs.workflow.name": workflow_name,
                "neatlogs.task.id": run_id,
            },
            "children": spans
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.ingest_url, json=payload, headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("trace_id")
            else:
                return None
        except Exception:
            return None


class TraceBuilder:
    """Convenience builder for recording spans throughout an agent run."""
    def __init__(self, tracer: NeatlogsTracer, workflow_name: str, run_id: str, issue_id: str):
        self.tracer = tracer
        self.workflow_name = workflow_name
        self.run_id = run_id
        self.issue_id = issue_id
        self.spans: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def add_span(
        self,
        name: str,
        kind: str,
        input_data: Any,
        output_data: Any,
        model: Optional[str] = None,
        tokens: Optional[Dict[str, int]] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        span: Dict[str, Any] = {
            "name": name,
            "kind": kind,
            "input": str(input_data)[:1000],
            "output": str(output_data)[:1000]
        }
        if model:
            span["model"] = model
        if tokens:
            span["tokens"] = tokens
        if attributes:
            span["attributes"] = attributes

        self.spans.append(span)

    def record_llm_span(self, name: str, model: str, prompt: str, completion: str, prompt_tokens: int = 0, completion_tokens: int = 0):
        self.add_span(
            name=name,
            kind="LLM",
            input_data=prompt,
            output_data=completion,
            model=model,
            tokens={"prompt": prompt_tokens, "completion": completion_tokens}
        )

    def record_tool_span(self, name: str, tool_input: Any, tool_output: Any):
        self.add_span(
            name=name,
            kind="TOOL",
            input_data=tool_input,
            output_data=tool_output
        )

    def finish(self, final_output: Any) -> Optional[str]:
        duration = round(time.time() - self.start_time, 3)
        return self.tracer.create_workflow_trace(
            workflow_name=self.workflow_name,
            run_id=self.run_id,
            issue_id=self.issue_id,
            input_data={"run_id": self.run_id, "issue_id": self.issue_id},
            output_data=final_output,
            spans=self.spans,
            duration_seconds=duration
        )
