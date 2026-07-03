from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder

BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_MODEL_DIR = BASE_DIR / "models" / "distilbert_model"

MODEL_REPO_NAME = "staywise-kl-distilbert-sentiment"


def main():
    if not LOCAL_MODEL_DIR.exists():
        raise FileNotFoundError(f"Local model folder not found: {LOCAL_MODEL_DIR}")

    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]

    hf_repo_id = f"{username}/{MODEL_REPO_NAME}"

    print("=" * 60)
    print("Uploading DistilBERT model to Hugging Face Hub")
    print("=" * 60)
    print(f"Local model folder: {LOCAL_MODEL_DIR}")
    print(f"Hugging Face repo: {hf_repo_id}")

    create_repo(
        repo_id=hf_repo_id,
        repo_type="model",
        private=False,
        exist_ok=True,
    )

    upload_folder(
        folder_path=str(LOCAL_MODEL_DIR),
        repo_id=hf_repo_id,
        repo_type="model",
        path_in_repo=".",
    )

    print("\nUpload completed successfully.")
    print(f"Model uploaded to: https://huggingface.co/{hf_repo_id}")
    print(f"\nUse this model ID in your app.py:")
    print(f'HF_MODEL_ID = "{hf_repo_id}"')


if __name__ == "__main__":
    main()