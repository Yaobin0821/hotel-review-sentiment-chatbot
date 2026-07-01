import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

HF_MODEL_ID = "qm0720/staywise-kl-distilbert-sentiment"

LABEL_ORDER = ["negative", "neutral", "positive"]

tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL_ID)
model.eval()

text = "The room was clean and the staff were friendly."

inputs = tokenizer(
    text,
    return_tensors="pt",
    truncation=True,
    padding=True,
    max_length=128,
)

with torch.no_grad():
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1).squeeze().tolist()

predicted_id = int(torch.argmax(outputs.logits, dim=1).item())

print("Text:", text)
print("Predicted sentiment:", LABEL_ORDER[predicted_id])
print("Confidence:", probs[predicted_id])
print("Probabilities:", {
    "negative": probs[0],
    "neutral": probs[1],
    "positive": probs[2],
})