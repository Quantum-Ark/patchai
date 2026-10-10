"""
Deterministic State Machine for PatchPilot AI.
Enforces valid lifecycle transitions and tracks progression from intake to verified recovery.
"""

from typing import List, Dict, Tuple
from datetime import datetime
from patchpilot.models import AgentState


class StateMachineError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateTransition:
    def __init__(self, from_state: AgentState, to_state: AgentState, reason: str):
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        self.timestamp = datetime.now()


class AgentStateMachine:
    # Explicit legal transitions
    VALID_TRANSITIONS: Dict[AgentState, List[AgentState]] = {
        AgentState.IDLE: [AgentState.INTAKE],
        AgentState.INTAKE: [AgentState.INVESTIGATING, AgentState.FAILED],
        AgentState.INVESTIGATING: [AgentState.REPRODUCING, AgentState.FAILED],
        AgentState.REPRODUCING: [AgentState.PATCHING, AgentState.FAILED],
        AgentState.PATCHING: [AgentState.TESTING, AgentState.FAILED],
        AgentState.TESTING: [AgentState.EVALUATING, AgentState.FAILED],
        AgentState.EVALUATING: [AgentState.VERIFIED, AgentState.RECOVERING, AgentState.FAILED],
        AgentState.RECOVERING: [AgentState.PATCHING, AgentState.FAILED],
        AgentState.VERIFIED: [],
        AgentState.FAILED: [],
    }

    def __init__(self, initial_state: AgentState = AgentState.IDLE):
        self._current_state = initial_state
        self._history: List[StateTransition] = []

    @property
    def current_state(self) -> AgentState:
        return self._current_state

    @property
    def history(self) -> List[StateTransition]:
        return list(self._history)

    def transition_to(self, new_state: AgentState, reason: str = "") -> AgentState:
        allowed = self.VALID_TRANSITIONS.get(self._current_state, [])
        if new_state not in allowed:
            raise StateMachineError(
                f"Invalid state transition from {self._current_state.value} to {new_state.value}. "
                f"Allowed destinations: {[s.value for s in allowed]}"
            )

        transition = StateTransition(self._current_state, new_state, reason)
        self._history.append(transition)
        self._current_state = new_state
        return self._current_state

    def can_transition_to(self, target_state: AgentState) -> bool:
        return target_state in self.VALID_TRANSITIONS.get(self._current_state, [])
