import json, sys
from models import Student, University
from matching import weighted_gale_shapley

def load_sample(path: str):
    # Load students and universities from JSON file
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)
    students = {
        d["name"]: Student(
            name=d["name"],
            preferences=d["prefs"],
            voice=d.get("voice", 1.0)
        ) for d in data["students"]
    }
    universities = {
        d["name"]: University(
            name=d["name"],
            capacity=d["capacity"],
            preferences=d["prefs"],
            power=d.get("power", 1.0)
        ) for d in data["universities"]
    }
    return students, universities

def main():
    # Load data and run matching algorithm
    if len(sys.argv) < 2:
        print("Usage: python cli.py sample_data.json")
        sys.exit(1)
    students, universities = load_sample(sys.argv[1])
    match = weighted_gale_shapley(students, universities, gamma=1.0)
    print("\nWeighted Matching Result")
    for s, u in match.items():
        print(f"{s}  →  {u}")

if __name__ == "__main__":
    main()