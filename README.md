# 🏗️ Local Permissioned Blockchain with AI Fraud Detection

## 📌 Overview

This project implements a **local, permissioned blockchain system** designed to simulate real-world financial transaction processing.
The system runs **entirely on a single machine**, yet preserves key blockchain principles such as immutability, cryptographic integrity, ordered consensus, and auditability.

It integrates a **rule-based + ML-assisted fraud detection engine**, real-time WebSocket clients, and an automated Proof-of-Work (PoW) mining mechanism.

> ⚠️ This system is **intentionally not decentralized**.
> Decentralization is constrained by the requirement that all components run locally.

---

## 🎯 Project Goals

The primary goals of this system are:

• Demonstrate core blockchain mechanics without external infrastructure
• Model real financial settlement systems (banks, CBDCs, private ledgers)
• Integrate AI fraud analysis safely into a ledger pipeline
• Maintain deterministic, auditable transaction processing
• Support real-time client interaction via terminals

This is **not** a cryptocurrency clone.
It is a **controlled blockchain laboratory**.

---

## 🧠 Design Philosophy

### Why Local?

The system is designed under the constraint that:
• No cloud
• No external nodes
• No peer-to-peer network

This mirrors how:
• Internal bank ledgers
• CBDC testbeds
• Permissioned enterprise blockchains

are actually built.

### What “Blockchain” Means Here

In this project, *blockchain* means:

✔ Append-only ledger
✔ Cryptographic block linking
✔ Proof-of-Work for ordering
✔ Tamper detection
✔ Deterministic validation

It does **not** mean:
✖ Trustless consensus
✖ Anonymous participation
✖ Economic mining incentives

---

## 🧱 High-Level Architecture

The system is composed of **independent logical components**, even though all run locally.

```
Clients ──▶ WebSocket Server ──▶ Validation Pipeline ──▶ Mempool ──▶ Miner ──▶ Blockchain
                                   │
                                   └──▶ Fraud Detection Engine
```

Each component has a **single responsibility**.

---

## 🧩 Component Breakdown (Detailed)

---

## 1️⃣ Blockchain Core (`blockchain.py`)

### Role

The blockchain is the **source of truth**.
Once data is written here, it cannot be altered without detection.

### Responsibilities

• Maintain the chain of blocks
• Enforce Proof-of-Work
• Validate block integrity
• Expose read-only access to history

### Block Structure

Each block contains:

```
Block {
  index           → Sequential block number
  timestamp       → Block creation time
  transactions    → List of validated transactions
  previous_hash   → Hash of previous block
  nonce           → PoW counter
  merkle_root     → Hash summary of transactions
  hash            → SHA-256 block hash
}
```

### Security Properties

• Any modification breaks hash linkage
• Blocks cannot be reordered
• Full chain validation is possible at any time

---

## 2️⃣ Fraud Detection Engine (`fraud_engine.py`)

### Role

The fraud engine is an **analytical service**, not a consensus authority.

It evaluates **risk**, not **validity**.

### Processing Model

Every incoming transaction is analyzed **before** entering the mempool.

The engine outputs:

```
fraud_score  → 0–100 risk score
risk_level   → LOW / MEDIUM / HIGH
decision     → SAFE / FRAUD (advisory)
```

### Detection Methods

**Hybrid Approach**:

1. Rule-based checks
   • Negative amounts
   • Rapid repeated transfers
   • Threshold violations

2. ML models (optional)
   • Random Forest
   • XGBoost

### Fault Tolerance

• If ML models fail to load → rules only
• No crashes propagate to the blockchain
• Blockchain remains operational at all times

### Important Design Choice

⚠️ Fraud detection **never rejects transactions** at protocol level.
The analysis is stored for audit and policy enforcement.

---

## 3️⃣ WebSocket Server (`server.py`)

### Role

The server acts as the **communication backbone**, not the decision maker.

### Responsibilities

• Manage WebSocket connections
• Receive transactions from clients
• Route data through validation & fraud analysis
• Broadcast system events

### Concurrency Model

• AsyncIO event loop
• Non-blocking I/O
• Background mining thread

### Why WebSockets?

• Real-time updates
• Bidirectional communication
• Terminal-friendly
• Low overhead for local systems

---

## 4️⃣ Mempool (In-Memory)

### Role

The mempool holds **validated, pending transactions**.

### Characteristics

• FIFO ordering
• Temporary storage
• Cleared once transactions are mined

### What the Mempool Guarantees

✔ No invalid transaction enters mining
✔ Clear separation between validation and consensus

---

## 5️⃣ Miner & Proof-of-Work

### Role

The miner is responsible for **ordering transactions** and committing them immutably.

### Proof-of-Work Purpose (Local Context)

PoW is used to:

• Enforce temporal cost
• Prevent instant block creation
• Simulate real blockchain behavior

It is **not** used for economic security.

### Mining Logic

• Runs automatically every fixed interval
• Mines all current mempool transactions
• Appends a new block to the chain

---

## 6️⃣ Client Interfaces

All clients connect via WebSockets.

### A. Sender Terminal (`sender.py`)

• Manual transaction creation
• Batch transaction testing
• Fraud scenario simulation

### B. Receiver Terminal (`receiver.py`)

• Passive listener
• Displays incoming transactions
• Highlights high-risk events

### C. Live Dashboard (`dashboard.py`)

• TPS (Transactions per second)
• Block height
• Difficulty
• System health indicators

---

## 🔄 Transaction Lifecycle (Step-by-Step)

1. Sender creates transaction
2. Transaction sent to server
3. Server forwards to fraud engine
4. Fraud analysis attached
5. Deterministic validation
6. Transaction enters mempool
7. Miner performs PoW
8. Block appended to blockchain
9. All clients notified

This flow is **linear, auditable, and deterministic**.

---

## 📄 Transaction Schema

```json
{
  "tx_id": "a1b2c3d4",
  "sender": "User_123",
  "receiver": "User_456",
  "amount": 500.0,
  "timestamp": 1700000000,
  "type": "PAYMENT",
  "fraud_analysis": {
    "score": 12.5,
    "risk": "LOW",
    "decision": "SAFE"
  }
}
```

---

## 🔐 Security Guarantees

✔ Ledger immutability
✔ Tamper detection
✔ Deterministic validation
✔ Audit-ready transaction history

---

## ⚠️ Known Limitations (Explicit by Design)

• Single node
• No cryptographic signatures
• No peer-to-peer gossip
• No fork resolution
• No economic incentives

These are **intentional trade-offs**, not oversights.

---

## 🚀 How to Run

1. Start server
2. Launch sender terminal
3. Launch receiver / dashboard
4. Transactions flow in real time

A batch script (`run_system.bat`) automates startup.

---

## 🧪 Intended Use Cases

• Academic projects
• Blockchain learning labs
• Fraud detection experiments
• CBDC / banking simulations
• Systems architecture demonstrations

---

## 🧠 Final Note

This project prioritizes **clarity, correctness, and auditability** over hype.
It demonstrates how blockchain concepts apply to **real financial systems**, not just cryptocurrencies.

It is a foundation — not a fantasy.
