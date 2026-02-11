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

def format_uptime(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hrs > 0:
        return f"{hrs}h {mins}m {secs}s"
    return f"{mins}m {secs}s"

def format_hash(h, length=16):
    if not h or len(h) < length:
        return h or "N/A"
    return f"{h[:length]}...{h[-6:]}"

def draw_dashboard(chain_data, stats_data, server_connected):
    clear()

    chain = chain_data.get("chain", [])
    stats = stats_data.get("stats", {})
    
    total_blocks = len(chain)
    total_tx = stats.get("total_tx", 0)
    fraud_count = stats.get("fraud_detected", 0)
    mempool = stats.get("mempool_size", 0)
    chain_valid = stats.get("chain_valid", True)
    uptime = stats.get("uptime", 0)

    # Calculate TPS
    if uptime > 0:
        tps = total_tx / uptime
    else:
        tps = 0.0

    latest_block = chain[-1] if chain else {}
    latest_hash = latest_block.get("hash", "N/A")
    latest_prev = latest_block.get("previous_hash", "N/A")
    latest_nonce = latest_block.get("nonce", 0)
    latest_merkle = latest_block.get("merkle_root", "N/A")
    latest_txs = len(latest_block.get("transactions", []))

    # Health indicator
    if chain_valid and server_connected:
        health = f"{Fore.GREEN}{Style.BRIGHT}● HEALTHY{Style.RESET_ALL}"
        health_bar = f"{Back.GREEN}{Fore.BLACK}{Style.BRIGHT}  SYSTEM OPERATIONAL  {Style.RESET_ALL}"
    else:
        health = f"{Fore.RED}{Style.BRIGHT}● DEGRADED{Style.RESET_ALL}"
        health_bar = f"{Back.RED}{Fore.WHITE}{Style.BRIGHT}  SYSTEM DEGRADED  {Style.RESET_ALL}"

    # Fraud rate
    fraud_rate = (fraud_count / total_tx * 100) if total_tx > 0 else 0

    print(f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════════════╗
║                    📊  BLOCKCHAIN LIVE DASHBOARD                     ║
║                    Local Permissioned Blockchain System               ║
╠══════════════════════════════════════════════════════════════════════╣
║                       {health_bar}                        ║
╠══════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}

{Fore.WHITE}{Style.BRIGHT}  ┌─────────────────── NETWORK STATS ───────────────────┐{Style.RESET_ALL}
  │                                                      │
  │  {Fore.YELLOW}System Health  :{Style.RESET_ALL}  {health}
  │  {Fore.YELLOW}Uptime         :{Style.RESET_ALL}  {format_uptime(uptime)}
  │  {Fore.YELLOW}Chain Valid     :{Style.RESET_ALL}  {'✅ Verified' if chain_valid else '❌ BROKEN'}
  │  {Fore.YELLOW}Server         :{Style.RESET_ALL}  {'🟢 Connected' if server_connected else '🔴 Disconnected'}
  │                                                      │
  {Fore.WHITE}{Style.BRIGHT}└──────────────────────────────────────────────────────┘{Style.RESET_ALL}

{Fore.WHITE}{Style.BRIGHT}  ┌─────────────── BLOCKCHAIN METRICS ──────────────────┐{Style.RESET_ALL}
  │                                                      │
  │  {Fore.CYAN}Block Height     :{Style.RESET_ALL}  {Fore.WHITE}{Style.BRIGHT}{total_blocks}{Style.RESET_ALL}
  │  {Fore.CYAN}Total Transactions:{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{total_tx}{Style.RESET_ALL}
  │  {Fore.CYAN}TPS (avg)        :{Style.RESET_ALL}  {Fore.WHITE}{Style.BRIGHT}{tps:.2f}{Style.RESET_ALL} tx/sec
  │  {Fore.CYAN}Mempool Pending  :{Style.RESET_ALL}  {Fore.YELLOW if mempool > 0 else Fore.GREEN}{mempool}{Style.RESET_ALL} transaction(s)
  │  {Fore.CYAN}Difficulty       :{Style.RESET_ALL}  {Fore.WHITE}2 leading zeros{Style.RESET_ALL}
  │  {Fore.CYAN}Hashing Algo     :{Style.RESET_ALL}  {Fore.WHITE}SHA-256{Style.RESET_ALL}
  │                                                      │
  {Fore.WHITE}{Style.BRIGHT}└──────────────────────────────────────────────────────┘{Style.RESET_ALL}

{Fore.WHITE}{Style.BRIGHT}  ┌──────────────── AI FRAUD DETECTION ─────────────────┐{Style.RESET_ALL}
  │                                                      │
  │  {Fore.CYAN}Fraud Alerts     :{Style.RESET_ALL}  {Fore.RED if fraud_count > 0 else Fore.GREEN}{Style.BRIGHT}{fraud_count}{Style.RESET_ALL}
  │  {Fore.CYAN}Fraud Rate       :{Style.RESET_ALL}  {Fore.RED if fraud_rate > 5 else Fore.GREEN}{fraud_rate:.2f}%{Style.RESET_ALL}
  │  {Fore.CYAN}Engine           :{Style.RESET_ALL}  {Fore.GREEN}Rule-Based + ML (RF + XGB){Style.RESET_ALL}
  │  {Fore.CYAN}Status           :{Style.RESET_ALL}  {Fore.GREEN}● Active{Style.RESET_ALL}
  │                                                      │
  {Fore.WHITE}{Style.BRIGHT}└──────────────────────────────────────────────────────┘{Style.RESET_ALL}

{Fore.WHITE}{Style.BRIGHT}  ┌──────────────── LATEST BLOCK ─────────────────────┐{Style.RESET_ALL}
  │                                                      │
  │  {Fore.YELLOW}Index        :{Style.RESET_ALL}  #{latest_block.get('index', 0)}
  │  {Fore.YELLOW}Hash         :{Style.RESET_ALL}  {Fore.WHITE}{Style.BRIGHT}{format_hash(latest_hash, 20)}{Style.RESET_ALL}
  │  {Fore.YELLOW}Prev Hash    :{Style.RESET_ALL}  {format_hash(latest_prev, 20)}
  │  {Fore.YELLOW}Merkle Root  :{Style.RESET_ALL}  {format_hash(latest_merkle, 20)}
  │  {Fore.YELLOW}Nonce        :{Style.RESET_ALL}  {latest_nonce}
  │  {Fore.YELLOW}Transactions :{Style.RESET_ALL}  {latest_txs} tx(s)
  │                                                      │
  {Fore.WHITE}{Style.BRIGHT}└──────────────────────────────────────────────────────┘{Style.RESET_ALL}""")

    # Show recent blocks as a mini chain visualization
    if len(chain) > 1:
        print(f"\n{Fore.WHITE}{Style.BRIGHT}  ┌──────────────── CHAIN VISUALIZATION ─────────────────┐{Style.RESET_ALL}")
        # Show last 5 blocks
        recent = chain[-5:]
        for i, block in enumerate(recent):
            bh = block.get("hash", "")[:10]
            bi = block.get("index", 0)
            btx = len(block.get("transactions", []))
            if i == len(recent) - 1:
                print(f"  │  {Fore.GREEN}{Style.BRIGHT}[Block #{bi}]{Style.RESET_ALL} {bh}... ({btx} tx)  ← {Fore.GREEN}{Style.BRIGHT}LATEST{Style.RESET_ALL}")
            else:
                print(f"  │  {Fore.CYAN}[Block #{bi}]{Style.RESET_ALL} {bh}... ({btx} tx)")
            if i < len(recent) - 1:
                print(f"  │      ↓")
        print(f"  {Fore.WHITE}{Style.BRIGHT}└──────────────────────────────────────────────────────┘{Style.RESET_ALL}")

    print(f"\n{Fore.WHITE}{Style.DIM}  Auto-refreshing every 5 seconds... Press Ctrl+C to exit.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{Style.DIM}  Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")


async def dashboard_loop():
    uri = "ws://localhost:8765"
    retry_count = 0
    max_retries = 10

    while retry_count < max_retries:
        try:
            async with websockets.connect(uri) as websocket:
                retry_count = 0  # Reset on successful connection

                # Wait for welcome
                welcome = await websocket.recv()

                while True:
                    # Request chain data
                    await websocket.send(json.dumps({"type": "GET_CHAIN"}))
                    chain_msg = await websocket.recv()
                    chain_data = json.loads(chain_msg)

                    # Request stats
                    await websocket.send(json.dumps({"type": "GET_STATS"}))
                    stats_msg = await websocket.recv()
                    stats_data = json.loads(stats_msg)

                    # Handle any broadcast messages that arrive between requests
                    if stats_data.get("type") != "STATS_DATA":
                        # Got a broadcast instead, try again
                        await websocket.send(json.dumps({"type": "GET_STATS"}))
                        stats_msg = await websocket.recv()
                        stats_data = json.loads(stats_msg)

                    draw_dashboard(chain_data, stats_data, True)
                    await asyncio.sleep(5)

        except ConnectionRefusedError:
            retry_count += 1
            clear()
            print(f"""
{Fore.YELLOW}{Style.BRIGHT}╔══════════════════════════════════════════════════════╗
║  ⏳  Waiting for server...  (Attempt {retry_count}/{max_retries})          ║
║  Server: ws://localhost:8765                         ║
║  Retrying in 3 seconds...                            ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}""")
            await asyncio.sleep(3)

        except websockets.exceptions.ConnectionClosed:
            retry_count += 1
            print(f"\n{Fore.YELLOW}🔌 Connection lost. Reconnecting... ({retry_count}/{max_retries}){Style.RESET_ALL}")
            await asyncio.sleep(3)

        except Exception as e:
            retry_count += 1
            await asyncio.sleep(3)

    print(f"""
{Fore.RED}{Style.BRIGHT}╔══════════════════════════════════════════════════════╗
║  ❌  Could not connect to server after {max_retries} attempts.  ║
║  Please ensure python server.py is running.          ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}""")


if __name__ == "__main__":
    try:
        asyncio.run(dashboard_loop())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Dashboard closed.{Style.RESET_ALL}")
        sys.exit(0)
