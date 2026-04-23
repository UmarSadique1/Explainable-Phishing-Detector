from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import io
import base64

import joblib
import numpy as np
import pandas as pd
import shap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lime.lime_text import LimeTextExplainer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.feature_extraction.text import CountVectorizer


MODEL_PATH = Path("models/baseline_lr.joblib")
DATA_PATH = Path("data/email_dataset/processed/emails.csv")

_model = None


@dataclass
class PredictionResult:
    label: str
    phishing_proba: float

    lime_weights: List[Tuple[str, float]]
    lime_percent_weights: List[Tuple[str, float, float, str]]
    highlighted_html: str
    lime_readable: str

    shap_weights: List[Tuple[str, float]]
    shap_percent_weights: List[Tuple[str, float, float, str]]
    shap_plot_base64: str
    shap_readable: str


def load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run: python3 scripts/train_baseline.py"
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def _normalise_weights_to_percent(weights: List[Tuple[str, float]]) -> List[Tuple[str, float, float, str]]:
    if not weights:
        return []

    total_abs = sum(abs(weight) for _, weight in weights)
    if total_abs == 0:
        return [(token, weight, 0.0, "neutral") for token, weight in weights]

    output = []
    for token, weight in weights:
        percent = (abs(weight) / total_abs) * 100
        direction = "phishing" if weight > 0 else "legitimate"
        output.append((token, weight, percent, direction))

    return output


def _lime_explain(text: str, num_features: int = 10):
    model = load_model()

    explainer = LimeTextExplainer(class_names=["legitimate", "phishing"])
    exp = explainer.explain_instance(
        text,
        model.predict_proba,
        num_features=num_features
    )

    weights = exp.as_list(label=1)
    weights = sorted(weights, key=lambda x: abs(x[1]), reverse=True)

    token_weights = {token.lower(): weight for token, weight in weights}

    def colour_for(weight: float) -> str:
        return "#e7b08a" if weight > 0 else "#a7d6a4"

    parts = []
    for raw_word in text.split():
        cleaned = raw_word.strip(".,!?;:()[]{}\"'").lower()
        if cleaned in token_weights:
            weight = token_weights[cleaned]
            parts.append(
                f"<span style='background:{colour_for(weight)}; padding:2px 4px; border-radius:6px'>{raw_word}</span>"
            )
        else:
            parts.append(raw_word)

    highlighted_html = " ".join(parts)

    top = weights[:4]
    top_tokens = [token for token, _ in top]

    if not top_tokens:
        lime_readable = "No strong LIME indicators were detected for this email."
    elif len(top_tokens) == 1:
        lime_readable = f"This email was mainly influenced by the term '{top_tokens[0]}'."
    else:
        lime_readable = (
            f"The strongest local indicators in this email were "
            f"{', '.join(top_tokens[:-1])} and {top_tokens[-1]}."
        )

    return weights, highlighted_html, lime_readable


def _shap_explain(text: str, num_features: int = 10):
    model = load_model()

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["clf"]

    X = vectorizer.transform([text])

    background_texts = [
        "normal meeting update attached thanks",
        "please review the project document",
        "verify your account immediately",
        "security alert confirm your login details",
    ]
    background = vectorizer.transform(background_texts)

    explainer = shap.LinearExplainer(classifier, background)
    shap_values = explainer(X)

    feature_names = vectorizer.get_feature_names_out()
    values = shap_values.values[0]

    non_zero_idx = X.nonzero()[1]
    pairs = [(feature_names[i], values[i]) for i in non_zero_idx]
    pairs = sorted(pairs, key=lambda x: abs(x[1]), reverse=True)[:num_features]

    if not pairs:
        return [], "", "No strong SHAP signals were detected for this email."

    tokens = [token for token, _ in pairs]
    vals = [value for _, value in pairs]
    colors = ["#e7b08a" if value > 0 else "#a7d6a4" for value in vals]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(tokens[::-1], vals[::-1], color=colors[::-1])
    ax.set_xlabel("Contribution to prediction")
    ax.set_title("SHAP Feature Contributions")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode("utf-8")

    top_tokens = [token for token, _ in pairs[:4]]
    if len(top_tokens) == 1:
        shap_readable = f"SHAP shows that '{top_tokens[0]}' had the strongest influence on this prediction."
    else:
        shap_readable = (
            f"SHAP shows that {', '.join(top_tokens[:-1])} and {top_tokens[-1]} "
            f"had the strongest influence on this prediction."
        )

    return pairs, plot_base64, shap_readable


def predict_with_lime(text: str) -> PredictionResult:
    """
    Single-source prediction:
    - raw ML probability only
    - LIME explains the same model
    - SHAP explains the same model
    - final category bands come from the same raw probability
    """
    model = load_model()

    proba = float(model.predict_proba([text])[0][1])

    if proba >= 0.60:
        label = "Phishing"
    elif proba >= 0.31:
        label = "Suspicious"
    else:
        label = "Likely Legitimate"

    lime_weights, highlighted_html, lime_readable = _lime_explain(text)
    shap_weights, shap_plot_base64, shap_readable = _shap_explain(text)

    lime_percent_weights = _normalise_weights_to_percent(lime_weights)
    shap_percent_weights = _normalise_weights_to_percent(shap_weights)

    return PredictionResult(
        label=label,
        phishing_proba=proba,
        lime_weights=lime_weights,
        lime_percent_weights=lime_percent_weights,
        highlighted_html=highlighted_html,
        lime_readable=lime_readable,
        shap_weights=shap_weights,
        shap_percent_weights=shap_percent_weights,
        shap_plot_base64=shap_plot_base64,
        shap_readable=shap_readable,
    )


def get_model_performance_metrics():
    model = load_model()

    if not DATA_PATH.exists():
        return {}

    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.2,
        random_state=42,
        stratify=df["label"],
    )

    y_proba = model.predict_proba(X_test)[:, 1]

    y_pred = np.where(y_proba >= 0.31, 1, 0)

    try:
        roc_auc = roc_auc_score(y_test, y_proba)
    except Exception:
        roc_auc = None

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc,
    }


def get_top_phishing_terms(top_n: int = 10):
    if not DATA_PATH.exists():
        return []

    df = pd.read_csv(DATA_PATH)

    if "text" not in df.columns or "label" not in df.columns:
        return []

    phishing_df = df[df["label"] == 1].copy()
    phishing_df = phishing_df.dropna(subset=["text"])

    if phishing_df.empty:
        return []

    vectorizer = CountVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=300
    )

    X = vectorizer.fit_transform(phishing_df["text"].astype(str))
    counts = np.asarray(X.sum(axis=0)).ravel()
    terms = vectorizer.get_feature_names_out()

    pairs = sorted(zip(terms, counts), key=lambda x: x[1], reverse=True)[:top_n]

    results = []
    for rank, (term, count) in enumerate(pairs, start=1):
        term_type = "Phrase" if " " in term else "Word"

        if any(word in term.lower() for word in ["verify", "account", "login", "bank", "security", "confirm"]):
            explanation = "This language often appears in credential theft or impersonation emails."
        elif any(word in term.lower() for word in ["click", "link", "http", "www"]):
            explanation = "These terms often direct users towards suspicious or malicious links."
        elif any(word in term.lower() for word in ["urgent", "immediately", "alert", "suspended"]):
            explanation = "Urgency language is often used to pressure users into acting without thinking."
        else:
            explanation = "This term appears frequently in phishing-labelled emails in the training data."

        results.append({
            "rank": rank,
            "term": term,
            "count": int(count),
            "type": term_type,
            "explanation": explanation,
        })

    return results


    