# Proposed Work and System Architecture Specification

## 1. Executive Summary
This document outlines the technical specifications, architectural design, and implementation roadmap for DA2: an **Intelligent Permissioned Blockchain System**. The proposed system integrates a high-performance, asynchronous Proof-of-Work blockchain with a hybrid machine learning fraud detection engine. The primary goal is to demonstrate a "Defense-in-Depth" strategy where financial transactions are not only cryptographically verified but also behaviorally analyzed before being committed to the immutable ledger.

---

## 2. Methodology and Project Phases

The project execution is divided into five distinct modules, following an Agile development methodology.

### 2.1 Phase 1: Cryptographic Core & Data Structures
*   **Block Structure**: Implementation of a header-body structure.
    *   *Header*: Index (int), Previous Hash (SHA256 hex), Timestamp (epoch), Nonce (int), Merkle Root (SHA256 hex).
    *   *Body*: List of Transaction objects.
*   **Hashing Algorithm**: Utilization of `hashlib.sha256` for double-hashing (SHA256(SHA256(x))) to prevent length-extension attacks.
*   **Consensus**: Implementation of a customizable Proof-of-Work algorithm where $H(block) < Target$. The difficulty is adjustable (default: 2 leading zeros) to simulate mining effort without excessive CPU load during demonstration.

### 2.2 Phase 2: Intelligence & Fraud Engine
*   **Data Pipeline**: Ingestion of the Kaggle Credit Card Fraud dataset (284,807 transactions).
*   **Preprocessing**: Normalization of `Amount` using `StandardScaler` and dimensionality reduction on PCA features (V1-V28).
*   **Model Training**:
    1.  **Random Forest**: `n_estimators=100`, `max_depth=10`, `class_weight='balanced'`.
    2.  **XGBoost**: `eta=0.1`, `max_depth=6`, `scale_pos_weight` optimized for recall.
*   **Serialization**: Models are saved as `.pkl` files using `joblib` for sub-millisecond inference during runtime.

### 2.3 Phase 3: The Asynchronous Network Layer
*   **Concurrency Model**: Adoption of Python's `asyncio` library to handle non-blocking I/O.
*   **WebSocket Protocol**: Implementation of a `websockets` server (`ws://localhost:8765`) enabling bidirectional, full-duplex communication.
*   **Event Loop Management**:
    *   *Task A*: Listen for incoming client connections.
    *   *Task B*: Process incoming transaction messages.
    *   *Task C* (Background): The Miner Loop, running continuously to batch mempool transactions into blocks.

### 2.4 Phase 4: Client Simulation Interfaces
*   **The Sender (Wallet Audit)**: A CLI tool to construct JSON payloads. Includes a 'Stress Test' mode injecting 50+ TPS to validate system throughput.
*   **The Receiver (Merchant Node)**: specific logic to parse and verify incoming block headers and display transaction validity confidence (0-100%).
*   **The Dashboard (Network Monitor)**: A real-time terminal UI using ANSI escape sequences to plot block height, mempool congestion, and cumulative fraud statistics.

---

## 3. detailed System Architecture

The system utilizes a **start-topology** where the central Server node acts as the Single Source of Truth (SSOT), mimicking a centralized ledger with distributed access points.

### 3.1 Module Interaction Diagram

```text
[ Sender Client ]       [ Dashboard ]        [ Receiver Client ]
       |                      |                      |
       | (JSON/WS)            | (JSON/WS)            | (JSON/WS)
       v                      v                      v
+------------------------------------------------------------+
|                       SERVER NODE                          |
+------------------------------------------------------------+
|  1. Network Interface (AsyncIO / WebSockets)               |
|------------------------------------------------------------|
|  2. Validation Layer                                       |
|     --> Syntax Check --> Crypto Check --> [ FRAUD ENGINE ] |
|                                                 |          |
|         (Score: 0.95) <--- [ XGBoost ] <--------+          |
|             |                                              |
|             v                                              |
|  3. Mempool (Priority Queue)                               |
|------------------------------------------------------------|
|  4. Consensus Layer (Miner)                                |
|     --> Select Tx --> Merkle Tree --> Find Nonce (PoW)     |
|------------------------------------------------------------|
|  5. Storage Layer (Blockchain List / JSON Backup)          |
+------------------------------------------------------------+
```

### 3.2 Component Details

#### A. The Intelligent Validator (Fraud Engine)
Unlike standard blockchains that only verify digital signatures, our Validator includes a semantic check.
*   **Input**: `Tx = {sender, receiver, amount, timestamp}`
*   **Logic**:
    *   `Risk = (0.4 * RF_Prob) + (0.6 * XGB_Prob)`
    *   If `Tx.Amount > 500,000`, add penalty `+0.2`.
*   **Thresholding**:
    *   `Risk < 0.2`: **SAFE** (Green)
    *   `0.2 <= Risk < 0.6`: **WARN** (Yellow)
    *   `Risk >= 0.6`: **FRAUD** (Red) - Reject from Mempool.

#### B. The Mining Loop
A continuous `while True` loop running in a separate thread/task:
1.  Check if `len(mempool) > 0`.
2.  Select top $N$ transactions.
3.  Calculate `MerkleRoot(transactions)`.
4.  Construct `BlockHeader`.
5.  **Brute Force**: Increment `Nonce` until `SHA256(BlockHeader)` starts with `00`.
6.  On success: Clear processed transactions from Mempool and Broadcast `BLOCK_MINED` event.

#### C. Data Structures
```python
class Transaction:
    id: str           # UUID4
    sender: str       # Strings
    receiver: str
    amount: float
    signature: str    # Hex
    fraud_score: float

class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int
    hash: str         # The Self-Reference Hash
```

---

## 4. Evaluation Metrics

### 4.1 Performance (System Throughput)
*   **TPS (Transactions Per Second)**: Measured under stress test conditions.
    *   *Target*: > 50 TPS validation speed.
    *   *Bottleneck*: The single-threaded Python Global Interpreter Lock (GIL) and PoW calculation.
*   **Latency**: Time difference between `Tx_Sent` and `Block_Confirmed`.

### 4.2 Accuracy (Fraud Detection)
*   **Precision/Recall**: Validated against the test split of the dataset.
    *   *Target Precision*: > 95% (minimize false accusations).
    *   *Target Recall*: > 90% (catch most fraud).
*   **AUC-ROC**: The Area Under the Curve metric will be used to select the optimal operating threshold.

---

## 5. Novelty and Future Scope

### 5.1 Novel Contributions
1.  **Pre-Consensus Filtering**: Integrating ML inference *before* the block creation phase creates a cleaner ledger.
2.  **Hybrid Approach**: Combining rule-based heuristics with deep learning models provides robustness against both known and unknown attack vectors.
3.  **Visual Observability**: The terminal-based dashboard lowers the barrier to entry for understanding complex blockchain states.

### 5.2 Future Scope
*   **Decentralization**: Shifting from a single Server node to a P2P mesh network using `gossip` protocol.
*   **Smart Contracts**: Implementing a Turing-complete Virtual Machine (VM) to execute logic on-chain.
*   **Zero-Knowledge Proofs (ZKP)**: Implementing ZK-SNARKs to validate transaction correctness without revealing the Sender/Receiver identities, enhancing privacy.

---

## 6. Code Availability
The project implementation, including the blockchain core, fraud engine, and client interfaces, is hosted on GitHub:
**Repository**: [https://github.com/Super-cod/Fraud_Bockchain_transaction](https://github.com/Super-cod/Fraud_Bockchain_transaction)

## 7. Conclusion
The proposed architecture provides a robust framework for simulating the next generation of financial infrastructure. By successfully coupling the immutability of blockchains with the predictive power of AI, DA2 offers a comprehensive solution for secure, auditable, and intelligent value transfer.
