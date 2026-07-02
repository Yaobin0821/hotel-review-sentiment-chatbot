# scripts/train_distilbert.py

from pathlib import Path
import os
import json
import random
import copy
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize


# =========================
# Configuration
# =========================
MODEL_NAME = "distilbert"

BASE_DIR = Path(__file__).resolve().parents[1]

TRAIN_PATH = BASE_DIR / "data" / "train_dataset.csv"
TEST_PATH = BASE_DIR / "data" / "test_dataset.csv"

MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"
GRAPH_DIR = BASE_DIR / "graphs"

TEXT_COLUMN = "BERT_Text"
LABEL_COLUMN = "Sentiment"

LABEL_ORDER = ["negative", "neutral", "positive"]

SENTIMENT_TO_ID = {
    "negative": 0,
    "neutral": 1,
    "positive": 2,
}

ID_TO_SENTIMENT = {
    0: "negative",
    1: "neutral",
    2: "positive",
}

NUM_CLASSES = 3

PRETRAINED_MODEL_NAME = "distilbert-base-uncased"

RANDOM_STATE = 42

# DistilBERT hyperparameters
MAX_LENGTH = 256
BATCH_SIZE = 16
EPOCHS = 10
VALIDATION_SIZE = 0.2
LEARNING_RATE = 2e-5
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.1
PATIENCE = 3
MAX_GRAD_NORM = 1.0


# =========================
# Reproducibility
# =========================
def set_seed(seed: int = 42):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# =========================
# Utility Functions
# =========================
def ensure_directories():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_dataset(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

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

    df["Label_ID_Final"] = df[LABEL_COLUMN].map(SENTIMENT_TO_ID)

    return df


def save_text_report(text: str, file_path: Path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def save_json(data: dict, file_path: Path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =========================
# Dataset Class
# =========================
class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        text = str(self.texts[index])
        label = int(self.labels[index])

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long),
        }


# =========================
# Plot Functions
# =========================
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
        title="DistilBERT - Confusion Matrix",
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

    ax.set_title("DistilBERT - Per-Class Metrics")
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

    ax.set_title("DistilBERT - Overall Metrics")
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


def plot_multiclass_roc(y_true_id, y_prob, save_path: Path):
    y_true_bin = label_binarize(y_true_id, classes=[0, 1, 2])

    fig, ax = plt.subplots(figsize=(8, 6))

    for i, label in enumerate(LABEL_ORDER):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, lw=2, label=f"{label} (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("DistilBERT - ROC Curve (One-vs-Rest)")
    ax.legend(loc="lower right")

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_training_accuracy(history_df: pd.DataFrame, save_path: Path):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(history_df["epoch"], history_df["train_accuracy"], label="Training Accuracy")
    ax.plot(history_df["epoch"], history_df["val_accuracy"], label="Validation Accuracy")

    ax.set_title("DistilBERT - Training and Validation Accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_training_loss(history_df: pd.DataFrame, save_path: Path):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(history_df["epoch"], history_df["train_loss"], label="Training Loss")
    ax.plot(history_df["epoch"], history_df["val_loss"], label="Validation Loss")

    ax.set_title("DistilBERT - Training and Validation Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


# =========================
# Training / Evaluation Helpers
# =========================
def train_one_epoch(model, data_loader, optimizer, scheduler, device):
    model.train()

    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    for batch in data_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )

        loss = outputs.loss
        logits = outputs.logits

        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)

        optimizer.step()
        scheduler.step()

        preds = torch.argmax(logits, dim=1)

        total_loss += loss.item() * input_ids.size(0)
        correct_predictions += torch.sum(preds == labels).item()
        total_samples += input_ids.size(0)

    avg_loss = total_loss / total_samples
    accuracy = correct_predictions / total_samples

    return avg_loss, accuracy


def evaluate_model(model, data_loader, device):
    model.eval()

    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    all_labels = []
    all_probs = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )

            loss = outputs.loss
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)

            total_loss += loss.item() * input_ids.size(0)
            correct_predictions += torch.sum(preds == labels).item()
            total_samples += input_ids.size(0)

            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    avg_loss = total_loss / total_samples
    accuracy = correct_predictions / total_samples

    return avg_loss, accuracy, np.array(all_labels), np.array(all_probs)


# =========================
# Main Training Function
# =========================
def main():
    print("=" * 60)
    print("Training DistilBERT Model")
    print("=" * 60)

    set_seed(RANDOM_STATE)
    ensure_directories()

    device = get_device()
    print(f"Using device: {device}")

    # Load data
    train_df = load_dataset(TRAIN_PATH)
    test_df = load_dataset(TEST_PATH)

    print(f"Train dataset shape: {train_df.shape}")
    print(f"Test dataset shape: {test_df.shape}")

    print("\nTrain label distribution:")
    print(train_df[LABEL_COLUMN].value_counts())

    print("\nTest label distribution:")
    print(test_df[LABEL_COLUMN].value_counts())

    X_full_train = train_df[TEXT_COLUMN].values
    y_full_train = train_df["Label_ID_Final"].values

    X_test_text = test_df[TEXT_COLUMN].values
    y_test_id = test_df["Label_ID_Final"].values

    # Train-validation split from training set only
    X_train_text, X_val_text, y_train_id, y_val_id = train_test_split(
        X_full_train,
        y_full_train,
        test_size=VALIDATION_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_full_train,
    )

    print("\nInternal train-validation split:")
    print(f"Training samples: {len(X_train_text)}")
    print(f"Validation samples: {len(X_val_text)}")
    print(f"Testing samples: {len(X_test_text)}")

    # Load tokenizer and model
    print(f"\nLoading tokenizer and model: {PRETRAINED_MODEL_NAME}")

    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)

    model = AutoModelForSequenceClassification.from_pretrained(
        PRETRAINED_MODEL_NAME,
        num_labels=NUM_CLASSES,
        id2label=ID_TO_SENTIMENT,
        label2id=SENTIMENT_TO_ID,
    )

    model.to(device)

    # Create datasets
    train_dataset = SentimentDataset(
        X_train_text,
        y_train_id,
        tokenizer,
        MAX_LENGTH,
    )

    val_dataset = SentimentDataset(
        X_val_text,
        y_val_id,
        tokenizer,
        MAX_LENGTH,
    )

    test_dataset = SentimentDataset(
        X_test_text,
        y_test_id,
        tokenizer,
        MAX_LENGTH,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    # Optimizer and scheduler
    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    total_training_steps = len(train_loader) * EPOCHS
    warmup_steps = int(total_training_steps * WARMUP_RATIO)

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_training_steps,
    )

    print("\nTraining configuration:")
    print(f"Max length: {MAX_LENGTH}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Warmup steps: {warmup_steps}")
    print(f"Total training steps: {total_training_steps}")

    # Training loop
    history = []
    best_val_loss = float("inf")
    best_model_state = None
    patience_counter = 0

    print("\nTraining model...")

    for epoch in range(1, EPOCHS + 1):
        print("\n" + "-" * 60)
        print(f"Epoch {epoch}/{EPOCHS}")
        print("-" * 60)

        train_loss, train_accuracy = train_one_epoch(
            model,
            train_loader,
            optimizer,
            scheduler,
            device,
        )

        val_loss, val_accuracy, _, _ = evaluate_model(
            model,
            val_loader,
            device,
        )

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "train_accuracy": train_accuracy,
                "val_loss": val_loss,
                "val_accuracy": val_accuracy,
            }
        )

        print(f"Train Loss: {train_loss:.4f}")
        print(f"Train Accuracy: {train_accuracy:.4f}")
        print(f"Validation Loss: {val_loss:.4f}")
        print(f"Validation Accuracy: {val_accuracy:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = copy.deepcopy(model.state_dict())
            patience_counter = 0
            print("Best model updated.")
        else:
            patience_counter += 1
            print(f"No improvement. Patience: {patience_counter}/{PATIENCE}")

        if patience_counter >= PATIENCE:
            print("Early stopping triggered.")
            break

    # Load best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        model.to(device)

    # Evaluate on test set
    print("\nEvaluating best model on test set...")

    test_loss, test_accuracy_internal, y_true_id, y_prob = evaluate_model(
        model,
        test_loader,
        device,
    )

    y_pred_id = np.argmax(y_prob, axis=1)# Neutral threshold adjustment
    NEUTRAL_ID = 1
    NEUTRAL_THRESHOLD = 0.45

    y_pred_id = []

    for prob in y_prob:
            pred = int(np.argmax(prob))

            if pred == NEUTRAL_ID and prob[NEUTRAL_ID] < NEUTRAL_THRESHOLD:
                prob_without_neutral = prob.copy()
                prob_without_neutral[NEUTRAL_ID] = -1
                pred = int(np.argmax(prob_without_neutral))

            y_pred_id.append(pred)

    y_pred_id = np.array(y_pred_id)

    y_test_label = [ID_TO_SENTIMENT[int(i)] for i in y_true_id]
    y_pred_label = [ID_TO_SENTIMENT[int(i)] for i in y_pred_id]

    accuracy = accuracy_score(y_test_label, y_pred_label)

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_test_label,
        y_pred_label,
        average="macro",
        zero_division=0,
    )

    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_test_label,
        y_pred_label,
        average="weighted",
        zero_division=0,
    )

    report_dict = classification_report(
        y_test_label,
        y_pred_label,
        labels=LABEL_ORDER,
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        y_test_label,
        y_pred_label,
        labels=LABEL_ORDER,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_test_label,
        y_pred_label,
        labels=LABEL_ORDER,
    )

    history_df = pd.DataFrame(history)

    # Save model and tokenizer
    model_save_path = MODEL_DIR / f"{MODEL_NAME}_model"
    label_mapping_path = MODEL_DIR / f"{MODEL_NAME}_label_mapping.json"

    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)

    save_json(
        {
            "sentiment_to_id": SENTIMENT_TO_ID,
            "id_to_sentiment": ID_TO_SENTIMENT,
            "label_order": LABEL_ORDER,
        },
        label_mapping_path,
    )

    # Save metrics summary
    metrics_summary = {
        "model_name": MODEL_NAME,
        "pretrained_model": PRETRAINED_MODEL_NAME,
        "text_column": TEXT_COLUMN,
        "label_column": LABEL_COLUMN,
        "train_samples_total": int(len(train_df)),
        "internal_train_samples": int(len(X_train_text)),
        "validation_samples": int(len(X_val_text)),
        "test_samples": int(len(test_df)),
        "test_loss": float(test_loss),
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_precision),
        "weighted_recall": float(weighted_recall),
        "weighted_f1": float(weighted_f1),
        "epochs_trained": int(len(history_df)),
        "best_val_loss": float(best_val_loss),
        "device": str(device),
    }

    metrics_df = pd.DataFrame([metrics_summary])
    metrics_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_metrics_summary.csv", index=False)

    # Save classification report
    report_df = pd.DataFrame(report_dict).transpose()
    report_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_classification_report.csv", index=True)

    save_text_report(
        report_text,
        REPORT_DIR / f"{MODEL_NAME}_classification_report.txt",
    )

    # Save confusion matrix
    cm_df = pd.DataFrame(cm, index=LABEL_ORDER, columns=LABEL_ORDER)
    cm_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_confusion_matrix.csv")

    # Save predictions
    predictions_df = pd.DataFrame(
        {
            "Text": X_test_text,
            "Actual_Label": y_test_label,
            "Predicted_Label": y_pred_label,
            "Correct": np.array(y_test_label) == np.array(y_pred_label),
            "Confidence": y_prob.max(axis=1),
            "Prob_Negative": y_prob[:, 0],
            "Prob_Neutral": y_prob[:, 1],
            "Prob_Positive": y_prob[:, 2],
        }
    )

    predictions_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_test_predictions.csv",
        index=False,
    )

    # Save misclassified samples
    misclassified_df = predictions_df[predictions_df["Correct"] == False].copy()
    misclassified_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_misclassified_samples.csv",
        index=False,
    )

    # Save training history
    history_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_training_history.csv",
        index=False,
    )

    # Save model config
    save_json(
        {
            "model_name": MODEL_NAME,
            "algorithm": "DistilBERT Transformer Model",
            "pretrained_model": PRETRAINED_MODEL_NAME,
            "train_file": str(TRAIN_PATH),
            "test_file": str(TEST_PATH),
            "text_column": TEXT_COLUMN,
            "label_column": LABEL_COLUMN,
            "label_order": LABEL_ORDER,
            "sentiment_to_id": SENTIMENT_TO_ID,
            "max_length": MAX_LENGTH,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "validation_size": VALIDATION_SIZE,
            "learning_rate": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "warmup_ratio": WARMUP_RATIO,
            "patience": PATIENCE,
            "max_grad_norm": MAX_GRAD_NORM,
            "random_state": RANDOM_STATE,
            "device": str(device),
        },
        REPORT_DIR / f"{MODEL_NAME}_config.json",
    )

    # Generate graphs
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
        y_true_id,
        y_prob,
        GRAPH_DIR / f"{MODEL_NAME}_roc_curve.png",
    )

    plot_training_accuracy(
        history_df,
        GRAPH_DIR / f"{MODEL_NAME}_training_accuracy.png",
    )

    plot_training_loss(
        history_df,
        GRAPH_DIR / f"{MODEL_NAME}_training_loss.png",
    )

    # Print summary
    print("\n" + "=" * 60)
    print("DistilBERT Training Completed Successfully")
    print("=" * 60)

    print(f"Model and tokenizer saved to: {model_save_path}")
    print(f"Label mapping saved to: {label_mapping_path}")

    print("\nEvaluation Results:")
    print(f"Test Loss:         {test_loss:.4f}")
    print(f"Accuracy:          {accuracy:.4f}")
    print(f"Macro Precision:   {macro_precision:.4f}")
    print(f"Macro Recall:      {macro_recall:.4f}")
    print(f"Macro F1-score:    {macro_f1:.4f}")

    print("\nGenerated report files:")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_metrics_summary.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_classification_report.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_classification_report.txt'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_confusion_matrix.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_test_predictions.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_misclassified_samples.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_training_history.csv'}")
    print(f"- {REPORT_DIR / f'{MODEL_NAME}_config.json'}")

    print("\nGenerated graph files:")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_confusion_matrix.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_per_class_metrics.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_overall_metrics.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_roc_curve.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_training_accuracy.png'}")
    print(f"- {GRAPH_DIR / f'{MODEL_NAME}_training_loss.png'}")


if __name__ == "__main__":
    main()