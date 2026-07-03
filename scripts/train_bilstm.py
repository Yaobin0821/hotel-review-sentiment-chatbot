
from pathlib import Path
import os
import json
import random
import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Embedding,
    Bidirectional,
    LSTM,
    Dense,
    Dropout,
    SpatialDropout1D,
    GlobalMaxPooling1D,
)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


MODEL_NAME = "bilstm"

BASE_DIR = Path(__file__).resolve().parents[1]

TRAIN_PATH = BASE_DIR / "data" / "train_dataset.csv"
TEST_PATH = BASE_DIR / "data" / "test_dataset.csv"

MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"
GRAPH_DIR = BASE_DIR / "graphs"

TEXT_COLUMN = "Cleaned_Text"
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

RANDOM_STATE = 42

MAX_WORDS = 10000
MAX_SEQUENCE_LENGTH = 80
EMBEDDING_DIM = 100
LSTM_UNITS = 64
DENSE_UNITS = 64
DROPOUT_RATE = 0.3
SPATIAL_DROPOUT_RATE = 0.2

BATCH_SIZE = 16
EPOCHS = 35
VALIDATION_SIZE = 0.2
LEARNING_RATE = 0.001

def set_seed(seed: int = 42):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)

def ensure_directories():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)


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
        title="BiLSTM - Confusion Matrix",
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

    ax.set_title("BiLSTM - Per-Class Metrics")
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

    ax.set_title("BiLSTM - Overall Metrics")
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
    ax.set_title("BiLSTM - ROC Curve (One-vs-Rest)")
    ax.legend(loc="lower right")

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_training_accuracy(history, save_path: Path):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(history.history["accuracy"], label="Training Accuracy")
    ax.plot(history.history["val_accuracy"], label="Validation Accuracy")

    ax.set_title("BiLSTM - Training and Validation Accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_training_loss(history, save_path: Path):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(history.history["loss"], label="Training Loss")
    ax.plot(history.history["val_loss"], label="Validation Loss")

    ax.set_title("BiLSTM - Training and Validation Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def build_bilstm_model(vocab_size: int):
    model = Sequential(
        [
            Embedding(
                input_dim=vocab_size,
                output_dim=EMBEDDING_DIM,
                input_length=MAX_SEQUENCE_LENGTH,
                name="embedding_layer",
            ),
            SpatialDropout1D(SPATIAL_DROPOUT_RATE),
            Bidirectional(
                LSTM(
                    LSTM_UNITS,
                    return_sequences=True,
                    dropout=0.2,
                    recurrent_dropout=0.0,
                ),
                name="bidirectional_lstm",
            ),
            GlobalMaxPooling1D(),
            Dense(DENSE_UNITS, activation="relu"),
            Dropout(DROPOUT_RATE),
            Dense(NUM_CLASSES, activation="softmax", name="sentiment_output"),
        ]
    )

    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def main():
    print("=" * 60)
    print("Training BiLSTM Model")
    print("=" * 60)

    set_seed(RANDOM_STATE)
    ensure_directories()

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

    print("\nFitting tokenizer...")
    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(X_train_text)

    X_train_seq = tokenizer.texts_to_sequences(X_train_text)
    X_val_seq = tokenizer.texts_to_sequences(X_val_text)
    X_test_seq = tokenizer.texts_to_sequences(X_test_text)

    X_train_pad = pad_sequences(
        X_train_seq,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post",
    )

    X_val_pad = pad_sequences(
        X_val_seq,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post",
    )

    X_test_pad = pad_sequences(
        X_test_seq,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post",
    )

    y_train_cat = to_categorical(y_train_id, num_classes=NUM_CLASSES)
    y_val_cat = to_categorical(y_val_id, num_classes=NUM_CLASSES)

    vocab_size = min(MAX_WORDS, len(tokenizer.word_index) + 1)

    print(f"Vocabulary size used: {vocab_size}")
    print(f"Maximum sequence length: {MAX_SEQUENCE_LENGTH}")

    model = build_bilstm_model(vocab_size)

    print("\nModel summary:")
    model.summary()

    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=6,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-5,
            verbose=1,
        ),
    ]

    print("\nTraining model...")
    history = model.fit(
        X_train_pad,
        y_train_cat,
        validation_data=(X_val_pad, y_val_cat),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    print("\nEvaluating model...")
    y_prob = model.predict(X_test_pad)
    y_pred_id = np.argmax(y_prob, axis=1)

    y_test_label = [ID_TO_SENTIMENT[int(i)] for i in y_test_id]
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

    model_path = MODEL_DIR / f"{MODEL_NAME}_model.keras"
    tokenizer_path = MODEL_DIR / f"{MODEL_NAME}_tokenizer.pkl"
    label_mapping_path = MODEL_DIR / f"{MODEL_NAME}_label_mapping.json"

    model.save(model_path)
    joblib.dump(tokenizer, tokenizer_path)

    save_json(
        {
            "sentiment_to_id": SENTIMENT_TO_ID,
            "id_to_sentiment": ID_TO_SENTIMENT,
            "label_order": LABEL_ORDER,
        },
        label_mapping_path,
    )

    metrics_summary = {
        "model_name": MODEL_NAME,
        "text_column": TEXT_COLUMN,
        "label_column": LABEL_COLUMN,
        "train_samples_total": int(len(train_df)),
        "internal_train_samples": int(len(X_train_text)),
        "validation_samples": int(len(X_val_text)),
        "test_samples": int(len(test_df)),
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_precision),
        "weighted_recall": float(weighted_recall),
        "weighted_f1": float(weighted_f1),
        "epochs_trained": int(len(history.history["loss"])),
    }

    metrics_df = pd.DataFrame([metrics_summary])
    metrics_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_metrics_summary.csv", index=False)

    report_df = pd.DataFrame(report_dict).transpose()
    report_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_classification_report.csv", index=True)

    save_text_report(
        report_text,
        REPORT_DIR / f"{MODEL_NAME}_classification_report.txt",
    )

    cm_df = pd.DataFrame(cm, index=LABEL_ORDER, columns=LABEL_ORDER)
    cm_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_confusion_matrix.csv")

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

    misclassified_df = predictions_df[predictions_df["Correct"] == False].copy()
    misclassified_df.to_csv(
        REPORT_DIR / f"{MODEL_NAME}_misclassified_samples.csv",
        index=False,
    )

    history_df = pd.DataFrame(history.history)
    history_df.to_csv(REPORT_DIR / f"{MODEL_NAME}_training_history.csv", index=False)

    save_json(
        {
            "model_name": MODEL_NAME,
            "algorithm": "Embedding + Bidirectional LSTM",
            "train_file": str(TRAIN_PATH),
            "test_file": str(TEST_PATH),
            "text_column": TEXT_COLUMN,
            "label_column": LABEL_COLUMN,
            "label_order": LABEL_ORDER,
            "sentiment_to_id": SENTIMENT_TO_ID,
            "max_words": MAX_WORDS,
            "max_sequence_length": MAX_SEQUENCE_LENGTH,
            "embedding_dim": EMBEDDING_DIM,
            "lstm_units": LSTM_UNITS,
            "dense_units": DENSE_UNITS,
            "dropout_rate": DROPOUT_RATE,
            "spatial_dropout_rate": SPATIAL_DROPOUT_RATE,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "validation_size": VALIDATION_SIZE,
            "learning_rate": LEARNING_RATE,
            "random_state": RANDOM_STATE,
            "early_stopping": {
                "monitor": "val_loss",
                "patience": 6,
                "restore_best_weights": True,
            },
            "reduce_lr_on_plateau": {
                "monitor": "val_loss",
                "factor": 0.5,
                "patience": 3,
                "min_lr": 1e-5,
            },
        },
        REPORT_DIR / f"{MODEL_NAME}_config.json",
    )

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
        y_test_id,
        y_prob,
        GRAPH_DIR / f"{MODEL_NAME}_roc_curve.png",
    )

    plot_training_accuracy(
        history,
        GRAPH_DIR / f"{MODEL_NAME}_training_accuracy.png",
    )

    plot_training_loss(
        history,
        GRAPH_DIR / f"{MODEL_NAME}_training_loss.png",
    )

    print("\n" + "=" * 60)
    print("BiLSTM Training Completed Successfully")
    print("=" * 60)
    print(f"Model saved to: {model_path}")
    print(f"Tokenizer saved to: {tokenizer_path}")
    print(f"Label mapping saved to: {label_mapping_path}")

    print("\nEvaluation Results:")
    print(f"Accuracy:         {accuracy:.4f}")
    print(f"Macro Precision:  {macro_precision:.4f}")
    print(f"Macro Recall:     {macro_recall:.4f}")
    print(f"Macro F1-score:   {macro_f1:.4f}")

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