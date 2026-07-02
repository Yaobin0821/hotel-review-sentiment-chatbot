# scripts/train_logistic_regression.py

from pathlib import Path
import json
import joblib

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize


# =====================================================
# Configuration
# =====================================================
MODEL_NAME = "logistic_regression"

BASE_DIR = Path(__file__).resolve().parents[1]

TRAIN_PATH = BASE_DIR / "data" / "train_dataset.csv"
TEST_PATH = BASE_DIR / "data" / "test_dataset.csv"

MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"
GRAPH_DIR = BASE_DIR / "graphs"

TEXT_COLUMN = "Cleaned_Text"
LABEL_COLUMN = "Sentiment"

LABEL_ORDER = ["negative", "neutral", "positive"]

RANDOM_STATE = 42


# =====================================================
# Utility Functions
# =====================================================
def ensure_directories():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_safe(file_path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="latin1")


def load_dataset(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = read_csv_safe(file_path)

    required_columns = [TEXT_COLUMN, LABEL_COLUMN]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in {file_path}")

    df[TEXT_COLUMN] = df[TEXT_COLUMN].fillna("").astype(str).str.strip()
    df[LABEL_COLUMN] = df[LABEL_COLUMN].fillna("").astype(str).str.strip().str.lower()

    df = df[df[TEXT_COLUMN] != ""].copy()
    df = df[df[LABEL_COLUMN].isin(LABEL_ORDER)].copy()

    if df.empty:
        raise ValueError(f"Dataset is empty after cleaning: {file_path}")

    return df.reset_index(drop=True)


def save_text_report(text: str, file_path: Path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def save_json(data: dict, file_path: Path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def check_train_test_leakage(train_df: pd.DataFrame, test_df: pd.DataFrame):
    train_text_set = set(train_df[TEXT_COLUMN].astype(str))
    test_text_set = set(test_df[TEXT_COLUMN].astype(str))

    overlap_texts = train_text_set.intersection(test_text_set)

    if overlap_texts:
        print(f"\nWarning: {len(overlap_texts)} duplicated texts found in both train and test set.")
        print("This may cause data leakage. Please check your preprocessing split.")
    else:
        print("\nNo duplicated texts found between train and test set.")

    return overlap_texts


# =====================================================
# Plot Functions
# =====================================================
def plot_confusion_matrix(cm, labels, save_path: Path):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(len(labels)),
        yticks=np.arange(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="Actual Label",
        xlabel="Predicted Label",
        title="Logistic Regression - Confusion Matrix",
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    threshold = cm.max() / 2 if cm.max() > 0 else 0

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], "d"),
                ha="center",
                va="center",
                color="white" if cm[i, j] > threshold else "black",
            )

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_class_metrics(report_dict, labels, save_path: Path):
    precisions = [report_dict[label]["precision"] for label in labels]
    recalls = [report_dict[label]["recall"] for label in labels]
    f1_scores = [report_dict[label]["f1-score"] for label in labels]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width, precisions, width, label="Precision")
    bars2 = ax.bar(x, recalls, width, label="Recall")
    bars3 = ax.bar(x + width, f1_scores, width, label="F1-score")

    ax.set_title("Logistic Regression - Per-Class Metrics")
    ax.set_xlabel("Sentiment Class")
    ax.set_ylabel("Score")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.05)
    ax.legend()

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_overall_metrics(metrics: dict, save_path: Path):
    names = ["Accuracy", "Macro Precision", "Macro Recall", "Macro F1"]
    values = [
        metrics["accuracy"],
        metrics["macro_precision"],
        metrics["macro_recall"],
        metrics["macro_f1"],
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(names, values)

    ax.set_title("Logistic Regression - Overall Metrics")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.xticks(rotation=15)
    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_multiclass_roc(y_true, y_prob, labels, save_path: Path):
    y_true_bin = label_binarize(y_true, classes=labels)

    fig, ax = plt.subplots(figsize=(8, 6))

    for i, label in enumerate(labels):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)

        ax.plot(
            fpr,
            tpr,
            lw=2,
            label=f"{label} (AUC = {roc_auc:.3f})",
        )

    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1)

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Logistic Regression - ROC Curve (One-vs-Rest)")
    ax.legend(loc="lower right")

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


# =====================================================
# Main Training Function
# =====================================================
def main():
    print("=" * 60)
    print("Training Logistic Regression Model")
    print("=" * 60)

    ensure_directories()

    # =====================================================
    # Load data
    # =====================================================
    train_df = load_dataset(TRAIN_PATH)
    test_df = load_dataset(TEST_PATH)

    print(f"\nTrain dataset shape: {train_df.shape}")
    print(f"Test dataset shape: {test_df.shape}")

    print("\nTrain label distribution:")
    print(train_df[LABEL_COLUMN].value_counts())

    print("\nTest label distribution:")
    print(test_df[LABEL_COLUMN].value_counts())

    overlap_texts = check_train_test_leakage(train_df, test_df)

    X_train = train_df[TEXT_COLUMN]
    y_train = train_df[LABEL_COLUMN]

    X_test = test_df[TEXT_COLUMN]
    y_test = test_df[LABEL_COLUMN]

    # =====================================================
    # Build pipeline
    # =====================================================
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                    max_features=10000,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                    solver="lbfgs",
                ),
            ),
        ]
    )

    print("\nTraining configuration:")
    print(f"Text column: {TEXT_COLUMN}")
    print(f"Label column: {LABEL_COLUMN}")
    print("Algorithm: TF-IDF + Logistic Regression")
    print("TF-IDF ngram range: (1, 2)")
    print("TF-IDF max features: 10000")
    print("Logistic Regression solver: lbfgs")
    print("Logistic Regression max_iter: 2000")

    # =====================================================
    # Train
    # =====================================================
    print("\nTraining model...")
    pipeline.fit(X_train, y_train)

    # =====================================================
    # Predict
    # =====================================================
    print("\nEvaluating model...")

    y_pred = pipeline.predict(X_test)
    y_prob_raw = pipeline.predict_proba(X_test)

    model_classes = list(pipeline.named_steps["classifier"].classes_)

    missing_classes = [label for label in LABEL_ORDER if label not in model_classes]
    if missing_classes:
        raise ValueError(
            f"Model did not learn all required classes. Missing classes: {missing_classes}"
        )

    prob_df = pd.DataFrame(y_prob_raw, columns=model_classes)
    prob_df = prob_df[LABEL_ORDER]
    y_prob = prob_df.values

    # =====================================================
    # Metrics
    # =====================================================
    accuracy = accuracy_score(y_test, y_pred)

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        average="macro",
        zero_division=0,
    )

    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    report_dict = classification_report(
        y_test,
        y_pred,
        labels=LABEL_ORDER,
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        y_test,
        y_pred,
        labels=LABEL_ORDER,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=LABEL_ORDER,
    )

    # =====================================================
    # Save model
    # =====================================================
    model_path = MODEL_DIR / f"{MODEL_NAME}_model.pkl"

    joblib.dump(pipeline, model_path)

    # =====================================================
    # Save metrics summary
    # =====================================================
    metrics_summary = {
        "model_name": MODEL_NAME,
        "algorithm": "TF-IDF + Logistic Regression",
        "text_column": TEXT_COLUMN,
        "label_column": LABEL_COLUMN,
        "train_file": str(TRAIN_PATH),
        "test_file": str(TEST_PATH),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_precision),
        "weighted_recall": float(weighted_recall),
        "weighted_f1": float(weighted_f1),
        "train_test_duplicate_text_count": int(len(overlap_texts)),
    }

    metrics_df = pd.DataFrame([metrics_summary])

    metrics_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_metrics_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # =====================================================
    # Save classification report
    # =====================================================
    report_df = pd.DataFrame(report_dict).transpose()

    report_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_classification_report.csv",
        index=True,
        encoding="utf-8-sig",
    )

    save_text_report(
        report_text,
        REPORT_DIR / f"{MODEL_NAME}_classification_report.txt",
    )

    # =====================================================
    # Save confusion matrix
    # =====================================================
    cm_df = pd.DataFrame(
        cm,
        index=LABEL_ORDER,
        columns=LABEL_ORDER,
    )

    cm_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_confusion_matrix.csv",
        encoding="utf-8-sig",
    )

    # =====================================================
    # Save predictions with original metadata
    # =====================================================
    predictions_df = test_df.reset_index(drop=True).copy()

    predictions_df["Actual_Label"] = y_test.values
    predictions_df["Predicted_Label"] = y_pred
    predictions_df["Correct"] = y_test.values == y_pred
    predictions_df["Confidence"] = y_prob.max(axis=1)
    predictions_df["Prob_Negative"] = y_prob[:, 0]
    predictions_df["Prob_Neutral"] = y_prob[:, 1]
    predictions_df["Prob_Positive"] = y_prob[:, 2]

    predictions_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_test_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # =====================================================
    # Save misclassified samples with metadata
    # =====================================================
    misclassified_df = predictions_df[predictions_df["Correct"] == False].copy()

    misclassified_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_misclassified_samples.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # =====================================================
    # Save model config
    # =====================================================
    save_json(
        {
            "model_name": MODEL_NAME,
            "algorithm": "TF-IDF + Logistic Regression",
            "train_file": str(TRAIN_PATH),
            "test_file": str(TEST_PATH),
            "text_column": TEXT_COLUMN,
            "label_column": LABEL_COLUMN,
            "label_order": LABEL_ORDER,
            "random_state": RANDOM_STATE,
            "train_test_duplicate_text_count": int(len(overlap_texts)),
            "tfidf_params": {
                "ngram_range": [1, 2],
                "min_df": 2,
                "max_df": 0.95,
                "sublinear_tf": True,
                "max_features": 10000,
            },
            "logistic_regression_params": {
                "max_iter": 2000,
                "random_state": RANDOM_STATE,
                "solver": "lbfgs",
            },
        },
        REPORT_DIR / f"{MODEL_NAME}_config.json",
    )

    # =====================================================
    # Generate graphs
    # =====================================================
    print("\nGenerating graphs...")

    plot_confusion_matrix(
        cm,
        LABEL_ORDER,
        GRAPH_DIR / f"{MODEL_NAME}_confusion_matrix.png",
    )

    plot_class_metrics(
        report_dict,
        LABEL_ORDER,
        GRAPH_DIR / f"{MODEL_NAME}_per_class_metrics.png",
    )

    plot_overall_metrics(
        metrics_summary,
        GRAPH_DIR / f"{MODEL_NAME}_overall_metrics.png",
    )

    plot_multiclass_roc(
        y_test.values,
        y_prob,
        LABEL_ORDER,
        GRAPH_DIR / f"{MODEL_NAME}_roc_curve.png",
    )

    # =====================================================
    # Print summary
    # =====================================================
    print("\n" + "=" * 60)
    print("Logistic Regression Training Completed Successfully")
    print("=" * 60)

    print(f"Model saved to: {model_path}")

    print("\nEvaluation Results:")
    print(f"Accuracy:          {accuracy:.4f}")
    print(f"Macro Precision:   {macro_precision:.4f}")
    print(f"Macro Recall:      {macro_recall:.4f}")
    print(f"Macro F1-score:    {macro_f1:.4f}")
    print(f"Weighted F1-score: {weighted_f1:.4f}")

    print("\nGenerated report files:")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_metrics_summary.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_classification_report.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_classification_report.txt'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_confusion_matrix.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_test_predictions.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_misclassified_samples.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_config.json'}")

    print("\nGenerated graph files:")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_confusion_matrix.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_per_class_metrics.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_overall_metrics.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_roc_curve.png'}")


if __name__ == "__main__":
    main()