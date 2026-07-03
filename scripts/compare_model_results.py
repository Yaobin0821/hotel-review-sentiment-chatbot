
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]

REPORT_DIR = BASE_DIR / "reports"
GRAPH_DIR = BASE_DIR / "graphs"

MODEL_ORDER = [
    "logistic_regression",
    "bilstm",
    "distilbert",
]

MODEL_DISPLAY_NAMES = {
    "logistic_regression": "Logistic Regression",
    "bilstm": "BiLSTM",
    "distilbert": "DistilBERT",
}

LABEL_ORDER = ["negative", "neutral", "positive"]

OVERALL_METRICS = [
    "accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1",
    "weighted_precision",
    "weighted_recall",
    "weighted_f1",
]


def ensure_directories():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)


def safe_read_csv(file_path: Path, index_col=None):
    if not file_path.exists():
        print(f"[WARNING] Missing file: {file_path}")
        return None

    try:
        return pd.read_csv(file_path, index_col=index_col)
    except Exception as e:
        print(f"[WARNING] Failed to read {file_path}: {e}")
        return None


def save_json(data: dict, file_path: Path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_text(text: str, file_path: Path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def get_existing_models():
    existing_models = []

    for model_name in MODEL_ORDER:
        metrics_path = REPORT_DIR / f"{model_name}_metrics_summary.csv"

        if metrics_path.exists():
            existing_models.append(model_name)
        else:
            print(f"[INFO] Skipping {model_name}: metrics summary not found.")

    return existing_models


def load_metrics_summary(model_name: str):
    metrics_path = REPORT_DIR / f"{model_name}_metrics_summary.csv"
    df = safe_read_csv(metrics_path)

    if df is None or df.empty:
        return None

    row = df.iloc[0].to_dict()
    row["model_name"] = model_name
    row["model_display_name"] = MODEL_DISPLAY_NAMES.get(model_name, model_name)

    return row


def load_classification_report(model_name: str):
    report_path = REPORT_DIR / f"{model_name}_classification_report.csv"
    df = safe_read_csv(report_path, index_col=0)

    if df is None or df.empty:
        return None

    records = []

    for class_name in LABEL_ORDER:
        if class_name in df.index:
            records.append(
                {
                    "model_name": model_name,
                    "model_display_name": MODEL_DISPLAY_NAMES.get(model_name, model_name),
                    "class": class_name,
                    "precision": float(df.loc[class_name, "precision"]),
                    "recall": float(df.loc[class_name, "recall"]),
                    "f1_score": float(df.loc[class_name, "f1-score"]),
                    "support": int(df.loc[class_name, "support"]),
                }
            )

    return pd.DataFrame(records)


def load_confusion_matrix(model_name: str):
    cm_path = REPORT_DIR / f"{model_name}_confusion_matrix.csv"
    df = safe_read_csv(cm_path, index_col=0)

    if df is None or df.empty:
        return None

    try:
        df = df.loc[LABEL_ORDER, LABEL_ORDER]
    except Exception:
        pass

    records = []

    for actual_label in df.index:
        for predicted_label in df.columns:
            records.append(
                {
                    "model_name": model_name,
                    "model_display_name": MODEL_DISPLAY_NAMES.get(model_name, model_name),
                    "actual_label": actual_label,
                    "predicted_label": predicted_label,
                    "count": int(df.loc[actual_label, predicted_label]),
                }
            )

    return pd.DataFrame(records)


def plot_overall_metrics_comparison(metrics_df: pd.DataFrame, save_path: Path):
    plot_metrics = ["accuracy", "macro_precision", "macro_recall", "macro_f1"]

    available_metrics = [m for m in plot_metrics if m in metrics_df.columns]

    if not available_metrics:
        print("[WARNING] No overall metrics available for plotting.")
        return

    display_names = metrics_df["model_display_name"].tolist()
    x = np.arange(len(display_names))
    width = 0.18

    fig, ax = plt.subplots(figsize=(11, 6))

    for i, metric in enumerate(available_metrics):
        values = metrics_df[metric].astype(float).values
        offset = (i - (len(available_metrics) - 1) / 2) * width

        bars = ax.bar(
            x + offset,
            values,
            width,
            label=metric.replace("_", " ").title(),
        )

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.3f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_title("Overall Model Performance Comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel("Score")
    ax.set_xticks(x)
    ax.set_xticklabels(display_names)
    ax.set_ylim(0, 1.05)
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_accuracy_macro_f1_comparison(metrics_df: pd.DataFrame, save_path: Path):
    required = ["accuracy", "macro_f1"]

    for col in required:
        if col not in metrics_df.columns:
            print(f"[WARNING] Missing {col}; cannot plot accuracy vs macro F1.")
            return

    display_names = metrics_df["model_display_name"].tolist()
    x = np.arange(len(display_names))
    width = 0.35

    accuracy_values = metrics_df["accuracy"].astype(float).values
    macro_f1_values = metrics_df["macro_f1"].astype(float).values

    fig, ax = plt.subplots(figsize=(9, 6))

    bars1 = ax.bar(x - width / 2, accuracy_values, width, label="Accuracy")
    bars2 = ax.bar(x + width / 2, macro_f1_values, width, label="Macro F1-score")

    ax.set_title("Accuracy and Macro F1-score Comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel("Score")
    ax.set_xticks(x)
    ax.set_xticklabels(display_names)
    ax.set_ylim(0, 1.05)
    ax.legend()

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.3f}",
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


def plot_per_class_f1_comparison(class_report_df: pd.DataFrame, save_path: Path):
    if class_report_df.empty:
        print("[WARNING] Class report dataframe is empty.")
        return

    pivot_df = class_report_df.pivot(
        index="class",
        columns="model_display_name",
        values="f1_score",
    )

    pivot_df = pivot_df.reindex(LABEL_ORDER)

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(pivot_df.index))
    model_names = list(pivot_df.columns)
    width = 0.8 / max(len(model_names), 1)

    for i, model_name in enumerate(model_names):
        values = pivot_df[model_name].astype(float).values
        offset = (i - (len(model_names) - 1) / 2) * width

        bars = ax.bar(
            x + offset,
            values,
            width,
            label=model_name,
        )

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_title("Per-Class F1-score Comparison")
    ax.set_xlabel("Sentiment Class")
    ax.set_ylabel("F1-score")
    ax.set_xticks(x)
    ax.set_xticklabels(pivot_df.index)
    ax.set_ylim(0, 1.05)
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_per_class_precision_comparison(class_report_df: pd.DataFrame, save_path: Path):
    if class_report_df.empty:
        print("[WARNING] Class report dataframe is empty.")
        return

    pivot_df = class_report_df.pivot(
        index="class",
        columns="model_display_name",
        values="precision",
    )

    pivot_df = pivot_df.reindex(LABEL_ORDER)

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(pivot_df.index))
    model_names = list(pivot_df.columns)
    width = 0.8 / max(len(model_names), 1)

    for i, model_name in enumerate(model_names):
        values = pivot_df[model_name].astype(float).values
        offset = (i - (len(model_names) - 1) / 2) * width

        bars = ax.bar(
            x + offset,
            values,
            width,
            label=model_name,
        )

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_title("Per-Class Precision Comparison")
    ax.set_xlabel("Sentiment Class")
    ax.set_ylabel("Precision")
    ax.set_xticks(x)
    ax.set_xticklabels(pivot_df.index)
    ax.set_ylim(0, 1.05)
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_per_class_recall_comparison(class_report_df: pd.DataFrame, save_path: Path):
    if class_report_df.empty:
        print("[WARNING] Class report dataframe is empty.")
        return

    pivot_df = class_report_df.pivot(
        index="class",
        columns="model_display_name",
        values="recall",
    )

    pivot_df = pivot_df.reindex(LABEL_ORDER)

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(pivot_df.index))
    model_names = list(pivot_df.columns)
    width = 0.8 / max(len(model_names), 1)

    for i, model_name in enumerate(model_names):
        values = pivot_df[model_name].astype(float).values
        offset = (i - (len(model_names) - 1) / 2) * width

        bars = ax.bar(
            x + offset,
            values,
            width,
            label=model_name,
        )

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_title("Per-Class Recall Comparison")
    ax.set_xlabel("Sentiment Class")
    ax.set_ylabel("Recall")
    ax.set_xticks(x)
    ax.set_xticklabels(pivot_df.index)
    ax.set_ylim(0, 1.05)
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_macro_f1_ranking(metrics_df: pd.DataFrame, save_path: Path):
    if "macro_f1" not in metrics_df.columns:
        print("[WARNING] Missing macro_f1; cannot plot ranking.")
        return

    sorted_df = metrics_df.sort_values(
        by=["macro_f1", "accuracy"],
        ascending=False,
    ).copy()

    names = sorted_df["model_display_name"].tolist()
    values = sorted_df["macro_f1"].astype(float).values

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(names, values)

    ax.set_title("Model Ranking by Macro F1-score")
    ax.set_xlabel("Model")
    ax.set_ylabel("Macro F1-score")
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

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_comparison_summary(metrics_df: pd.DataFrame, best_model_row: pd.Series):
    best_model_display = best_model_row["model_display_name"]
    best_macro_f1 = best_model_row["macro_f1"]
    best_accuracy = best_model_row["accuracy"]

    summary = []
    summary.append("Model Comparison Summary")
    summary.append("=" * 60)
    summary.append("")
    summary.append("Models compared:")

    for _, row in metrics_df.iterrows():
        summary.append(
            f"- {row['model_display_name']}: "
            f"Accuracy = {row['accuracy']:.4f}, "
            f"Macro F1-score = {row['macro_f1']:.4f}"
        )

    summary.append("")
    summary.append("Best model selection:")
    summary.append(
        f"The best-performing model is {best_model_display}, "
        f"with Accuracy = {best_accuracy:.4f} and Macro F1-score = {best_macro_f1:.4f}."
    )
    summary.append("")
    summary.append(
        "Macro F1-score was used as the main model selection criterion because "
        "the project compares performance across positive, neutral and negative sentiment classes. "
        "Macro F1-score treats each class equally and is more suitable than accuracy alone when "
        "the objective is to maintain balanced performance across all sentiment categories."
    )
    summary.append("")
    summary.append(
        "The final deployed model should be selected based on both model performance and deployment suitability. "
        "If two models have similar Macro F1-score, the simpler and more stable model may be preferred for Streamlit deployment."
    )

    return "\n".join(summary)


def main():
    print("=" * 60)
    print("Comparing Model Results")
    print("=" * 60)

    ensure_directories()

    existing_models = get_existing_models()

    if not existing_models:
        raise FileNotFoundError(
            "No model metrics found. Please train at least one model first."
        )

    print("\nModels found:")
    for model in existing_models:
        print(f"- {MODEL_DISPLAY_NAMES.get(model, model)}")

    metrics_records = []

    for model_name in existing_models:
        row = load_metrics_summary(model_name)

        if row is not None:
            metrics_records.append(row)

    if not metrics_records:
        raise ValueError("No valid metrics summary files were loaded.")

    metrics_df = pd.DataFrame(metrics_records)

    preferred_columns = [
        "model_name",
        "model_display_name",
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_precision",
        "weighted_recall",
        "weighted_f1",
        "train_samples",
        "train_samples_total",
        "internal_train_samples",
        "validation_samples",
        "test_samples",
        "epochs_trained",
        "text_column",
        "label_column",
        "pretrained_model",
        "device",
    ]

    existing_columns = [col for col in preferred_columns if col in metrics_df.columns]
    remaining_columns = [col for col in metrics_df.columns if col not in existing_columns]

    metrics_df = metrics_df[existing_columns + remaining_columns].copy()

    for metric in OVERALL_METRICS:
        if metric in metrics_df.columns:
            metrics_df[metric] = pd.to_numeric(metrics_df[metric], errors="coerce")

    metrics_df = metrics_df.sort_values(
        by=["macro_f1", "accuracy"],
        ascending=False,
    ).reset_index(drop=True)

    model_evaluation_path = REPORT_DIR / "model_evaluation_results.csv"
    metrics_df.to_csv(model_evaluation_path, index=False)

    class_report_frames = []

    for model_name in existing_models:
        class_df = load_classification_report(model_name)

        if class_df is not None and not class_df.empty:
            class_report_frames.append(class_df)

    if class_report_frames:
        all_class_reports_df = pd.concat(class_report_frames, ignore_index=True)
    else:
        all_class_reports_df = pd.DataFrame()

    all_class_reports_path = REPORT_DIR / "all_model_classification_reports.csv"
    all_class_reports_df.to_csv(all_class_reports_path, index=False)

    confusion_frames = []

    for model_name in existing_models:
        cm_df = load_confusion_matrix(model_name)

        if cm_df is not None and not cm_df.empty:
            confusion_frames.append(cm_df)

    if confusion_frames:
        all_confusion_df = pd.concat(confusion_frames, ignore_index=True)
    else:
        all_confusion_df = pd.DataFrame()

    all_confusion_path = REPORT_DIR / "all_model_confusion_matrices.csv"
    all_confusion_df.to_csv(all_confusion_path, index=False)

    best_model_row = metrics_df.iloc[0]

    best_model_summary = {
        "best_model_name": best_model_row["model_name"],
        "best_model_display_name": best_model_row["model_display_name"],
        "selection_criterion": "Highest Macro F1-score; Accuracy used as tie-breaker",
        "accuracy": float(best_model_row["accuracy"]),
        "macro_precision": float(best_model_row["macro_precision"]),
        "macro_recall": float(best_model_row["macro_recall"]),
        "macro_f1": float(best_model_row["macro_f1"]),
        "reason": (
            "The final model was selected mainly using Macro F1-score because "
            "the project needs balanced performance across positive, neutral and negative sentiment classes. "
            "Accuracy was used as a secondary criterion."
        ),
    }

    best_model_summary_path = REPORT_DIR / "best_model_summary.json"
    save_json(best_model_summary, best_model_summary_path)

    best_model_summary_csv_path = REPORT_DIR / "best_model_summary.csv"
    pd.DataFrame([best_model_summary]).to_csv(best_model_summary_csv_path, index=False)

    comparison_text = generate_comparison_summary(metrics_df, best_model_row)
    comparison_text_path = REPORT_DIR / "model_comparison_summary.txt"
    save_text(comparison_text, comparison_text_path)

    print("\nGenerating comparison graphs...")

    plot_overall_metrics_comparison(
        metrics_df,
        GRAPH_DIR / "model_comparison_overall_metrics.png",
    )

    plot_accuracy_macro_f1_comparison(
        metrics_df,
        GRAPH_DIR / "model_comparison_accuracy_macro_f1.png",
    )

    plot_macro_f1_ranking(
        metrics_df,
        GRAPH_DIR / "model_ranking_by_macro_f1.png",
    )

    if not all_class_reports_df.empty:
        plot_per_class_f1_comparison(
            all_class_reports_df,
            GRAPH_DIR / "model_comparison_per_class_f1.png",
        )

        plot_per_class_precision_comparison(
            all_class_reports_df,
            GRAPH_DIR / "model_comparison_per_class_precision.png",
        )

        plot_per_class_recall_comparison(
            all_class_reports_df,
            GRAPH_DIR / "model_comparison_per_class_recall.png",
        )
    else:
        print("[WARNING] No classification reports found. Skipping per-class comparison graphs.")

    print("\n" + "=" * 60)
    print("Model Comparison Completed Successfully")
    print("=" * 60)

    print("\nOverall ranking:")
    for index, row in metrics_df.iterrows():
        print(
            f"{index + 1}. {row['model_display_name']} | "
            f"Accuracy: {row['accuracy']:.4f} | "
            f"Macro F1: {row['macro_f1']:.4f}"
        )

    print("\nBest model:")
    print(f"- {best_model_row['model_display_name']}")

    print("\nGenerated report files:")
    print(f"- {model_evaluation_path}")
    print(f"- {all_class_reports_path}")
    print(f"- {all_confusion_path}")
    print(f"- {best_model_summary_path}")
    print(f"- {best_model_summary_csv_path}")
    print(f"- {comparison_text_path}")

    print("\nGenerated graph files:")
    print(f"- {GRAPH_DIR / 'model_comparison_overall_metrics.png'}")
    print(f"- {GRAPH_DIR / 'model_comparison_accuracy_macro_f1.png'}")
    print(f"- {GRAPH_DIR / 'model_ranking_by_macro_f1.png'}")
    print(f"- {GRAPH_DIR / 'model_comparison_per_class_f1.png'}")
    print(f"- {GRAPH_DIR / 'model_comparison_per_class_precision.png'}")
    print(f"- {GRAPH_DIR / 'model_comparison_per_class_recall.png'}")


if __name__ == "__main__":
    main()