"""
Quick verification script to test Neatlogs tracing.
Runs a test trace and verifies it was delivered to Neatlogs dashboard.
"""

from neatlogs_tracer import TraceSession

def main():
    print("Testing Neatlogs tracing connection...")

    session = TraceSession(
        workflow_name="patchpilot-code-fix",
        task_input="Fix NullPointerException in payment service"
    )

    # 1. Simulate an LLM analysis span
    session.record_llm_call(
        name="diagnose_bug",
        model="gpt-4o",
        input_data="Analyze stack trace: NPE at line 42 in payment_processor.py",
        output_data="Null check is missing on transaction.metadata object.",
        prompt_tokens=45,
        completion_tokens=22,
    )

    # 2. Simulate a tool span
    session.record_tool_call(
        name="apply_git_patch",
        tool_input={"file": "payment_processor.py", "lines": "42-45"},
        tool_output={"success": True, "diff": "+ if transaction.metadata is not None:"}
    )

    # 3. Simulate an LLM evaluation span
    session.record_llm_call(
        name="verify_patch",
        model="gpt-4o",
        input_data="Verify regression risk for patched code",
        output_data="Patch verified. Unit tests pass with 0 regressions.",
        prompt_tokens=30,
        completion_tokens=15,
    )

    # Finish and send the trace
    result = session.finish(final_output="Bug fixed and patch verified successfully.")

    if result.get("success"):
        print("\n[SUCCESS] Trace successfully recorded in Neatlogs!")
        print(f"Trace ID: {result.get('trace_id')}")
        print("You can now view this trace in your Neatlogs dashboard.")
    else:
        print("\n[ERROR] Trace submission failed:", result.get("error"))

if __name__ == "__main__":
    main()
