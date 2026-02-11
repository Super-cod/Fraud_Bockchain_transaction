"""
System Test Script
Tests all components without starting the full WebSocket server
"""

import sys
import os

print("=" * 60)
print("  BLOCKCHAIN SYSTEM - COMPONENT TEST")
print("=" * 60)
print()

# Test 1: Blockchain Core
print("[1/5] Testing Blockchain Core...")
try:
    from blockchain import Blockchain, Transaction, Block
    bc = Blockchain()
    assert len(bc.chain) == 1, "Genesis block missing"
    assert bc.difficulty == 2, "Wrong difficulty"
    
    # Add transaction
    tx = Transaction("Alice", "Bob", 100.0, "PAYMENT")
    bc.mempool.append(tx)
    assert len(bc.mempool) == 1, "Mempool error"
    
    # Mine block
    new_block = bc.mine_pending_transactions("MINER")
    assert new_block is not None, "Mining failed"
    assert len(bc.chain) == 2, "Block not added"
    assert len(bc.mempool) == 0, "Mempool not cleared"
    assert bc.is_chain_valid(), "Chain invalid"
    
    print("  ✅ Blockchain Core: PASS")
    print(f"     - Genesis block created")
    print(f"     - Transaction added to mempool")
    print(f"     - Block mined successfully")
    print(f"     - Chain validation: OK")
except Exception as e:
    print(f"  ❌ Blockchain Core: FAIL - {e}")
    sys.exit(1)

# Test 2: Fraud Detection Engine
print("\n[2/5] Testing Fraud Detection Engine...")
try:
    from fraud_engine import FraudDetectionEngine
    engine = FraudDetectionEngine()
    
    # Test normal transaction
    normal_tx = {
        "sender": "C123456789",
        "receiver": "C987654321",
        "amount": 100.0,
        "type": "PAYMENT"
    }
    result = engine.evaluate_transaction(normal_tx)
    assert result.score >= 0 and result.score <= 100, "Invalid score"
    assert result.risk_level in ["LOW", "MEDIUM", "HIGH"], "Invalid risk level"
    
    # Test fraud transaction
    fraud_tx = {
        "sender": "C111111111",
        "receiver": "C222222222",
        "amount": 9000000.0,
        "type": "TRANSFER"
    }
    fraud_result = engine.evaluate_transaction(fraud_tx)
    assert fraud_result.score > result.score, "Fraud not detected"
    
    # Test negative amount
    invalid_tx = {
        "sender": "C333333333",
        "receiver": "C444444444",
        "amount": -500.0,
        "type": "PAYMENT"
    }
    invalid_result = engine.evaluate_transaction(invalid_tx)
    assert invalid_result.score == 100, "Negative amount not caught"
    
    print("  ✅ Fraud Detection Engine: PASS")
    print(f"     - Normal tx score: {result.score:.1f} ({result.risk_level})")
    print(f"     - Fraud tx score: {fraud_result.score:.1f} ({fraud_result.risk_level})")
    print(f"     - Invalid tx score: {invalid_result.score:.1f} ({invalid_result.risk_level})")
    print(f"     - ML Models: {'LOADED' if engine.models_loaded else 'NOT LOADED'}")
except Exception as e:
    print(f"  ❌ Fraud Detection Engine: FAIL - {e}")
    sys.exit(1)

# Test 3: ML Models
print("\n[3/5] Testing ML Models...")
try:
    import pickle
    rf_path = "models/rf_model.pkl"
    xgb_path = "models/xgb_model.pkl"
    encoder_path = "models/label_encoder_type.pkl"
    
    models_exist = os.path.exists(rf_path) and os.path.exists(xgb_path) and os.path.exists(encoder_path)
    
    if models_exist:
        with open(rf_path, "rb") as f:
            rf_model = pickle.load(f)
        with open(xgb_path, "rb") as f:
            xgb_model = pickle.load(f)
        with open(encoder_path, "rb") as f:
            encoder = pickle.load(f)
        
        print("  ✅ ML Models: PASS")
        print(f"     - Random Forest: LOADED")
        print(f"     - XGBoost: LOADED")
        print(f"     - Label Encoder: LOADED")
    else:
        print("  ⚠️  ML Models: NOT TRAINED")
        print(f"     Run: python train_model.py")
except Exception as e:
    print(f"  ❌ ML Models: FAIL - {e}")

# Test 4: Data File
print("\n[4/5] Testing Data File...")
try:
    import pandas as pd
    df = pd.read_csv("data/output_1_to_10.csv")
    print("  ✅ Data File: PASS")
    print(f"     - Rows: {len(df):,}")
    print(f"     - Columns: {len(df.columns)}")
    print(f"     - Fraud cases: {df['isFraud'].sum():,}")
except Exception as e:
    print(f"  ❌ Data File: FAIL - {e}")

# Test 5: Dependencies
print("\n[5/5] Testing Dependencies...")
try:
    import websockets
    import colorama
    import sklearn
    import numpy
    import pandas
    
    print("  ✅ Dependencies: PASS")
    print(f"     - websockets: OK")
    print(f"     - colorama: OK")
    print(f"     - scikit-learn: OK")
    print(f"     - numpy: OK")
    print(f"     - pandas: OK")
except ImportError as e:
    print(f"  ❌ Dependencies: FAIL - {e}")
    print(f"     Run: pip install websockets colorama scikit-learn numpy pandas xgboost")

print()
print("=" * 60)
print("  ALL TESTS COMPLETE")
print("=" * 60)
print()
print("✅ System is ready! Run: .\\run_system.bat")
print()
