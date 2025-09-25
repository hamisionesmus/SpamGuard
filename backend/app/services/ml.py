"""
Machine Learning service for spam/fraud detection
"""

import os
import pickle
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sqlalchemy.ext.asyncio import AsyncSession
import joblib

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)


class MLService:
    """Machine Learning service for text classification"""

    def __init__(self):
        self.models_dir = Path(settings.MODEL_PATH)
        self.models_dir.mkdir(exist_ok=True)
        self.vectorizer = None
        self.model = None
        self._load_latest_model()

    def _load_latest_model(self):
        """Load the latest trained model"""
        try:
            model_files = list(self.models_dir.glob("*.pkl"))
            if model_files:
                latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
                with open(latest_model, 'rb') as f:
                    model_data = pickle.load(f)
                    self.vectorizer = model_data['vectorizer']
                    self.model = model_data['model']
                logger.info(f"Loaded model: {latest_model.name}")
            else:
                logger.warning("No trained model found, using default")
                self._create_default_model()
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._create_default_model()

    def _create_default_model(self):
        """Create a basic default model for initial predictions"""
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.model = LogisticRegression(random_state=42)

        # Train on dummy data
        dummy_texts = [
            "This is a legitimate message",
            "Buy now cheap viagra",
            "Meeting at 3pm tomorrow",
            "Win lottery now!!!",
            "Hello friend",
            "URGENT: Your account is suspended"
        ]
        dummy_labels = [0, 1, 0, 1, 0, 1]  # 0=ham, 1=spam

        X = self.vectorizer.fit_transform(dummy_texts)
        self.model.fit(X, dummy_labels)

        logger.info("Created default model")

    async def predict(
        self,
        text: str,
        model_version: str = "latest",
        user_id: str = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Make a prediction on input text"""
        try:
            if not self.vectorizer or not self.model:
                raise ValueError("Model not loaded")

            # Preprocess text
            processed_text = self._preprocess_text(text)

            # Vectorize
            X = self.vectorizer.transform([processed_text])

            # Predict
            prediction_proba = self.model.predict_proba(X)[0]
            prediction = int(self.model.predict(X)[0])

            # Get confidence
            confidence = float(prediction_proba[prediction])

            # Generate explanation
            explanation = self._generate_explanation(text, prediction)

            # Log prediction if db provided
            if db and user_id:
                await self._log_prediction(db, user_id, text, prediction, confidence, explanation)

            return {
                "prediction": "spam" if prediction == 1 else "ham",
                "confidence": confidence,
                "explanation": explanation,
                "model_version": model_version
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def _generate_explanation(self, text: str, prediction: int) -> Dict[str, Any]:
        """Generate explanation for the prediction"""
        # Simple keyword-based explanation
        spam_keywords = ['buy', 'win', 'free', 'urgent', 'click', 'subscribe', 'viagra', 'lottery']
        ham_keywords = ['meeting', 'hello', 'thanks', 'schedule', 'project']

        found_keywords = []
        text_lower = text.lower()

        if prediction == 1:  # spam
            for keyword in spam_keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
        else:  # ham
            for keyword in ham_keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)

        return {
            "keywords_found": found_keywords,
            "reason": f"Detected {len(found_keywords)} relevant keywords"
        }

    async def _log_prediction(
        self,
        db: AsyncSession,
        user_id: str,
        text: str,
        prediction: int,
        confidence: float,
        explanation: Dict[str, Any]
    ):
        """Log prediction to database"""
        # TODO: Implement database logging
        pass

    async def train_model(
        self,
        training_data: List[Dict[str, Any]],
        model_name: str = None
    ) -> Dict[str, Any]:
        """Train a new model"""
        try:
            # Prepare data
            texts = [item['text'] for item in training_data]
            labels = [item['label'] for item in training_data]

            # Create new vectorizer and model
            vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            model = LogisticRegression(random_state=42)

            # Train
            X = vectorizer.fit_transform(texts)
            model.fit(X, labels)

            # Evaluate
            predictions = model.predict(X)
            accuracy = accuracy_score(labels, predictions)
            precision = precision_score(labels, predictions, zero_division=0)
            recall = recall_score(labels, predictions, zero_division=0)
            f1 = f1_score(labels, predictions, zero_division=0)

            # Save model
            model_data = {
                'vectorizer': vectorizer,
                'model': model,
                'metrics': {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1
                },
                'training_samples': len(texts)
            }

            if model_name:
                model_path = self.models_dir / f"{model_name}.pkl"
            else:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                model_path = self.models_dir / f"model_{timestamp}.pkl"

            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)

            # Update current model
            self.vectorizer = vectorizer
            self.model = model

            logger.info(f"Trained and saved model: {model_path.name}")

            return {
                "model_name": model_path.name,
                "metrics": model_data['metrics'],
                "training_samples": len(texts)
            }

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            models = []
            for model_file in self.models_dir.glob("*.pkl"):
                try:
                    with open(model_file, 'rb') as f:
                        model_data = pickle.load(f)

                    models.append({
                        "name": model_file.stem,
                        "path": str(model_file),
                        "metrics": model_data.get('metrics', {}),
                        "training_samples": model_data.get('training_samples', 0),
                        "created": model_file.stat().st_mtime
                    })
                except Exception as e:
                    logger.warning(f"Failed to load model info for {model_file}: {e}")

            return sorted(models, key=lambda x: x['created'], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def get_prediction_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Get prediction history for user"""
        # TODO: Implement database query
        return []