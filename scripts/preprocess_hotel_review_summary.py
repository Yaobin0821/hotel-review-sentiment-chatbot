import re
import json
import time
from pathlib import Path

import pandas as pd



BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "Hotel_Review_Summary_Final.csv"
OUTPUT_FILE = BASE_DIR / "data" / "Hotel_Review_Summary_Processed.csv"

REPORT_DIR = BASE_DIR / "reports"
CACHE_FILE = BASE_DIR / "data" / "translation_cache_hotel_reviews.json"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

ENABLE_TRANSLATION = True
TRANSLATION_SLEEP_SECONDS = 0.35



try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False



POSITIVE_EMOJIS = [
    "😊", "😍", "👍", "😁", "😄", "❤️", "✨", "🥰", "👏", "✅",
    "😃", "😆", "🤩", "💯", "🌟", "⭐"
]

NEGATIVE_EMOJIS = [
    "😡", "😠", "👎", "😞", "😢", "🤮", "😤", "❌", "💔", "😭",
    "😣", "😖", "😫", "😩", "🙄"
]

NEUTRAL_EMOJIS = [
    "😐", "🤔", "🙂", "😶", "😑"
]

POSITIVE_EMOTICONS = [
    ":)", ":-)", ":D", ":-D", ";)", ";-)", "=)", "(y)"
]

NEGATIVE_EMOTICONS = [
    ":(", ":-(", ":'(", ">:(", ":-/", ":/", "=("
]

NEUTRAL_EMOTICONS = [
    ":|", ":-|"
]


EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE
)



def safe_text(value, default=""):
    if pd.isna(value):
        return default

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return default

    return text


def normalize_spaces(text):
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


def load_translation_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    return {}


def save_translation_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)



def detect_review_language(text):
    text = safe_text(text)

    if text == "":
        return "unknown"

    if not LANGDETECT_AVAILABLE:
        return "en_assumed"

    try:
        language = detect(text)
        return language
    except Exception:
        return "unknown"



def translate_to_english(text, detected_language, cache):
    text = safe_text(text)

    if text == "":
        return ""

    if detected_language in ["en", "en_assumed", "unknown"]:
        return text

    if text in cache:
        return cache[text]

    if not ENABLE_TRANSLATION:
        return text

    if not DEEP_TRANSLATOR_AVAILABLE:
        print(
            f"Translation skipped because deep-translator is not installed. "
            f"Language: {detected_language}"
        )
        return text

    try:
        translated_text = GoogleTranslator(source="auto", target="en").translate(text)
        translated_text = normalize_spaces(translated_text)

        if translated_text == "":
            translated_text = text

        cache[text] = translated_text
        time.sleep(TRANSLATION_SLEEP_SECONDS)

        return translated_text

    except Exception as error:
        print(f"Translation failed for language {detected_language}: {error}")
        return text



def extract_unicode_emojis(text):
    text = safe_text(text)
    return EMOJI_PATTERN.findall(text)


def detect_emoji_signals(text):
    text = safe_text(text)

    positive_signals = []
    negative_signals = []
    neutral_signals = []

    for signal in POSITIVE_EMOJIS + POSITIVE_EMOTICONS:
        if signal in text:
            positive_signals.append(signal)

    for signal in NEGATIVE_EMOJIS + NEGATIVE_EMOTICONS:
        if signal in text:
            negative_signals.append(signal)

    for signal in NEUTRAL_EMOJIS + NEUTRAL_EMOTICONS:
        if signal in text:
            neutral_signals.append(signal)

    all_unicode_emojis = extract_unicode_emojis(text)

    positive_count = len(positive_signals)
    negative_count = len(negative_signals)
    neutral_count = len(neutral_signals)

    if positive_count == 0 and negative_count == 0 and neutral_count == 0:
        emoji_sentiment = "No emoji signal"
    elif positive_count > negative_count and positive_count >= neutral_count:
        emoji_sentiment = "Positive"
    elif negative_count > positive_count and negative_count >= neutral_count:
        emoji_sentiment = "Negative"
    elif neutral_count > positive_count and neutral_count > negative_count:
        emoji_sentiment = "Neutral"
    else:
        emoji_sentiment = "Mixed"

    return {
        "emoji_sentiment": emoji_sentiment,
        "positive_signals": " ".join(positive_signals),
        "negative_signals": " ".join(negative_signals),
        "neutral_signals": " ".join(neutral_signals),
        "all_emoji_detected": " ".join(all_unicode_emojis),
        "emoji_count": len(all_unicode_emojis),
        "emoji_signal_count": positive_count + negative_count + neutral_count
    }


def remove_emojis_and_emoticons(text):
    text = safe_text(text)

    text = EMOJI_PATTERN.sub(" ", text)

    all_emoticons = POSITIVE_EMOTICONS + NEGATIVE_EMOTICONS + NEUTRAL_EMOTICONS

    for emoticon in all_emoticons:
        text = text.replace(emoticon, " ")

    return normalize_spaces(text)



def clean_text_for_keyword_analysis(text):
    text = safe_text(text)
    text = remove_emojis_and_emoticons(text)
    text = text.lower()

    contractions = {
        "can't": "cannot",
        "won't": "will not",
        "n't": " not",
        "'re": " are",
        "'s": " is",
        "'d": " would",
        "'ll": " will",
        "'t": " not",
        "'ve": " have",
        "'m": " am"
    }

    for old, new in contractions.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = normalize_spaces(text)

    return text


def prepare_bert_text(text):
    text = safe_text(text)
    text = normalize_spaces(text)
    return text



def standardize_sentiment_label(value):
    value = safe_text(value).lower()

    mapping = {
        "positive": "positive",
        "pos": "positive",
        "good": "positive",
        "neutral": "neutral",
        "neu": "neutral",
        "mixed": "neutral",
        "negative": "negative",
        "neg": "negative",
        "bad": "negative"
    }

    return mapping.get(value, value)


def standardize_area_label(value):
    value = safe_text(value).lower()

    mapping = {
        "klcc": "klcc",
        "kuala lumpur city centre": "klcc",
        "kuala lumpur city center": "klcc",
        "bukit jalil": "bukit jalil",
        "petaling jaya": "petaling jaya",
        "pj": "petaling jaya",
        "sunway": "sunway"
    }

    return mapping.get(value, value)


def standardize_source_label(value):
    return safe_text(value).lower()


def standardize_general_label(value):
    return normalize_spaces(safe_text(value))



def validate_required_columns(df):
    required_columns = [
        "ID",
        "Review",
        "Hotel_name",
        "Hotel_Address",
        "sentiment",
        "area",
        "risk_type",
        "Traveller_Suitability",
        "Improvement_Area",
        "Aspect",
        "Source"
    ]

    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")



def create_language_report(df):
    language_report = (
        df["Detected_Language"]
        .value_counts()
        .reset_index()
    )

    language_report.columns = ["Detected_Language", "Count"]

    language_report.to_csv(
        REPORT_DIR / "preprocessing_language_distribution.csv",
        index=False,
        encoding="utf-8-sig"
    )


def create_emoji_report(df):
    emoji_report = (
        df["Emoji_Sentiment"]
        .value_counts()
        .reset_index()
    )

    emoji_report.columns = ["Emoji_Sentiment", "Count"]

    emoji_report.to_csv(
        REPORT_DIR / "preprocessing_emoji_distribution.csv",
        index=False,
        encoding="utf-8-sig"
    )


def create_hotel_summary_report(df):
    summary_rows = []

    for hotel_name, hotel_df in df.groupby("Hotel_name"):
        total = len(hotel_df)

        sentiment_counts = hotel_df["sentiment"].value_counts()

        positive_count = int(sentiment_counts.get("positive", 0))
        neutral_count = int(sentiment_counts.get("neutral", 0))
        negative_count = int(sentiment_counts.get("negative", 0))

        if total == 0:
            positive_pct = 0
            neutral_pct = 0
            negative_pct = 0
        else:
            positive_pct = round((positive_count / total) * 100, 2)
            neutral_pct = round((neutral_count / total) * 100, 2)
            negative_pct = round((negative_count / total) * 100, 2)

        area = hotel_df["area"].mode().iloc[0] if not hotel_df["area"].mode().empty else ""
        source = hotel_df["Source"].mode().iloc[0] if not hotel_df["Source"].mode().empty else ""

        summary_rows.append({
            "Hotel_name": hotel_name,
            "area": area,
            "Source": source,
            "Total_Reviews": total,
            "Positive_Count": positive_count,
            "Neutral_Count": neutral_count,
            "Negative_Count": negative_count,
            "Positive_Percentage": positive_pct,
            "Neutral_Percentage": neutral_pct,
            "Negative_Percentage": negative_pct,
            "Top_Aspect": hotel_df["Aspect"].value_counts().index[0] if not hotel_df["Aspect"].value_counts().empty else "",
            "Top_Risk_Type": hotel_df["risk_type"].value_counts().index[0] if not hotel_df["risk_type"].value_counts().empty else "",
            "Top_Traveller_Suitability": hotel_df["Traveller_Suitability"].value_counts().index[0] if not hotel_df["Traveller_Suitability"].value_counts().empty else "",
            "Top_Improvement_Area": hotel_df["Improvement_Area"].value_counts().index[0] if not hotel_df["Improvement_Area"].value_counts().empty else "",
        })

    summary_df = pd.DataFrame(summary_rows)

    summary_df.to_csv(
        REPORT_DIR / "preprocessing_summary_by_hotel.csv",
        index=False,
        encoding="utf-8-sig"
    )



def preprocess_dataset():
    print("=" * 70)
    print("Hotel Review Summary Dataset Preprocessing")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    print(f"Reading input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    validate_required_columns(df)

    print(f"Original shape: {df.shape}")
    print(f"Original columns: {list(df.columns)}")

    df = df.copy()

    df["Original_Review"] = df["Review"].apply(safe_text)
    df["Original_Sentiment"] = df["sentiment"].apply(safe_text)
    df["Original_Area"] = df["area"].apply(safe_text)

    text_columns = [
        "Review",
        "Hotel_name",
        "Hotel_Address",
        "sentiment",
        "area",
        "risk_type",
        "Traveller_Suitability",
        "Improvement_Area",
        "Aspect",
        "Source"
    ]

    for column in text_columns:
        df[column] = df[column].apply(safe_text)

    before_empty_filter = len(df)

    df = df[
        (df["Review"].str.strip() != "")
        & (df["Hotel_name"].str.strip() != "")
    ].copy()

    removed_empty_rows = before_empty_filter - len(df)

    print(f"Removed empty review / hotel name rows: {removed_empty_rows}")

    df["Is_Duplicate_Review"] = df.duplicated(
        subset=["Hotel_name", "Review"],
        keep="first"
    )

    duplicate_count = int(df["Is_Duplicate_Review"].sum())

    print(f"Duplicate review rows detected: {duplicate_count}")

    df["sentiment"] = df["sentiment"].apply(standardize_sentiment_label)
    df["area"] = df["area"].apply(standardize_area_label)
    df["Source"] = df["Source"].apply(standardize_source_label)
    df["risk_type"] = df["risk_type"].apply(standardize_general_label)
    df["Traveller_Suitability"] = df["Traveller_Suitability"].apply(standardize_general_label)
    df["Improvement_Area"] = df["Improvement_Area"].apply(standardize_general_label)
    df["Aspect"] = df["Aspect"].apply(standardize_general_label)
    df["Hotel_name"] = df["Hotel_name"].apply(standardize_general_label)
    df["Hotel_Address"] = df["Hotel_Address"].apply(standardize_general_label)

    print("Detecting language...")

    df["Detected_Language"] = df["Original_Review"].apply(detect_review_language)

    language_distribution = df["Detected_Language"].value_counts()

    print("\nLanguage distribution:")
    print(language_distribution)

    print("\nExtracting emoji and emoticon signals...")

    emoji_results = df["Original_Review"].apply(detect_emoji_signals)

    df["Emoji_Sentiment"] = emoji_results.apply(lambda result: result["emoji_sentiment"])
    df["Positive_Emoji_Signals"] = emoji_results.apply(lambda result: result["positive_signals"])
    df["Negative_Emoji_Signals"] = emoji_results.apply(lambda result: result["negative_signals"])
    df["Neutral_Emoji_Signals"] = emoji_results.apply(lambda result: result["neutral_signals"])
    df["All_Emoji_Detected"] = emoji_results.apply(lambda result: result["all_emoji_detected"])
    df["Emoji_Count"] = emoji_results.apply(lambda result: result["emoji_count"])
    df["Emoji_Signal_Count"] = emoji_results.apply(lambda result: result["emoji_signal_count"])

    print("\nEmoji signal distribution:")
    print(df["Emoji_Sentiment"].value_counts())

    print("\nTranslating non-English reviews when needed...")

    translation_cache = load_translation_cache()

    translated_reviews = []

    for index, row in df.iterrows():
        original_review = row["Original_Review"]
        detected_language = row["Detected_Language"]

        translated_review = translate_to_english(
            text=original_review,
            detected_language=detected_language,
            cache=translation_cache
        )

        translated_reviews.append(translated_review)

        if (len(translated_reviews) % 100) == 0:
            print(f"Processed translations: {len(translated_reviews)} / {len(df)}")
            save_translation_cache(translation_cache)

    df["Translated_Review"] = translated_reviews

    save_translation_cache(translation_cache)

    print("\nPreparing Cleaned_Text and BERT_Text...")

    df["Review_Without_Emoji"] = df["Translated_Review"].apply(remove_emojis_and_emoticons)
    df["Cleaned_Text"] = df["Translated_Review"].apply(clean_text_for_keyword_analysis)
    df["BERT_Text"] = df["Translated_Review"].apply(prepare_bert_text)

    df["Needs_Translation"] = ~df["Detected_Language"].isin(["en", "en_assumed", "unknown"])
    df["Was_Translated"] = df["Original_Review"].str.strip() != df["Translated_Review"].str.strip()
    df["Has_Emoji"] = df["Emoji_Count"] > 0
    df["Has_Emoji_Sentiment_Signal"] = df["Emoji_Sentiment"] != "No emoji signal"
    df["Review_Length_Characters"] = df["Original_Review"].apply(len)
    df["Review_Length_Words"] = df["Cleaned_Text"].apply(lambda text: len(str(text).split()))

    preferred_columns = [
        "ID",
        "Hotel_name",
        "Hotel_Address",
        "area",
        "Source",
        "Original_Review",
        "Detected_Language",
        "Translated_Review",
        "Review_Without_Emoji",
        "Cleaned_Text",
        "BERT_Text",
        "sentiment",
        "Original_Sentiment",
        "risk_type",
        "Traveller_Suitability",
        "Improvement_Area",
        "Aspect",
        "Emoji_Sentiment",
        "Positive_Emoji_Signals",
        "Negative_Emoji_Signals",
        "Neutral_Emoji_Signals",
        "All_Emoji_Detected",
        "Emoji_Count",
        "Emoji_Signal_Count",
        "Needs_Translation",
        "Was_Translated",
        "Has_Emoji",
        "Has_Emoji_Sentiment_Signal",
        "Review_Length_Characters",
        "Review_Length_Words",
        "Is_Duplicate_Review",
        "Review",
        "Original_Area"
    ]

    remaining_columns = [
        column for column in df.columns
        if column not in preferred_columns
    ]

    df = df[preferred_columns + remaining_columns]

    print(f"\nSaving processed dataset to: {OUTPUT_FILE}")

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Saving preprocessing reports...")

    create_language_report(df)
    create_emoji_report(df)
    create_hotel_summary_report(df)

    print("\nFinal shape:", df.shape)

    print("\nProcessed columns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nOutput files created:")
    print(f"- {OUTPUT_FILE}")
    print(f"- {REPORT_DIR / 'preprocessing_language_distribution.csv'}")
    print(f"- {REPORT_DIR / 'preprocessing_emoji_distribution.csv'}")
    print(f"- {REPORT_DIR / 'preprocessing_summary_by_hotel.csv'}")

    print("\nDone.")


if __name__ == "__main__":
    preprocess_dataset()