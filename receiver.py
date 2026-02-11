import asyncio
import websockets
import json
import time
import os
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Stats tracking
rx_stats = {
    "total_tx": 0,
    "total_blocks": 0,
    "fraud_alerts": 0,
    "total_volume": 0.0,
    "start_time": time.time()
}

def print_banner():
    print(f"""
{Fore.BLUE}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║              📡  TRANSACTION RECEIVER TERMINAL               ║
║              Live Blockchain Event Stream                     ║
╠══════════════════════════════════════════════════════════════╣
║  Mode     : Passive Listener                                 ║
║  Stream   : Transactions + Blocks                            ║
║  Alerts   : High-Risk Fraud Detection                        ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

def print_transaction(tx):
    fraud = tx.get("fraud_analysis", {})
    score = fraud.get("score", 0)
    risk = fraud.get("risk_level", "UNKNOWN")
    decision = fraud.get("decision", "UNKNOWN")
    details = fraud.get("details", [])

    rx_stats["total_tx"] += 1
    rx_stats["total_volume"] += float(tx.get("amount", 0))

    # Color based on risk
    if risk == "HIGH":
        rx_stats["fraud_alerts"] += 1
        border_color = Fore.RED
        risk_icon = "🚨"
        risk_bar = f"{Back.RED}{Fore.WHITE}{Style.BRIGHT} FRAUD ALERT {Style.RESET_ALL}"
    elif risk == "MEDIUM":
        border_color = Fore.YELLOW
        risk_icon = "⚠️"
        risk_bar = f"{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT} MEDIUM RISK {Style.RESET_ALL}"
    else:
        border_color = Fore.GREEN
        risk_icon = "✅"
        risk_bar = f"{Back.GREEN}{Fore.BLACK}{Style.BRIGHT}    SAFE     {Style.RESET_ALL}"

    amount = float(tx.get("amount", 0))
    amount_color = Fore.RED if amount > 500000 else (Fore.YELLOW if amount > 100000 else Fore.WHITE)

    tx_hash = tx.get("tx_id", "N/A")

    print(f"""
{border_color}{Style.BRIGHT}┌──────────────────── {risk_icon} TRANSACTION #{rx_stats['total_tx']} ────────────────────┐{Style.RESET_ALL}
│                                                              │
│  {Fore.CYAN}SHA-256 Hash :{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{tx_hash[:24]}...{tx_hash[-8:]}{Style.RESET_ALL}
│                                                              │
│  {Fore.CYAN}From         :{Style.RESET_ALL} {tx.get('sender', 'N/A')}
│  {Fore.CYAN}To           :{Style.RESET_ALL} {tx.get('receiver', 'N/A')}
│  {Fore.CYAN}Amount       :{Style.RESET_ALL} {amount_color}{Style.BRIGHT}${amount:>14,.2f}{Style.RESET_ALL}
│  {Fore.CYAN}Type         :{Style.RESET_ALL} {tx.get('type', 'N/A')}
│  {Fore.CYAN}Timestamp    :{Style.RESET_ALL} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tx.get('timestamp', 0)))}
│                                                              │
│  {Fore.WHITE}{Style.BRIGHT}──── 🔍 AI FRAUD ANALYSIS ────{Style.RESET_ALL}
│  {Fore.CYAN}Risk Score   :{Style.RESET_ALL} {border_color}{Style.BRIGHT}{score:>6.1f} / 100{Style.RESET_ALL}  {'█' * int(score / 5)}{'░' * (20 - int(score / 5))}
│  {Fore.CYAN}Risk Level   :{Style.RESET_ALL} {risk_bar}
│  {Fore.CYAN}Decision     :{Style.RESET_ALL} {border_color}{Style.BRIGHT}{decision}{Style.RESET_ALL}
│  {Fore.CYAN}Details      :{Style.RESET_ALL} {'; '.join(details) if details else 'No anomalies detected'}
│                                                              │
{border_color}{Style.BRIGHT}└──────────────────────────────────────────────────────────────┘{Style.RESET_ALL}""")

def print_block(block):
    rx_stats["total_blocks"] += 1
    tx_count = len(block.get("transactions", []))

    print(f"""
{Fore.GREEN}{Style.BRIGHT}╔══════════════════════ ⛏️  NEW BLOCK MINED ══════════════════════╗{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}                                                                  {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Block Index    :{Style.RESET_ALL} #{block.get('index', '?'):<47} {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Block Hash     :{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{block.get('hash', 'N/A')}{Style.RESET_ALL}  {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Previous Hash  :{Style.RESET_ALL} {block.get('previous_hash', 'N/A')[:48]}... {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Merkle Root    :{Style.RESET_ALL} {block.get('merkle_root', 'N/A')[:48]}... {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Nonce          :{Style.RESET_ALL} {block.get('nonce', 0):<47} {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Transactions   :{Style.RESET_ALL} {tx_count} transaction(s) committed                    {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Mined At       :{Style.RESET_ALL} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.get('timestamp', 0))):<47} {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}                                                                  {Fore.GREEN}║{Style.RESET_ALL}
{Fore.GREEN}{Style.BRIGHT}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}""")

    # Print each tx in the block briefly
    for i, tx in enumerate(block.get("transactions", [])):
        fraud = tx.get("fraud_analysis", {})
        risk = fraud.get("risk_level", "?")
        r_color = Fore.RED if risk == "HIGH" else (Fore.YELLOW if risk == "MEDIUM" else Fore.GREEN)
        print(f"  {Fore.WHITE}  └─ TX {i+1}: {tx.get('sender','?')[:12]} → {tx.get('receiver','?')[:12]}  ${float(tx.get('amount',0)):>12,.2f}  {r_color}[{risk}]{Style.RESET_ALL}")

def print_stats_bar():
    uptime = time.time() - rx_stats["start_time"]
    mins = int(uptime // 60)
    secs = int(uptime % 60)
    print(f"\n{Fore.WHITE}{Style.DIM}  📊 Received: {rx_stats['total_tx']} txs | {rx_stats['total_blocks']} blocks | 🚨 {rx_stats['fraud_alerts']} alerts | 💰 ${rx_stats['total_volume']:,.2f} volume | ⏱ {mins}m {secs}s{Style.RESET_ALL}")

async def receiver_loop():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            clear()
            print_banner()
            print(f"{Fore.GREEN}{Style.BRIGHT}🔗 Connected! Listening for events...{Style.RESET_ALL}\n")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "NEW_TRANSACTION":
                    print_transaction(data.get("transaction", {}))
                    print_stats_bar()

                elif msg_type == "NEW_BLOCK":
                    print_block(data.get("block", {}))
                    print_stats_bar()

                elif msg_type == "WELCOME":
                    pass  # Already handled

    except ConnectionRefusedError:
        print(f"""
{Fore.RED}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║  ❌  CONNECTION FAILED                       ║
║  Server is not running on ws://localhost:8765 ║
║  Start the server first: python server.py    ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}""")
    except websockets.exceptions.ConnectionClosed:
        print(f"\n{Fore.RED}🔌 Connection lost.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        asyncio.run(receiver_loop())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Receiver terminated.{Style.RESET_ALL}")
        sys.exit(0)
