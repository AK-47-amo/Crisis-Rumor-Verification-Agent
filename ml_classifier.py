import logging
from pathlib import Path

import joblib

from config import MODEL_PATH
from models import MLPrediction
from utils import clean_text

logger = logging.getLogger(__name__)


class DisasterClassifier:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self) -> None:
        """Load the trained model from disk."""
        if not self.model_path.exists():
            logger.warning(
                "Model file not found at %s. "
                "Run train_model.py first to train the classifier.",
                self.model_path,
            )
            return

        try:
            self.model = joblib.load(self.model_path)
            logger.info("Model loaded successfully from %s", self.model_path)
        except Exception as e:
            logger.error("Failed to load model: %s", e)
            self.model = None

    def predict(self, message: str) -> MLPrediction:
        if self.model is None:
            logger.warning("No model loaded. Returning default prediction.")
            return MLPrediction(
                label="Likely Non-Crisis",
                confidence=0.5,
                model_used="No model available",
            )

        try:
            cleaned = clean_text(message)
            # predict_proba returns [[prob_class_0, prob_class_1]]
            probabilities = self.model.predict_proba([cleaned])[0]
            predicted_class = self.model.predict([cleaned])[0]

            # Class 1 = disaster (real crisis), Class 0 = non-disaster
            confidence = float(max(probabilities))
            label = (
                "Likely Real Crisis" if predicted_class == 1
                else "Likely Non-Crisis"
            )

            return MLPrediction(
                label=label,
                confidence=confidence,
                model_used="TF-IDF + Logistic Regression",
            )

        except Exception as e:
            logger.error("Prediction failed: %s", e)
            return MLPrediction(
                label="Likely Non-Crisis",
                confidence=0.5,
                model_used=f"Error: {e}",
            )
