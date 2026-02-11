
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# Try to import XGBoost, but fallback if not available
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not installed. Skipping XGBoost model.")

DATA_PATH = r"data/output_1_to_10.csv"
MODEL_DIR = r"models"

def train_and_save_models():
    print("🚀 Starting Model Training Pipeline...")

    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Data file not found at {DATA_PATH}")
        return

    print(f"📂 Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # 2. Preprocessing
    print("🛠️ Preprocessing data...")
    
    # Drop columns that are not useful for prediction (or too high cardinality)
    # keeping 'type', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest'
    # 'nameOrig', 'nameDest', 'isFlaggedFraud', 'step' are dropped for simplicity/leakage prevention
    # In a real scenario, you might feature engineer 'step' (time of day) or 'nameDest' (frequency)
    
    features = ['type', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
    target = 'isFraud'
    
    X = df[features].copy()
    y = df[target]

    # Encode Categorical Data ('type')
    le = LabelEncoder()
    X['type'] = le.fit_transform(X['type'])
    
    # Save the encoder for later use in inference
    with open(os.path.join(MODEL_DIR, "label_encoder_type.pkl"), "wb") as f:
        pickle.dump(le, f)
    print("✅ Label Encoder saved.")

    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"📊 Data split: {X_train.shape[0]} training samples, {X_test.shape[0]} test samples")

    # 4. Train Random Forest
    print("🌲 Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    y_pred_rf = rf_model.predict(X_test)
    print(f"✅ Random Forest Accuracy: {accuracy_score(y_test, y_pred_rf):.4f}")
    # print(classification_report(y_test, y_pred_rf))

    # Save RF Model
    with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "wb") as f:
        pickle.dump(rf_model, f)
    print("💾 Random Forest model saved.")

    # 5. Train XGBoost (Optional)
    if XGBOOST_AVAILABLE:
        print("🚀 Training XGBoost Classifier...")
        xgb_model = XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            use_label_encoder=False,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train, y_train)
        
        y_pred_xgb = xgb_model.predict(X_test)
        print(f"✅ XGBoost Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}")
        
        # Save XGBoost Model
        with open(os.path.join(MODEL_DIR, "xgb_model.pkl"), "wb") as f:
            pickle.dump(xgb_model, f)
        print("💾 XGBoost model saved.")
    
    print("\n🎉 Training Complete! Models are ready in 'models/' directory.")

if __name__ == "__main__":
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    train_and_save_models()
