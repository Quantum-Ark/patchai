"""Unit tests for Neatlogs tracing, span lifecycles, and graceful error handling."""

import pytest
from unittest.mock import patch, MagicMock
from patchpilot.telemetry.tracing import NeatlogsTracer, TraceBuilder


def test_tracer_initialization_without_key():
    tracer = NeatlogsTracer(project_id="test-proj", api_key="", enabled=False)
    assert tracer.is_configured() is False

    builder = TraceBuilder(tracer, "test_workflow", "run-1", "issue-1")
    builder.add_span("step1", "TOOL", "input", "output")
    builder.record_llm_span("call_model", "gpt-4o", "prompt", "completion", 10, 20)
    builder.record_tool_span("run_test", "pytest", "1 passed")

    # Finishing should return simulated trace ID without failing or making external requests
    trace_id = builder.finish("success")
    assert trace_id == "simulated-trace-run-1"


def test_tracer_lifecycle_with_mocked_network():
    tracer = NeatlogsTracer(
        project_id="test-proj",
        api_key="neatlogs_test_secret_key",
        ingest_url="https://ingest.neatlogs.com/v1/trace",
        enabled=True,
    )
    assert tracer.is_configured() is True

    builder = TraceBuilder(tracer, "agent_workflow", "run-42", "issue-99")
    builder.add_span("investigation", "STEP", {"repo": "patchpilot"}, {"status": "ok"})
    builder.record_llm_span("generate_patch", "gpt-4o", "generate fix", "diff", 100, 50)

    assert len(builder.spans) == 2
    assert builder.spans[0]["name"] == "investigation"
    assert builder.spans[1]["kind"] == "LLM"

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"trace_id": "real-neatlogs-trace-123"}
        mock_post.return_value = mock_response

        trace_id = builder.finish({"final": "verified"})
        assert trace_id == "real-neatlogs-trace-123"
        assert mock_post.called

        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer neatlogs_test_secret_key"
        payload = kwargs["json"]
        assert payload["project"] == "test-proj"
        assert len(payload["children"]) == 2


def test_tracer_network_failure_is_graceful():
    tracer = NeatlogsTracer(
        project_id="test-proj",
        api_key="neatlogs_test_key",
        ingest_url="https://ingest.neatlogs.com/v1/trace",
        enabled=True,
    )
    builder = TraceBuilder(tracer, "failing_workflow", "run-err", "issue-1")
    builder.add_span("span_1", "TOOL", "in", "out")

    with patch("requests.post", side_effect=Exception("Connection refused")):
        # Must not raise an exception; must degrade gracefully and return None
        trace_id = builder.finish("done")
        assert trace_id is None
