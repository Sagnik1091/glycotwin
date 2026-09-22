"""Train and evaluate the synthetic-cohort risk model."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from twin.model import train_model  # noqa: E402

if __name__ == "__main__":
    metrics = train_model()
    output = Path("artifacts/metrics.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))
