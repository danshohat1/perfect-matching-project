from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Student:
    name: str
    preferences: List[str]           # Ordered list of ALL universities (strict preference)
    voice: float = 1.0               # Weight of this student's opinion
    match: Optional[str] = None     # Assigned university after matching

@dataclass
class University:
    name: str
    capacity: int                   # Max number of students this university can accept
    preferences: List[str]          # List of preferred students (partial or full)
    power: float = 1.0              # Institutional weight (importance)
    accepted: List[str] = field(default_factory=list)  # Current accepted students
    _cursor: int = 0                # Internal pointer for proposing

    def has_free_slot(self) -> bool:
        return len(self.accepted) < self.capacity

    def next_candidate(self) -> Optional[str]:
        # Returns next student on preference list, or None if exhausted
        if self._cursor >= len(self.preferences):
            return None
        student = self.preferences[self._cursor]
        self._cursor += 1
        return student