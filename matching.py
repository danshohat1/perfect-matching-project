from typing import Dict, List
from models import Student, University

def weighted_gale_shapley(students: Dict[str, Student],
                          universities: Dict[str, University],
                          gamma: float = 1.0):
    """
    University-proposing Gale-Shapley with weighted scoring.
    Students decide based on:
    score(s,u) = voice_s * (n - rank_s(u) + 1) + gamma * power_u
    """
    n = len(universities)  # total number of universities

    def score(s: Student, u: University) -> float:
        # Computes score based on student preference + university power
        return s.voice * (n - s.preferences.index(u.name) + 1) + gamma * u.power

    # Initialize free universities
    free_unis: List[University] = [u for u in universities.values() if u.has_free_slot()]

    while free_unis:
        u = free_unis.pop(0)
        cand_name = u.next_candidate()  # pick next student to propose to
        if cand_name is None or cand_name not in students:
            continue

        s = students[cand_name]

        if s.match is None:
            # student is unmatched → accept offer
            s.match = u.name
            u.accepted.append(s.name)
        else:
            current_u = universities[s.match]
            # decide whether to switch based on score
            if score(s, u) > score(s, current_u):
                current_u.accepted.remove(s.name)
                s.match = u.name
                u.accepted.append(s.name)
                if current_u.has_free_slot():
                    free_unis.append(current_u)
            else:
                # rejected → stay in queue if space
                if u.has_free_slot():
                    free_unis.append(u)

        # re-queue university if not full
        if u.has_free_slot():
            free_unis.append(u)

    return {s.name: s.match for s in students.values()}  # final matching