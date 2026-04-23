import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


DATA_PATH = "data/email_dataset/processed/emails.csv"
MODEL_PATH = "models/baseline_lr.joblib"


def load_dataset(path: str) -> pd.DataFrame:
    """
    Expects a CSV with columns:
      - text: email content
      - label: 0 (legitimate) or 1 (phishing/spam)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            f"Make sure you have run: python3 scripts/prepare_email_dataset.py"
        )

    df = pd.read_csv(path)

    required = {"text", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns {required}. Found: {set(df.columns)}")

    df = df.dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)

    bad_labels = set(df["label"].unique()) - {0, 1}
    if bad_labels:
        raise ValueError(f"Labels must be 0/1 only. Found unexpected: {bad_labels}")

    return df


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def train_and_save(data_path: str = DATA_PATH, model_path: str = MODEL_PATH) -> None:
    df = load_dataset(data_path)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.2,
        random_state=42,
        stratify=df["label"],
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    print(f"\nDataset: {data_path}")
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
    print("Label balance (train):", y_train.value_counts().to_dict())
    print("Label balance (test): ", y_test.value_counts().to_dict())

    print("\nConfusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nReport:\n", classification_report(y_test, y_pred, digits=3))

    try:
        auc = roc_auc_score(y_test, y_proba)
        print(f"ROC-AUC: {auc:.4f}")
    except Exception:
        pass

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\nSaved model to: {model_path}")


if __name__ == "__main__":
    train_and_save()