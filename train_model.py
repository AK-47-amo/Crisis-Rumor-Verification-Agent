import logging
import sys

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

import joblib

from config import DATA_DIR, MODEL_DIR, MODEL_PATH, TRAINING_DATA_PATH
from utils import clean_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
)
logger = logging.getLogger(__name__)


def load_data() -> pd.DataFrame:
    if not TRAINING_DATA_PATH.exists():
        logger.error(
            "Training data not found at: %s\n"
            "Please download 'train.csv' from:\n"
            "  https://www.kaggle.com/c/nlp-getting-started/data\n"
            "and place it in the data/ directory.",
            TRAINING_DATA_PATH,
        )
        sys.exit(1)

    df = pd.read_csv(TRAINING_DATA_PATH)
    logger.info("Loaded %d rows from %s", len(df), TRAINING_DATA_PATH)

    required_cols = {"text", "target"}
    if not required_cols.issubset(df.columns):
        logger.error("Dataset must contain columns: %s", required_cols)
        sys.exit(1)

    # Drop rows with missing text
    df = df.dropna(subset=["text"])
    logger.info("After dropping NaN text: %d rows", len(df))

    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["clean_text"] = df["text"].apply(clean_text)
    return df


def train() -> None:
    logger.info("=" * 60)
    logger.info("  Crisis Rumor Verification — Model Training")
    logger.info("=" * 60)

    # ── 1. Load data ────────────────────────────────────────────────
    df = load_data()
    df = preprocess(df)

    # ── 2. Split ────────────────────────────────────────────────────
    X = df["clean_text"]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )
    logger.info("Train size: %d | Test size: %d", len(X_train), len(X_test))

    # ── 3. Build pipeline ──────────────────────────────────────────
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                max_features=10_000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                C=1.0,
                solver="lbfgs",
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    # ── 4. Train ───────────────────────────────────────────────────
    logger.info("Training TF-IDF + Logistic Regression pipeline...")
    pipeline.fit(X_train, y_train)
    logger.info("Training complete.")

    # ── 5. Evaluate ────────────────────────────────────────────────
    y_pred = pipeline.predict(X_test)
    report = classification_report(
        y_test, y_pred,
        target_names=["Non-Crisis (0)", "Real Crisis (1)"],
    )
    logger.info("\n📊 Classification Report:\n%s", report)

    # ── 6. Save ────────────────────────────────────────────────────
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info("✅ Model saved to: %s", MODEL_PATH)

    # ── 7. Quick sanity check ──────────────────────────────────────
    test_messages = [
        "Massive earthquake hits Turkey, thousands feared dead",
        "Just had a great lunch at the new restaurant downtown",
        "BREAKING: Forest fire engulfs northern California, evacuations ordered",
    ]
    logger.info("\n🧪 Sanity Check:")
    for msg in test_messages:
        cleaned = clean_text(msg)
        pred = pipeline.predict([cleaned])[0]
        prob = pipeline.predict_proba([cleaned])[0]
        label = "Real Crisis" if pred == 1 else "Non-Crisis"
        logger.info("  [%s] (%.1f%%) → %s", label, max(prob) * 100, msg[:70])


if __name__ == "__main__":
    train()
