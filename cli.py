import json
import sys
from typing import Dict
from models import Student, University
from matching import weighted_gale_shapley

def load_json(path: str):
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)

    students = {
        d["name"]: Student(
            name=d["name"],
            preferences=d["prefs"],
            voice=d.get("voice", 1.0),
        )
        for d in data["students"]
    }

    universities = {
        d["name"]: University(
            name=d["name"],
            capacity=d["capacity"],
            preferences=d["prefs"],
            power=d.get("power", 1.0),
        )
        for d in data["universities"]
    }

    return students, universities

def boost_voice_by_demand(students: Dict[str, Student],
                          universities: Dict[str, University],
                          alpha: float = 1.0):
    counts = {s: 0 for s in students}
    for uni in universities.values():
        for tier in uni.preferences:
            for name in (tier if isinstance(tier, list) else [tier]):
                if name in counts:
                    counts[name] += 1
    for name, cnt in counts.items():
        students[name].voice += alpha * cnt

def assign_unmatched(students: Dict[str, Student],
                     universities: Dict[str, University],
                     result: Dict[str, str]):
    unmatched = [s for s, u in result.items() if u is None]
    print(f"\n🔄 Assigning {len(unmatched)} unmatched students manually...")
    for student_name in unmatched:
        for uni in universities.values():
            for tier in uni.preferences:
                names = tier if isinstance(tier, list) else [tier]
                if student_name in names:
                    result[student_name] = uni.name
                    print(f"→ {student_name} forcibly placed in {uni.name}")
                    break
            if result[student_name] is not None:
                break

def reset_state(students: Dict[str, Student], universities: Dict[str, University]):
    for s in students.values():
        s.match = None
    for u in universities.values():
        u.accepted = []
        u.preference_pointer = 0

def print_matching(title: str, result: Dict[str, str]):
    matched = {s: u for s, u in result.items() if u}
    unmatched = [s for s, u in result.items() if not u]

    print(f"\n📌 {title}")
    print(f"Matched: {len(matched)} / {len(result)}")
    for student, uni in sorted(matched.items(), key=lambda x: (x[1], x[0])):
        print(f"{student:25} → {uni}")
    if unmatched:
        print(f"\n❌ Unmatched ({len(unmatched)}):")
        for student in unmatched:
            print(f"{student:25} → No match")

def print_powers(universities: Dict[str, University]):
    print("\n🏛️ University power levels (OPTIMIZED):")
    for u in universities.values():
        print(f"{u.name:15} → power: {u.power}")

def main():
    json_path = input("Enter path to your JSON file (e.g. data.json): ").strip()
    students_orig, universities_orig = load_json(json_path)

    # ----- ORIGINAL MATCHING -----
    print("\n================ ORIGINAL MATCHING ================\n")
    students = {k: Student(v.name, v.preferences, v.voice) for k, v in students_orig.items()}
    universities = {k: University(v.name, v.capacity, v.preferences, v.power) for k, v in universities_orig.items()}
    boost_voice_by_demand(students, universities)
    result_original = weighted_gale_shapley(students, universities, gamma=1.0)
    assign_unmatched(students, universities, result_original)
    print_matching("Original Matching (gamma = 1.0)", result_original)

    # ----- OPTIMIZED MATCHING (gamma & power) -----
    print("\n================ OPTIMIZED MATCHING ================\n")
    students = {k: Student(v.name, v.preferences, v.voice) for k, v in students_orig.items()}
    universities = {k: University(v.name, v.capacity, v.preferences, v.power) for k, v in universities_orig.items()}
    boost_voice_by_demand(students, universities)

    best_gamma = 1.0
    fewest_unmatched = float("inf")
    best_result = None
    best_powers = {}

    def frange(start, stop, step):
        while start <= stop:
            yield round(start, 3)
            start += step

    for gamma in frange(0.5, 4.0, 0.5):
        for uni in universities.values():
            uni.power = 1.0  # reset
        for uni in universities.values():
            best_local = 1.0
            least = float("inf")
            for p in frange(0.5, 5.0, 0.5):
                reset_state(students, universities)
                uni.power = p
                try:
                    result = weighted_gale_shapley(students, universities, gamma)
                    unmatched = sum(1 for v in result.values() if v is None)
                    if unmatched < least:
                        least = unmatched
                        best_local = p
                except:
                    continue
            uni.power = best_local

        reset_state(students, universities)
        result = weighted_gale_shapley(students, universities, gamma)
        unmatched = sum(1 for v in result.values() if v is None)
        if unmatched < fewest_unmatched:
            fewest_unmatched = unmatched
            best_gamma = gamma
            best_result = result.copy()
            best_powers = {u.name: u.power for u in universities.values()}

    # Apply best powers
    for uni in universities.values():
        uni.power = best_powers[uni.name]
    reset_state(students, universities)
    result_opt = weighted_gale_shapley(students, universities, best_gamma)
    assign_unmatched(students, universities, result_opt)

    print_matching(f"Optimized Matching (gamma = {best_gamma})", result_opt)
    print_powers(universities)

if __name__ == "__main__":
    main()
    input("Please Enter Any Key To Exit...")
