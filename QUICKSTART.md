# 🚀 Quick Start Guide

## System Overview

This is a **production-grade local permissioned blockchain** with AI-powered fraud detection.

### Key Features
- ✅ SHA-256 Proof-of-Work consensus
- ✅ Real-time WebSocket communication
- ✅ Hybrid fraud detection (Rules + ML)
- ✅ Beautiful color-coded terminals
- ✅ 99.7% ML model accuracy
- ✅ Full transaction audit trail

---

## 📋 Prerequisites

```powershell
# Install Python dependencies (if not already installed)
pip install websockets colorama scikit-learn numpy pandas xgboost
```

---

## 🎯 How to Run

### Option 1: Automated Launch (Recommended)

```powershell
# Start everything with one command
.\run_system.bat
```

This opens **4 terminal windows**:
1. **Server** (Cyan) - Blockchain node & fraud engine
2. **Receiver** (Purple) - Live transaction stream
3. **Dashboard** (Yellow) - System metrics
4. **Sender** (Green) - Interactive transaction creator

### Option 2: Manual Launch

```powershell
# Terminal 1: Start server
python server.py

# Terminal 2: Start receiver
python receiver.py

# Terminal 3: Start dashboard
python dashboard.py

# Terminal 4: Start sender
python sender.py
```

---

## 🎮 Using the Sender

The **Sender** terminal has an interactive menu:

```
[1] Send Manual Transaction
    - Enter sender, receiver, amount, type

[2] Send Batch (Random Transactions)
    - Specify count and delay
    - Generates realistic random transactions

[3] Send Fraud Test (High Amount)
    - Sends 5 pre-configured fraud scenarios:
      • 9.5M transfer (HIGH RISK)
      • 750K cash out (MEDIUM RISK)
      • Merchant sending large amount
      • Negative amount (CRITICAL)
      • 10M transfer (HIGH RISK)

[4] Send Rapid-Fire Stress Test
    - Max speed transaction flood
    - Tests system throughput

[q] Quit
```

---

## 📊 What to Watch

### In the **Server** window:
- Full transaction details with SHA-256 hashes
- Fraud analysis scores and risk levels
- Block mining with Proof-of-Work nonces
- Chain validation status

### In the **Receiver** window:
- Color-coded transactions (🟢 Safe, 🟡 Medium, 🔴 Fraud)
- Visual risk bars showing fraud probability
- Block confirmations with all included transactions
- Running statistics (total volume, fraud alerts)

### In the **Dashboard** window:
- System health and uptime
- Block height and TPS (transactions per second)
- Fraud detection rate
- Latest block details
- Chain visualization (last 5 blocks)

---

## 🛑 Stopping the System

### Option 1: Using the launcher
Press any key in the launcher window

### Option 2: Dedicated stop script
```powershell
.\stop_system.bat
```

### Option 3: Manual
Close all 4 terminal windows

---

## 🧪 Testing

Run the test suite to verify all components:

```powershell
python test_system.py
```

This tests:
- Blockchain core (mining, validation)
- Fraud detection engine (rules + ML)
- ML model loading
- Data file integrity
- Dependencies

---

## 📁 Project Structure

```
crypto/
├── blockchain.py          # Core blockchain logic
├── fraud_engine.py        # AI fraud detection
├── server.py              # WebSocket server
├── sender.py              # Transaction sender CLI
├── receiver.py            # Transaction receiver CLI
├── dashboard.py           # Live metrics dashboard
├── train_model.py         # ML model training
├── test_system.py         # System tests
├── run_system.bat         # Automated launcher
├── stop_system.bat        # Cleanup script
├── README.md              # Full technical documentation
├── QUICKSTART.md          # This file
├── models/                # Trained ML models
│   ├── rf_model.pkl
│   ├── xgb_model.pkl
│   └── label_encoder_type.pkl
└── data/
    └── output_1_to_10.csv # Training dataset (90K+ transactions)
```

---

## 🔧 Troubleshooting

### Port 8765 already in use
```powershell
.\stop_system.bat
# Wait 5 seconds
.\run_system.bat
```

### ML models not found
```powershell
python train_model.py
```

### Connection refused
- Ensure server.py is running first
- Wait 7 seconds after server starts
- Check Windows Firewall settings

### Terminal colors not showing
- Use Windows Terminal (recommended)
- Or enable ANSI colors in CMD: `reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1`

---

## 💡 Tips

1. **Start with Fraud Test**: Use option `[3]` in Sender to see the fraud detection in action
2. **Watch the Dashboard**: Keep it visible to monitor system health
3. **Check Receiver**: See every transaction with full fraud analysis
4. **Stress Test**: Option `[4]` shows how the system handles high load

---

## 📚 Learn More

See `README.md` for:
- Full architecture explanation
- Design philosophy
- Security guarantees
- Known limitations
- Transaction lifecycle details

---

## ✅ Quick Verification

After starting the system:

1. ✅ Server shows "🚀 Server listening on ws://localhost:8765"
2. ✅ Receiver shows "🔗 Connected! Listening for events..."
3. ✅ Dashboard shows live metrics updating every 5 seconds
4. ✅ Sender shows interactive menu

If all 4 are green, you're ready to go!

---

**Enjoy your blockchain! 🎉**
