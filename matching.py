"""University-proposing Gale–Shapley with weights and university ties, supporting tiered student preferences."""

from typing import Dict, List
from models import Student, University


def get_rank(student: Student, university_name: str) -> int:
    """
    Find the rank (tier index) of the given university in the student's preferences,
    supporting tied preferences (tiers).
    """
    for i, tier in enumerate(student.preferences):
        if isinstance(tier, str):
            if tier == university_name:
                return i
        elif isinstance(tier, list) and university_name in tier:
            return i
    return len(student.preferences)  # lowest rank if not found


def weighted_gale_shapley(students: Dict[str, Student],
                          universities: Dict[str, University],
                          gamma: float = 1.0):
    """
    University-proposing Gale–Shapley algorithm with weights and support for tiered student preferences.

    Parameters
    ----------
    students      : dict of student_name -> Student
    universities  : dict of university_name -> University
    gamma         : weight for university power

    Returns
    -------
    dict student_name -> matched_university_name
    """
    n = len(universities)

    def score(s: Student, u: University) -> float:
        rank = get_rank(s, u.name)
        return s.voice * (n - rank) + gamma * u.power

    free_unis: List[University] = [u for u in universities.values() if u.has_free_slot()]

    while free_unis:
        u = free_unis.pop(0)
        cand_name = u.next_candidate()
        if cand_name is None or cand_name not in students:
            continue

        s = students[cand_name]

        if s.match is None:
            # Only assign if the university has space
            if u.has_free_slot():
                s.match = u.name
                u.accepted.append(s.name)
        else:
            current_u = universities[s.match]
            if score(s, u) > score(s, current_u):
                # student prefers new university under weighted score
                current_u.accepted.remove(s.name)
                if u.has_free_slot():
                    s.match = u.name
                    u.accepted.append(s.name)
                    if current_u.has_free_slot():
                        free_unis.append(current_u)
                else:
                    # new university is full → stay at current match
                    pass
            else:
                # student prefers current → nothing changes
                pass

        # Requeue university only if it has space and more candidates
        if u.has_free_slot() and u.preference_pointer < len(u.preferences_flat):
            free_unis.append(u)

    # Safety check: no overfilling
    for u in universities.values():
        assert len(u.accepted) <= u.capacity, f"{u.name} overfilled: {len(u.accepted)} > {u.capacity}"

    return {s.name: s.match for s in students.values()}