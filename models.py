"""Data classes with tiered university preferences (ties allowed)."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Iterator, Union


@dataclass
class Student:
    name: str
    preferences: List[str]           # strict total order of *all* universities
    voice: float = 1.0               # weight of the student's opinion
    match: Optional[str] = None      # university assigned after matching



@dataclass
class University:
    name: str
    capacity: int
    preferences: List[Union[str, List[str]]]  # list of names or tiers
    power: float = 1.0
    accepted: List[str] = field(default_factory=list)

    # New fields added:
    preferences_flat: List[str] = field(init=False)
    preference_pointer: int = field(default=0, init=False)

    def __post_init__(self):
        # Flatten tiered prefs into a single list
        self.preferences_flat = []
        for tier in self.preferences:
            if isinstance(tier, list):
                self.preferences_flat.extend(tier)
            else:
                self.preferences_flat.append(tier)

    def has_free_slot(self) -> bool:
        return len(self.accepted) < self.capacity

    def next_candidate(self) -> Union[str, None]:
        while self.preference_pointer < len(self.preferences_flat):
            candidate = self.preferences_flat[self.preference_pointer]
            self.preference_pointer += 1
            if candidate not in self.accepted:
                return candidate
        return None