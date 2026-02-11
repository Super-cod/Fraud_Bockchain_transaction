"""
Data Preprocessing Module for Transaction Fraud Detection
Handles data loading, cleaning, feature engineering, and normalization
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle


class TransactionPreprocessor:
    """
    Handles all data preprocessing for fraud detection
    
    Steps:
    1. Load CSV data
    2. Feature engineering (extract meaningful features)
    3. Encode categorical variables
    4. Normalize numerical features
    5. Split into train/validation sets
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        
    def load_data(self, filepath):
        """
        Load transaction data from CSV
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            pandas DataFrame
        """
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} transactions")
        print(f"Fraud cases: {df['isFraud'].sum()} ({df['isFraud'].mean()*100:.2f}%)")
        return df
    
    def engineer_features(self, df):
        """
        Create meaningful features from raw transaction data
        
        Features created:
        - amount: Transaction amount
        - balance_change_orig: Change in sender's balance
        - balance_change_dest: Change in receiver's balance
        - type_encoded: Transaction type (encoded)
        - is_transfer: Binary flag for TRANSFER transactions
        - is_cash_out: Binary flag for CASH_OUT transactions
        - balance_ratio: Ratio of transaction to sender's balance
        
        Args:
            df: Raw dataframe
            
        Returns:
            DataFrame with engineered features
        """
        print("Engineering features...")
        
        features_df = pd.DataFrame()
        
        # Basic features
        features_df['amount'] = df['amount']
        
        # Balance changes (indicate unusual behavior)
        features_df['balance_change_orig'] = df['newbalanceOrig'] - df['oldbalanceOrg']
        features_df['balance_change_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
        
        # Transaction type encoding (some types are riskier)
        features_df['type_encoded'] = self.label_encoder.fit_transform(df['type'])
        
        # Binary flags for risky transaction types
        features_df['is_transfer'] = (df['type'] == 'TRANSFER').astype(int)
        features_df['is_cash_out'] = (df['type'] == 'CASH_OUT').astype(int)
        
        # Balance ratio (large transactions relative to account balance are suspicious)
        features_df['balance_ratio'] = df['amount'] / (df['oldbalanceOrg'] + 1)  # +1 to avoid division by zero
        
        # Time step (fraud patterns may vary over time)
        features_df['time_step'] = df['step']
        
        # Error flags (when balance doesn't match transaction)
        features_df['error_balanceOrig'] = ((df['oldbalanceOrg'] - df['amount']) != df['newbalanceOrig']).astype(int)
        features_df['error_balanceDest'] = ((df['oldbalanceDest'] + df['amount']) != df['newbalanceDest']).astype(int)
        
        # Target variable
        features_df['isFraud'] = df['isFraud']
        
        # Handle any NaN or infinite values
        features_df = features_df.replace([np.inf, -np.inf], np.nan)
        features_df = features_df.fillna(0)
        
        self.feature_names = [col for col in features_df.columns if col != 'isFraud']
        
        print(f"Created {len(self.feature_names)} features")
        return features_df
    
    def prepare_data(self, df, test_size=0.2, random_state=42):
        """
        Prepare data for model training
        
        Args:
            df: DataFrame with features
            test_size: Fraction for validation set
            random_state: Random seed for reproducibility
            
        Returns:
            X_train, X_val, y_train, y_val (normalized)
        """
        print("Preparing train/validation split...")
        
        # Separate features and target
        X = df[self.feature_names].values
        y = df['isFraud'].values
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Normalize features (important for neural networks)
        X_train = self.scaler.fit_transform(X_train)
        X_val = self.scaler.transform(X_val)
        
        print(f"Train set: {len(X_train)} samples")
        print(f"Validation set: {len(X_val)} samples")
        print(f"Train fraud rate: {y_train.mean()*100:.2f}%")
        print(f"Val fraud rate: {y_val.mean()*100:.2f}%")
        
        return X_train, X_val, y_train, y_val
    
    def save_preprocessor(self, filepath='preprocessor.pkl'):
        """
        Save scaler and encoders for deployment
        
        Args:
            filepath: Where to save the preprocessor
        """
        print(f"Saving preprocessor to {filepath}...")
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_names': self.feature_names,
                'input_size': len(self.feature_names) if self.feature_names else 0
            }, f)
        print("Preprocessor saved!")
    
    def load_preprocessor(self, filepath='preprocessor.pkl'):
        """
        Load saved preprocessor
        
        Args:
            filepath: Path to saved preprocessor
        """
        print(f"Loading preprocessor from {filepath}...")
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.scaler = data['scaler']
            self.label_encoder = data['label_encoder']
            self.feature_names = data['feature_names']
        print("Preprocessor loaded!")
    
    def preprocess_single_transaction(self, transaction_data):
        """
        Preprocess a single transaction for real-time prediction
        
        Args:
            transaction_data: Dict with transaction features
            
        Returns:
            Normalized feature array ready for model
        """
        # Create feature vector (same order as training)
        features = []
        
        # This should match the feature engineering logic
        # For simplicity in demo, we'll use a basic version
        # In production, this should exactly match engineer_features
        
        required_features = [
            'amount', 'balance_change_orig', 'balance_change_dest',
            'type_encoded', 'is_transfer', 'is_cash_out',
            'balance_ratio', 'time_step', 'error_balanceOrig', 'error_balanceDest'
        ]
        
        feature_vector = np.array([[transaction_data.get(f, 0) for f in required_features]])
        normalized = self.scaler.transform(feature_vector)
        
        return normalized
