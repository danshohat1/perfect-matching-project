"""Command-line wrapper for the weighted matching algorithm."""
import json
import sys
from models import Student, University
from matching import weighted_gale_shapley


def load_json(path: str):
    """Load students & universities from a JSON file (UTF-8)."""
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
            preferences=d["prefs"],          # note: list of tiers
            power=d.get("power", 1.0),
        )
        for d in data["universities"]
    }
    return students, universities

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <data.json> [gamma]")
        sys.exit(1)

    gamma = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    students, universities = load_json(sys.argv[1])
    result = weighted_gale_shapley(students, universities, gamma)

    print("\nFinal matching (gamma =", gamma, ")")

    matched = {s: u for s, u in result.items() if u is not None}
    unmatched = [s for s, u in result.items() if u is None]

    sorted_by_uni = sorted(matched.items(), key=lambda x: x[1])  # sort by university

    print("\n🎓 Matched Students:")
    for student, uni in sorted_by_uni:
        print(f"{student:25} → {uni}")

    if unmatched:
        print("\n❌ Unmatched Students:")
        for student in unmatched:
            print(f"{student:25} → No match")


if __name__ == "__main__":
    main()