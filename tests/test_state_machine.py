"""Unit tests for PatchPilot AI deterministic state machine."""

import pytest
from patchpilot.models import AgentState
from patchpilot.state_machine import AgentStateMachine, StateMachineError


def test_valid_happy_path_transitions():
    sm = AgentStateMachine()
    assert sm.current_state == AgentState.IDLE

    assert sm.transition_to(AgentState.INTAKE) == AgentState.INTAKE
    assert sm.transition_to(AgentState.INVESTIGATING) == AgentState.INVESTIGATING
    assert sm.transition_to(AgentState.REPRODUCING) == AgentState.REPRODUCING
    assert sm.transition_to(AgentState.PATCHING) == AgentState.PATCHING
    assert sm.transition_to(AgentState.TESTING) == AgentState.TESTING
    assert sm.transition_to(AgentState.EVALUATING) == AgentState.EVALUATING
    assert sm.transition_to(AgentState.VERIFIED) == AgentState.VERIFIED

    assert sm.current_state == AgentState.VERIFIED
    assert len(sm.history) == 7


def test_recovery_cycle_transitions():
    sm = AgentStateMachine()
    sm.transition_to(AgentState.INTAKE)
    sm.transition_to(AgentState.INVESTIGATING)
    sm.transition_to(AgentState.REPRODUCING)
    sm.transition_to(AgentState.PATCHING)
    sm.transition_to(AgentState.TESTING)
    sm.transition_to(AgentState.EVALUATING)

    # Recovery cycle
    assert sm.transition_to(AgentState.RECOVERING) == AgentState.RECOVERING
    assert sm.transition_to(AgentState.PATCHING) == AgentState.PATCHING
    assert sm.current_state == AgentState.PATCHING


def test_invalid_transition_raises():
    sm = AgentStateMachine()
    assert sm.current_state == AgentState.IDLE
    with pytest.raises(StateMachineError, match="Invalid state transition from IDLE to VERIFIED"):
        sm.transition_to(AgentState.VERIFIED)


def test_can_transition_to():
    sm = AgentStateMachine()
    assert sm.can_transition_to(AgentState.INTAKE) is True
    assert sm.can_transition_to(AgentState.VERIFIED) is False
