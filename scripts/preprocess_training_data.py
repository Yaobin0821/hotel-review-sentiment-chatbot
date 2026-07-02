import re
import html
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

# =====================================================
# Optional Translation Packages
# =====================================================
try:
    from langdetect import detect
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False


# =====================================================
# File Paths
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_CSV = DATA_DIR / "training_dataset.csv"
INPUT_EXCEL = DATA_DIR / "training_dataset.xlsx"

OUTPUT_PREPROCESSED = DATA_DIR / "preprocessed_training_dataset.csv"
OUTPUT_TRAIN = DATA_DIR / "train_dataset.csv"
OUTPUT_TEST = DATA_DIR / "test_dataset.csv"
OUTPUT_SUMMARY = DATA_DIR / "preprocessing_summary.csv"
OUTPUT_TRANSLATION_CACHE = DATA_DIR / "translation_cache.csv"


# =====================================================
# Label Mapping
# =====================================================
SENTIMENT_MAPPING = {
    "positive": "positive",
    "pos": "positive",
    "good": "positive",

    "neutral": "neutral",
    "neu": "neutral",
    "average": "neutral",

    "negative": "negative",
    "neg": "negative",
    "bad": "negative",
}

LABEL_ID_MAPPING = {
    "negative": 0,
    "neutral": 1,
    "positive": 2,
}

SENTIMENT_SORT_ORDER = {
    "positive": 0,
    "neutral": 1,
    "negative": 2,
}


# =====================================================
# Emoji and Emoticon Mapping
# =====================================================
EMOJI_MAPPING = {
    "😊": " positive emoji ",
    "😄": " positive emoji ",
    "😁": " positive emoji ",
    "😍": " positive emoji ",
    "👍": " positive emoji ",
    "❤️": " positive emoji ",
    "❤": " positive emoji ",
    "✨": " positive emoji ",
    "⭐": " positive emoji ",
    "🌟": " positive emoji ",

    "😐": " neutral emoji ",
    "😶": " neutral emoji ",
    "🤔": " neutral emoji ",

    "😡": " negative emoji ",
    "😠": " negative emoji ",
    "😞": " negative emoji ",
    "😢": " negative emoji ",
    "😭": " negative emoji ",
    "👎": " negative emoji ",
    "💔": " negative emoji ",
    "😤": " negative emoji ",
}

EMOTICON_MAPPING = {
    ":)": " positive emoticon ",
    ":-)": " positive emoticon ",
    ":D": " positive emoticon ",
    ":-D": " positive emoticon ",
    "<3": " positive emoticon ",

    ":|": " neutral emoticon ",
    ":-|": " neutral emoticon ",

    ":(": " negative emoticon ",
    ":-(": " negative emoticon ",
    ":'(": " negative emoticon ",
}


# =====================================================
# Hotel Review Typo Normalisation
# =====================================================
TYPO_MAPPING = {
    "cleaness": "cleanliness",
    "cleanness": "cleanliness",
    "cleaniness": "cleanliness",

    "wifi": "wi fi",
    "wi-fi": "wi fi",
    "wi fi": "wi fi",

    "aircond": "air conditioning",
    "aircon": "air conditioning",
    "ac": "air conditioning",

    "noice": "noise",
    "noisyy": "noisy",

    "recieption": "reception",
    "receiption": "reception",

    "restuarant": "restaurant",
    "breakfirst": "breakfast",

    "bath room": "bathroom",
    "checkin": "check in",
    "checkout": "check out",

    "ok": "okay",
    "okk": "okay",

    "pravicy": "privacy",
    "enviroment": "environment",
}


# =====================================================
# Malay / Malaysian Slang Normalisation
# =====================================================
MALAY_SLANG_MAPPING = {
    r"\bsy\b": "saya",
    r"\bsaye\b": "saya",
    r"\bsya\b": "saya",

    r"\bdh\b": "sudah",
    r"\bdah\b": "sudah",

    r"\bx\b": "tidak",
    r"\btak\b": "tidak",
    r"\btk\b": "tidak",
    r"\btdk\b": "tidak",

    r"\bxdapat\b": "tidak dapat",
    r"\bx dapat\b": "tidak dapat",
    r"\bxde\b": "tiada",
    r"\bx de\b": "tiada",

    r"\bnk\b": "nak",
    r"\bdkt\b": "dekat",
    r"\bdekt\b": "dekat",

    r"\bbyr\b": "bayar",
    r"\bsgt\b": "sangat",
    r"\byg\b": "yang",
    r"\bmmg\b": "memang",
    r"\bklu\b": "kalau",
    r"\bklo\b": "kalau",
    r"\bskrg\b": "sekarang",
    r"\bkat\b": "di",
    r"\bdepo\b": "deposit",
    r"\bbg\b": "bagi",
    r"\bsmua\b": "semua",
    r"\bbnyk\b": "banyak",
    r"\bbyk\b": "banyak",
    r"\bmkn\b": "makan",
    r"\btgk\b": "tengok",

    r"\bsenang\b": "mudah",
    r"\bserabut\b": "menyusahkan",
    r"\bparking serabut\b": "parking menyusahkan",
}

MALAY_MARKERS = {
    "tak", "tidak", "tk", "tdk", "bilik", "sangat", "bersih", "kotor",
    "selesa", "dekat", "saya", "yang", "memang", "kalau", "makan",
    "tengok", "berbau", "bau", "serabut", "menyusahkan", "aircond",
    "boleh", "keadaan", "sekeliling", "memuaskan", "gatal", "badan",
    "bantal", "kedudukan", "akses", "keluarga", "senang", "mudah"
}

COMMON_ENGLISH_HOTEL_WORDS = {
    "hotel", "room", "clean", "dirty", "staff", "service", "location",
    "breakfast", "parking", "toilet", "bathroom", "smell", "nice",
    "good", "bad", "average", "comfortable", "uncomfortable", "friendly",
    "rude", "price", "expensive", "cheap", "value", "worth", "wifi",
    "wi", "fi", "air", "conditioning", "lift", "elevator", "view",
    "stay", "family", "near", "mall", "station", "improve", "big",
    "small", "environment", "channel", "antenna", "facilities", "privacy"
}


# =====================================================
# Dataset Loading
# =====================================================
def load_input_dataset() -> pd.DataFrame:
    if INPUT_CSV.exists():
        print(f"Reading CSV file: {INPUT_CSV}")

        try:
            return pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
        except UnicodeDecodeError:
            return pd.read_csv(INPUT_CSV, encoding="latin1")

    if INPUT_EXCEL.exists():
        print(f"Reading Excel file: {INPUT_EXCEL}")
        return pd.read_excel(INPUT_EXCEL, engine="openpyxl")

    raise FileNotFoundError(
        "No dataset file found. Please place either training_dataset.csv "
        "or training_dataset.xlsx inside the data folder."
    )


# =====================================================
# Column Detection
# =====================================================
def detect_text_column(df: pd.DataFrame) -> str:
    possible_text_columns = [
        "Sentence",
        "sentence",
        "Review_Text",
        "Review Text",
        "review_text",
        "Text",
        "text",
        "Review",
        "review",
    ]

    for col in possible_text_columns:
        if col in df.columns:
            return col

    raise ValueError(
        "No valid review text column found. Please make sure your dataset has "
        "a column named 'Sentence', 'sentence', or 'Review_Text'."
    )


def detect_sentiment_column(df: pd.DataFrame) -> str:
    possible_sentiment_columns = [
        "Sentiment",
        "sentiment",
        "Label",
        "label",
        "Class",
        "class",
    ]

    for col in possible_sentiment_columns:
        if col in df.columns:
            return col

    raise ValueError(
        "No valid sentiment column found. Please make sure your dataset has "
        "a column named 'Sentiment' or 'sentiment'."
    )


def detect_hotel_column(df: pd.DataFrame) -> str | None:
    possible_hotel_columns = [
        "Hotel",
        "hotel",
        "Hotel_Name",
        "hotel_name",
        "Hotel Name",
        "Location",
        "location",
        "Property",
        "property",
        "Property_Name",
        "property_name",
    ]

    for col in possible_hotel_columns:
        if col in df.columns:
            return col

    return None


# =====================================================
# Translation Functions
# =====================================================
def load_translation_cache() -> dict:
    if OUTPUT_TRANSLATION_CACHE.exists():
        cache_df = pd.read_csv(OUTPUT_TRANSLATION_CACHE, encoding="utf-8-sig")

        required_cols = {"Original_Text", "Translated_Text"}
        if required_cols.issubset(set(cache_df.columns)):
            return dict(zip(cache_df["Original_Text"], cache_df["Translated_Text"]))

    return {}


def save_translation_cache(cache: dict) -> None:
    cache_df = pd.DataFrame([
        {
            "Original_Text": original,
            "Translated_Text": translated
        }
        for original, translated in cache.items()
    ])

    cache_df.to_csv(OUTPUT_TRANSLATION_CACHE, index=False, encoding="utf-8-sig")


def normalize_malay_slang_before_translation(text: str) -> str:
    text = str(text)

    for pattern, replacement in MALAY_SLANG_MAPPING.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_language_safe(text: str) -> str:
    text = str(text).strip()

    if text == "":
        return "unknown"

    if not TRANSLATION_AVAILABLE:
        return "unknown"

    try:
        return detect(text)
    except Exception:
        return "unknown"


def has_malay_marker(text: str) -> bool:
    tokens = re.findall(r"[a-zA-Z]+", str(text).lower())
    return any(token in MALAY_MARKERS for token in tokens)


def looks_like_english_hotel_review(text: str) -> bool:
    text = str(text).strip()

    if text == "":
        return False

    tokens = re.findall(r"[a-zA-Z]+", text.lower())

    if len(tokens) < 3:
        return False

    if has_malay_marker(text):
        return False

    english_word_count = sum(
        1 for token in tokens if token in COMMON_ENGLISH_HOTEL_WORDS
    )

    english_ratio = english_word_count / len(tokens)

    if english_ratio >= 0.35:
        return True

    if text.isascii() and english_word_count >= 2:
        return True

    return False


def translate_to_english_safe(text: str, translation_cache: dict):
    original_text = str(text).strip()

    if original_text == "":
        return original_text, "unknown", False

    if not TRANSLATION_AVAILABLE:
        return original_text, "translation_package_not_installed", False

    text_for_translation = normalize_malay_slang_before_translation(original_text)
    detected_language = detect_language_safe(text_for_translation)

    if detected_language != "en" and looks_like_english_hotel_review(original_text):
        return original_text, "en_assumed", False

    if detected_language == "en":
        return original_text, detected_language, False

    if detected_language == "unknown":
        return original_text, detected_language, False

    cache_key = original_text

    if cache_key in translation_cache:
        return translation_cache[cache_key], detected_language, True

    try:
        translated_text = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text_for_translation)

        if translated_text is None or str(translated_text).strip() == "":
            return original_text, detected_language, False

        translated_text = str(translated_text).strip()
        translation_cache[cache_key] = translated_text

        return translated_text, detected_language, True

    except Exception as e:
        print(f"Translation failed for text: {original_text[:80]}")
        print("Reason:", e)
        return original_text, detected_language, False


# =====================================================
# Text Processing Functions
# =====================================================
def replace_emoji_and_emoticon(text: str) -> str:
    text = str(text)

    for emoji, replacement in EMOJI_MAPPING.items():
        text = text.replace(emoji, replacement)

    for emoticon, replacement in EMOTICON_MAPPING.items():
        text = text.replace(emoticon, replacement)

    return text


def normalize_typos(text: str) -> str:
    text = str(text)

    for wrong, correct in TYPO_MAPPING.items():
        pattern = r"\b" + re.escape(wrong) + r"\b"
        text = re.sub(pattern, correct, text, flags=re.IGNORECASE)

    return text


def normalize_contractions(text: str) -> str:
    text = str(text)

    contractions = {
        "can't": "cannot",
        "won't": "will not",
        "n't": " not",
        "i'm": "i am",
        "it's": "it is",
        "that's": "that is",
        "there's": "there is",
        "they're": "they are",
        "we're": "we are",
        "you're": "you are",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "haven't": "have not",
        "hasn't": "has not",
        "hadn't": "had not",
    }

    text_lower = text.lower()

    for contraction, full_form in contractions.items():
        text_lower = text_lower.replace(contraction, full_form)

    return text_lower


def clean_text_for_traditional_model(text: str) -> str:
    text = str(text)
    text = html.unescape(text)

    text = replace_emoji_and_emoticon(text)
    text = text.lower()
    text = normalize_contractions(text)
    text = normalize_typos(text)

    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_text_for_bert(text: str) -> str:
    text = str(text)
    text = html.unescape(text)

    text = replace_emoji_and_emoticon(text)
    text = normalize_typos(text)

    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_sentiment(label: str) -> str:
    label = str(label).strip().lower()
    return SENTIMENT_MAPPING.get(label, label)


# =====================================================
# Dataset Sorting Helper
# =====================================================
def sort_by_sentiment_and_hotel(df: pd.DataFrame, hotel_col: str | None) -> pd.DataFrame:
    df = df.copy()
    df["_Sentiment_Order"] = df["Sentiment"].map(SENTIMENT_SORT_ORDER)

    if hotel_col is not None and hotel_col in df.columns:
        df[hotel_col] = df[hotel_col].astype(str).str.strip()

        df = df.sort_values(
            by=["_Sentiment_Order", hotel_col, "Review_Text"],
            ascending=[True, True, True]
        ).reset_index(drop=True)

        print(f"\nFinal dataset sorted by Sentiment order and hotel column: {hotel_col}")
    else:
        df = df.sort_values(
            by=["_Sentiment_Order", "Review_Text"],
            ascending=[True, True]
        ).reset_index(drop=True)

        print("\nNo hotel column detected. Final dataset sorted by Sentiment order and Review_Text.")

    df = df.drop(columns=["_Sentiment_Order"])

    return df


# =====================================================
# Main Preprocessing Function
# =====================================================
def main():
    print("========================================")
    print(" Hotel Review Dataset Preprocessing")
    print("========================================")

    if not TRANSLATION_AVAILABLE:
        print("\nWarning: Translation packages are not installed.")
        print("Run: pip install langdetect deep-translator")
        print("The script will continue without translation.\n")

    df = load_input_dataset()

    print("\nOriginal dataset shape:", df.shape)
    print("Original columns:", list(df.columns))

    text_col = detect_text_column(df)
    sentiment_col = detect_sentiment_column(df)
    hotel_col = detect_hotel_column(df)

    print("\nDetected text column:", text_col)
    print("Detected sentiment column:", sentiment_col)

    if hotel_col is not None:
        print("Detected hotel column:", hotel_col)
    else:
        print("Detected hotel column: None")

    df = df.copy()

    # =====================================================
    # Standardise source column
    # =====================================================
    if "source" in df.columns:
        df["source"] = "Agoda"
    elif "Source" in df.columns:
        df["Source"] = "Agoda"

    df["Review_Text"] = df[text_col].astype(str)
    df["Sentiment"] = df[sentiment_col].apply(normalize_sentiment)

    original_rows = len(df)

    # =====================================================
    # Translation to English
    # =====================================================
    print("\nDetecting language and translating non-English reviews...")

    translation_cache = load_translation_cache()

    translation_results = df["Review_Text"].apply(
        lambda text: translate_to_english_safe(text, translation_cache)
    )

    df["Translated_Text"] = translation_results.apply(lambda x: x[0])
    df["Detected_Language"] = translation_results.apply(lambda x: x[1])
    df["Translation_Applied"] = translation_results.apply(lambda x: x[2])

    save_translation_cache(translation_cache)

    print("\nLanguage distribution:")
    print(df["Detected_Language"].value_counts())

    print("Number of translated reviews:", int(df["Translation_Applied"].sum()))

    # =====================================================
    # Remove empty values
    # =====================================================
    before_empty_filter = len(df)

    df = df.dropna(subset=["Review_Text", "Translated_Text", "Sentiment"])
    df = df[df["Review_Text"].str.strip() != ""]
    df = df[df["Translated_Text"].str.strip() != ""]
    df = df[df["Sentiment"].str.strip() != ""]

    after_empty_filter = len(df)

    print("\nRows removed due to empty review/sentiment:", before_empty_filter - after_empty_filter)

    # =====================================================
    # Keep only valid sentiment labels
    # =====================================================
    valid_sentiments = ["positive", "neutral", "negative"]

    before_valid_filter = len(df)
    df = df[df["Sentiment"].isin(valid_sentiments)]
    after_valid_filter = len(df)

    print("Rows removed due to invalid sentiment labels:", before_valid_filter - after_valid_filter)

    # =====================================================
    # Create cleaned text columns
    # =====================================================
    df["Cleaned_Text"] = df["Translated_Text"].apply(clean_text_for_traditional_model)
    df["BERT_Text"] = df["Translated_Text"].apply(clean_text_for_bert)

    # =====================================================
    # Remove short text
    # =====================================================
    before_short_filter = len(df)

    df["Word_Count"] = df["Cleaned_Text"].apply(lambda x: len(str(x).split()))
    df = df[df["Word_Count"] >= 3]

    after_short_filter = len(df)

    print("Rows removed because cleaned text is too short:", before_short_filter - after_short_filter)

    # =====================================================
    # Remove duplicate text
    # =====================================================
    before_duplicates = len(df)

    df = df.drop_duplicates(subset=["Cleaned_Text"])

    after_duplicates = len(df)

    print("Duplicate rows removed:", before_duplicates - after_duplicates)

    # =====================================================
    # Balance Dataset After Preprocessing
    # =====================================================
    before_balance = len(df)

    class_counts = df["Sentiment"].value_counts()
    min_class_count = class_counts.min()

    balanced_parts = []

    for sentiment, group_df in df.groupby("Sentiment"):
        balanced_parts.append(
            group_df.sample(n=min_class_count, random_state=42)
        )

    df = pd.concat(balanced_parts).reset_index(drop=True)

    after_balance = len(df)

    print("\nDataset balanced after preprocessing.")
    print("Rows removed during balancing:", before_balance - after_balance)
    print("Balanced sentiment distribution:")
    print(df["Sentiment"].value_counts())

    # =====================================================
    # Add Label ID
    # =====================================================
    df["Label_ID"] = df["Sentiment"].map(LABEL_ID_MAPPING)

    # =====================================================
    # Reorder columns
    # =====================================================
    final_columns = [
        "Review_Text",
        "Detected_Language",
        "Translation_Applied",
        "Translated_Text",
        "Cleaned_Text",
        "BERT_Text",
        "Sentiment",
        "Label_ID",
        "Word_Count",
    ]

    extra_columns = [
        col for col in df.columns
        if col not in final_columns and col not in [text_col, sentiment_col]
    ]

    df = df[final_columns + extra_columns]

    # =====================================================
    # Sort final full dataset for checking/reporting
    # positive -> neutral -> negative
    # Inside each sentiment, group by same hotel
    # =====================================================
    df = sort_by_sentiment_and_hotel(df, hotel_col)

    print("\nFinal dataset shape:", df.shape)
    print("\nFinal sentiment distribution:")
    print(df["Sentiment"].value_counts())

    # =====================================================
    # Save full preprocessed dataset
    # =====================================================
    df.to_csv(OUTPUT_PREPROCESSED, index=False, encoding="utf-8-sig")

    # =====================================================
    # Train-test split
    # Important:
    # The full preprocessed file is sorted for readability.
    # But train-test split must still shuffle + stratify for fair training/testing.
    # =====================================================
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["Sentiment"],
        shuffle=True
    )

    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    train_df.to_csv(OUTPUT_TRAIN, index=False, encoding="utf-8-sig")
    test_df.to_csv(OUTPUT_TEST, index=False, encoding="utf-8-sig")

    print("\nTrain dataset shape:", train_df.shape)
    print("Test dataset shape:", test_df.shape)

    print("\nTrain sentiment distribution:")
    print(train_df["Sentiment"].value_counts())

    print("\nTest sentiment distribution:")
    print(test_df["Sentiment"].value_counts())

    # =====================================================
    # Save preprocessing summary
    # =====================================================
    summary_rows = [
        {
            "Item": "Original Rows",
            "Value": original_rows,
        },
        {
            "Item": "Rows After Empty Removal",
            "Value": after_empty_filter,
        },
        {
            "Item": "Rows After Valid Sentiment Filter",
            "Value": after_valid_filter,
        },
        {
            "Item": "Rows After Short Text Filter",
            "Value": after_short_filter,
        },
        {
            "Item": "Rows After Duplicate Removal",
            "Value": after_duplicates,
        },
        {
            "Item": "Rows After Balancing",
            "Value": after_balance,
        },
        {
            "Item": "Rows Removed During Balancing",
            "Value": before_balance - after_balance,
        },
        {
            "Item": "Translated Reviews",
            "Value": int(df["Translation_Applied"].sum()),
        },
        {
            "Item": "Detected Languages",
            "Value": ", ".join(df["Detected_Language"].value_counts().index.astype(str).tolist()),
        },
        {
            "Item": "Train Rows",
            "Value": len(train_df),
        },
        {
            "Item": "Test Rows",
            "Value": len(test_df),
        },
        {
            "Item": "Positive Reviews",
            "Value": int(df["Sentiment"].value_counts().get("positive", 0)),
        },
        {
            "Item": "Neutral Reviews",
            "Value": int(df["Sentiment"].value_counts().get("neutral", 0)),
        },
        {
            "Item": "Negative Reviews",
            "Value": int(df["Sentiment"].value_counts().get("negative", 0)),
        },
    ]

    if hotel_col is not None and hotel_col in df.columns:
        summary_rows.append(
            {
                "Item": "Hotel Column Used For Sorting",
                "Value": hotel_col,
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(OUTPUT_SUMMARY, index=False, encoding="utf-8-sig")

    print("\nFiles saved successfully:")
    print("-", OUTPUT_PREPROCESSED)
    print("-", OUTPUT_TRAIN)
    print("-", OUTPUT_TEST)
    print("-", OUTPUT_SUMMARY)
    print("-", OUTPUT_TRANSLATION_CACHE)

    print("\nPreprocessing completed successfully.")


if __name__ == "__main__":
    main()