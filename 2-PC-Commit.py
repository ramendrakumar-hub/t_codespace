"""
Minimal 2-Phase Commit (2PC) simulation.

This is a self-contained demo with a coordinator and participants.
It prints the decision flow and final states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Vote(Enum):
    YES = "YES"
    NO = "NO"


class Decision(Enum):
    COMMIT = "COMMIT"
    ABORT = "ABORT"


class State(Enum):
    INIT = "INIT"
    READY = "READY"  # Voted YES and prepared to commit
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"


@dataclass
class Participant:
    name: str
    will_vote_yes: bool = True
    state: State = State.INIT
    log: List[str] = field(default_factory=list)

    def prepare(self) -> Vote:
        """Phase 1: coordinator asks if participant can commit."""
        if self.will_vote_yes:
            self.state = State.READY
            self.log.append("VOTE YES")
            return Vote.YES
        self.state = State.ABORTED
        self.log.append("VOTE NO")
        return Vote.NO

    def commit(self) -> None:
        """Phase 2: coordinator tells participant to commit."""
        self.state = State.COMMITTED
        self.log.append("COMMIT")

    def abort(self) -> None:
        """Phase 2: coordinator tells participant to abort."""
        self.state = State.ABORTED
        self.log.append("ABORT")


@dataclass
class Coordinator:
    participants: List[Participant]
    decision: Decision | None = None
    log: List[str] = field(default_factory=list)

    def run_2pc(self) -> Decision:
        """Execute the two-phase commit protocol."""
        votes: Dict[str, Vote] = {}

        # Phase 1: Prepare / Vote
        self.log.append("PHASE 1: PREPARE")
        for p in self.participants:
            vote = p.prepare()
            votes[p.name] = vote
            self.log.append(f"{p.name} -> {vote.value}")

        # Decide
        if all(v == Vote.YES for v in votes.values()):
            self.decision = Decision.COMMIT
        else:
            self.decision = Decision.ABORT
        self.log.append(f"DECISION: {self.decision.value}")

        # Phase 2: Commit / Abort
        self.log.append("PHASE 2: " + self.decision.value)
        for p in self.participants:
            if self.decision == Decision.COMMIT:
                p.commit()
            else:
                p.abort()
            self.log.append(f"{p.name} -> {p.state.value}")

        return self.decision


def demo() -> None:
    participants = [
        Participant("A", will_vote_yes=True),
        Participant("B", will_vote_yes=True),
        Participant("C", will_vote_yes=False),  # one NO forces ABORT
    ]
    coordinator = Coordinator(participants)
    decision = coordinator.run_2pc()

    print("Coordinator log:")
    for line in coordinator.log:
        print("  ", line)

    print("\nParticipant logs:")
    for p in participants:
        print(f"  {p.name} ({p.state.value}): {p.log}")

    print(f"\nFinal decision: {decision.value}")


if __name__ == "__main__":
    demo()
