from pathlib import Path


def load_dataset() -> list[str]:
    facts_path = Path(__file__).resolve().parent / "facts.txt"
    with open(facts_path, "r", encoding="utf-8") as file:
        dataset = [line.strip() for line in file if line.strip()]
    print(f"Loaded {len(dataset)} entries")
    return dataset
