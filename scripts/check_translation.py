import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "preprocessed_training_dataset.csv"

df = pd.read_csv(DATA_PATH)

translated_df = df[df["Translation_Applied"] == True][[
    "Review_Text",
    "Detected_Language",
    "Translated_Text",
    "Sentiment"
]]

print("Total translated rows:", len(translated_df))
print(translated_df.head(50).to_string(index=False))

output_path = BASE_DIR / "data" / "translation_check.csv"
translated_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\nSaved translation check file to:")
print(output_path)