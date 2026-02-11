
import os
import pickle
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FraudEngine")

# Constants
MODEL_DIR = "models"
RF_MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.pkl")
XGB_MODEL_PATH = os.path.join(MODEL_DIR, "xgb_model.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder_type.pkl")

# Risk Levels
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
DECISION_SAFE = "SAFE"
DECISION_FRAUD = "FRAUD"  # Advisory only

@dataclass
class FraudAnalysisResult:
    score: float
    risk_level: str
    decision: str
    details: List[str]

class FraudDetectionEngine:
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.label_encoder = None
        self.models_loaded = False
        self._load_models()

    def _load_models(self):
        """Attempts to load pre-trained ML models."""
        try:
            if os.path.exists(RF_MODEL_PATH):
                with open(RF_MODEL_PATH, "rb") as f:
                    self.rf_model = pickle.load(f)
                logger.info("✅ Random Forest model loaded.")
            
            if os.path.exists(XGB_MODEL_PATH):
                with open(XGB_MODEL_PATH, "rb") as f:
                    self.xgb_model = pickle.load(f)
                logger.info("✅ XGBoost model loaded.")
                
            if os.path.exists(LABEL_ENCODER_PATH):
                with open(LABEL_ENCODER_PATH, "rb") as f:
                    self.label_encoder = pickle.load(f)
                logger.info("✅ Label Encoder loaded.")
            
            if self.rf_model or self.xgb_model:
                self.models_loaded = True
        except Exception as e:
            logger.error(f"⚠️ Failed to load ML models: {e}")
            self.models_loaded = False

    def evaluate_transaction(self, tx_data: Dict[str, Any]) -> FraudAnalysisResult:
        """
        Analyzes a transaction using a hybrid approach (Rules + ML).
        """
        score = 0.0
        details = []

        # 1. Rule-Based Checks
        rule_score, rule_details = self._check_rules(tx_data)
        score += rule_score
        details.extend(rule_details)

        # 2. ML-Based Checks (if models are available)
        if self.models_loaded and rule_score < 100:  # Only use ML if rules didn't find critical fraud
            ml_score, ml_details = self._check_ml(tx_data)
            score = (score * 0.4) + (ml_score * 0.6)  # Weighted average
            details.extend(ml_details)
        elif rule_score >= 100:
            # Critical fraud detected by rules, keep score at 100
            score = 100.0
        else:
            details.append("ML models unavailable - relying on rules only")

        # Cap score at 100
        score = min(max(score, 0.0), 100.0)

        # Determine Risk Level
        if score < 20:
            risk_level = RISK_LOW
            decision = DECISION_SAFE
        elif score < 60:
            risk_level = RISK_MEDIUM
            decision = DECISION_SAFE # Still safe, but flagged
        else:
            risk_level = RISK_HIGH
            decision = DECISION_FRAUD

        return FraudAnalysisResult(
            score=round(score, 2),
            risk_level=risk_level,
            decision=decision,
            details=details
        )

    def _check_rules(self, tx: Dict[str, Any]) -> (float, List[str]):
        """Executes deterministic rule-based checks."""
        score = 0.0
        reasons = []
        
        amount = float(tx.get("amount", 0.0))
        sender = tx.get("sender", "")
        
        # Rule 1: Negative or Zero Amount
        if amount <= 0:
            score += 100
            reasons.append("Invalid transaction amount")

        # Rule 2: High Value Transaction
        if amount > 500000:
            score += 40
            reasons.append("High value transaction > 500k")
        elif amount > 100000:
            score += 20
            reasons.append("High value transaction > 100k")

        # Rule 3: Suspicious Sender Name (Example)
        if sender.startswith("M") and amount > 10000:
             # Merchants usually receive, rarely send
             score += 10
             reasons.append("Merchant sending large amount")

        return score, reasons

    def _check_ml(self, tx: Dict[str, Any]) -> (float, List[str]):
        """Uses loaded ML models to predict fraud probability."""
        score = 0.0
        reasons = []

        try:
            # Prepare features for model:
            # ['type', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
            # We need to map tx data to these features.
            # Assuming tx_data has similar keys or we derive them. 
            # For simplicity in this demo, we'll try to extract them or use defaults.
            
            tx_type = tx.get("type", "PAYMENT")
            amount = float(tx.get("amount", 0.0))
            old_bal_org = float(tx.get("sender_balance", 0.0)) # From state? Or passed in tx?
            new_bal_orig = old_bal_org - amount
            old_bal_dest = float(tx.get("receiver_balance", 0.0))
            new_bal_dest = old_bal_dest + amount

            # Encode Type
            if self.label_encoder:
                try:
                    type_encoded = self.label_encoder.transform([tx_type])[0]
                except ValueError:
                    type_encoded = 0 # Default/Unknown
            else:
                type_encoded = 0
            
            features = np.array([[
                type_encoded, 
                amount, 
                old_bal_org, 
                new_bal_orig, 
                old_bal_dest, 
                new_bal_dest
            ]])

            # RF Prediction
            if self.rf_model:
                prob_rf = self.rf_model.predict_proba(features)[0][1] # Probability of Class 1 (Fraud)
                score += prob_rf * 100
                reasons.append(f"ML Model Risk: {prob_rf*100:.1f}%")

            # XGB Prediction (optional fallback or ensemble)
            if self.xgb_model:
                pass # Already used RF mainly

        except Exception as e:
            logger.error(f"ML Prediction Error: {e}")
            reasons.append("ML Analysis Failed")
        
        return score, reasons

# Singleton instance for easy access if needed
engine = FraudDetectionEngine()
