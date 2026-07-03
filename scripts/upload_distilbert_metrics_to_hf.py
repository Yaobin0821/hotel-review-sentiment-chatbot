from pathlib import Path
from huggingface_hub import HfApi

BASE_DIR = Path(__file__).resolve().parents[1]

REPO_ID = "qm0720/staywise-kl-distilbert-sentiment"

FILES_TO_UPLOAD = [
    {
        "local_path": BASE_DIR / "reports" / "distilbert_metrics_summary.csv",
        "repo_path": "distilbert_metrics_summary.csv",
    },
    {
        "local_path": BASE_DIR / "reports" / "model_evaluation_results.csv",
        "repo_path": "model_evaluation_results.csv",
    },
    {
        "local_path": BASE_DIR / "reports" / "best_model_summary.csv",
        "repo_path": "best_model_summary.csv",
    },
]


def main():
    api = HfApi()

    for item in FILES_TO_UPLOAD:
        local_path = item["local_path"]
        repo_path = item["repo_path"]

        if not local_path.exists():
            print(f"Skipping missing file: {local_path}")
            continue

        print(f"Uploading {local_path} -> {repo_path}")

        api.upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=repo_path,
            repo_id=REPO_ID,
            repo_type="model",
        )

    print("\nMetrics files uploaded successfully.")


if __name__ == "__main__":
    main()