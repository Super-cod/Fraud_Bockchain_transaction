import asyncio
import websockets
import json
import random
import time
import os
from colorama import init, Fore, Back, Style

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(f"""
{Fore.MAGENTA}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║              📤  TRANSACTION SENDER TERMINAL                 ║
║              Local Permissioned Blockchain System            ║
╠══════════════════════════════════════════════════════════════╣
║  Mode     : Interactive CLI                                  ║
║  Hashing  : SHA-256                                          ║
║  Protocol : WebSocket (ws://localhost:8765)                   ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

def print_tx_sent(tx_data, index=None, total=None):
    batch_label = f" [{index}/{total}]" if index else ""
    amount = tx_data['amount']
    amount_color = Fore.RED if amount > 500000 else (Fore.YELLOW if amount > 100000 else Fore.GREEN)
    print(f"""
{Fore.WHITE}{Style.BRIGHT}┌──────────────── ✅ TRANSACTION SENT{batch_label} ────────────────┐{Style.RESET_ALL}
│  {Fore.CYAN}Sender   :{Style.RESET_ALL} {tx_data['sender']}
│  {Fore.CYAN}Receiver :{Style.RESET_ALL} {tx_data['receiver']}
│  {Fore.CYAN}Amount   :{Style.RESET_ALL} {amount_color}{Style.BRIGHT}${amount:,.2f}{Style.RESET_ALL}
│  {Fore.CYAN}Type     :{Style.RESET_ALL} {tx_data['type']}
│  {Fore.CYAN}Time     :{Style.RESET_ALL} {time.strftime('%H:%M:%S')}
{Fore.WHITE}{Style.BRIGHT}└───────────────────────────────────────────────────────┘{Style.RESET_ALL}""")

def print_menu():
    print(f"""
{Fore.CYAN}{Style.BRIGHT}┌─────────────────── MENU ───────────────────┐{Style.RESET_ALL}
│  {Fore.WHITE}[1]{Style.RESET_ALL} Send Manual Transaction               │
│  {Fore.WHITE}[2]{Style.RESET_ALL} Send Batch (Random Transactions)      │
│  {Fore.WHITE}[3]{Style.RESET_ALL} Send Fraud Test (High Amount)         │
│  {Fore.WHITE}[4]{Style.RESET_ALL} Send Rapid-Fire Stress Test           │
│  {Fore.WHITE}[q]{Style.RESET_ALL} Quit                                  │
{Fore.CYAN}{Style.BRIGHT}└────────────────────────────────────────────┘{Style.RESET_ALL}""")

async def sender_loop():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)

            clear()
            print_banner()
            print(f"{Fore.GREEN}{Style.BRIGHT}🔗 Connected to server!{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   Chain Height: {welcome_data.get('chain_height', '?')} | Difficulty: {welcome_data.get('difficulty', '?')}{Style.RESET_ALL}")

            while True:
                try:
                    print_menu()
                    choice = input(f"{Fore.YELLOW}  ▶ Choose option: {Style.RESET_ALL}")

                    if choice == "q":
                        print(f"\n{Fore.RED}👋 Disconnecting...{Style.RESET_ALL}")
                        break

                    elif choice == "1":
                        print(f"\n{Fore.CYAN}{Style.BRIGHT}── Manual Transaction ──{Style.RESET_ALL}")
                        sender = input(f"  {Fore.WHITE}Sender   : {Style.RESET_ALL}") or f"User_{random.randint(1000,9999)}"
                        receiver = input(f"  {Fore.WHITE}Receiver : {Style.RESET_ALL}") or f"User_{random.randint(1000,9999)}"
                        try:
                            amount = float(input(f"  {Fore.WHITE}Amount $ : {Style.RESET_ALL}") or "100")
                        except ValueError:
                            amount = 100.0
                        tx_type = input(f"  {Fore.WHITE}Type (PAYMENT/TRANSFER/CASH_OUT) : {Style.RESET_ALL}") or "PAYMENT"

                        tx_data = {
                            "sender": sender,
                            "receiver": receiver,
                            "amount": amount,
                            "type": tx_type.upper(),
                            "timestamp": time.time()
                        }
                        try:
                            await websocket.send(json.dumps({"type": "ADD_TRANSACTION", "transaction": tx_data}))
                            print_tx_sent(tx_data)
                        except websockets.exceptions.ConnectionClosed:
                            print(f"\n{Fore.RED}❌ Connection lost. Server may have crashed.{Style.RESET_ALL}")
                            return

                    elif choice == "2":
                        try:
                            count = int(input(f"  {Fore.WHITE}How many transactions? : {Style.RESET_ALL}") or "5")
                            delay = float(input(f"  {Fore.WHITE}Delay between (sec)? : {Style.RESET_ALL}") or "0.5")
                        except ValueError:
                            count, delay = 5, 0.5

                        print(f"\n{Fore.YELLOW}{Style.BRIGHT}🚀 Sending {count} random transactions...{Style.RESET_ALL}")
                        for i in range(count):
                            tx_data = {
                                "sender": f"C{random.randint(100000000, 999999999)}",
                                "receiver": f"C{random.randint(100000000, 999999999)}",
                                "amount": round(random.uniform(50, 50000), 2),
                                "type": random.choice(["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN"]),
                                "timestamp": time.time()
                            }
                            try:
                                await websocket.send(json.dumps({"type": "ADD_TRANSACTION", "transaction": tx_data}))
                                print_tx_sent(tx_data, i + 1, count)
                                await asyncio.sleep(delay)
                            except websockets.exceptions.ConnectionClosed:
                                print(f"\n{Fore.RED}❌ Connection lost after {i+1} transactions.{Style.RESET_ALL}")
                                return

                        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Batch complete!{Style.RESET_ALL}")

                    elif choice == "3":
                        print(f"\n{Fore.RED}{Style.BRIGHT}⚠️  FRAUD SIMULATION MODE{Style.RESET_ALL}")
                        fraud_scenarios = [
                            {"sender": "C999999999", "receiver": "C000000001", "amount": 9500000.0, "type": "TRANSFER"},
                            {"sender": "C111111111", "receiver": "C222222222", "amount": 750000.0, "type": "CASH_OUT"},
                            {"sender": "M888888888", "receiver": "C333333333", "amount": 50000.0, "type": "PAYMENT"},
                            {"sender": "C444444444", "receiver": "C555555555", "amount": -500.0, "type": "PAYMENT"},
                            {"sender": "C666666666", "receiver": "C777777777", "amount": 10000000.0, "type": "TRANSFER"},
                        ]
                        for i, scenario in enumerate(fraud_scenarios):
                            scenario["timestamp"] = time.time()
                            try:
                                await websocket.send(json.dumps({"type": "ADD_TRANSACTION", "transaction": scenario}))
                                print_tx_sent(scenario, i + 1, len(fraud_scenarios))
                                await asyncio.sleep(0.3)
                            except websockets.exceptions.ConnectionClosed:
                                print(f"\n{Fore.RED}❌ Connection lost during fraud test.{Style.RESET_ALL}")
                                return

                        print(f"\n{Fore.RED}{Style.BRIGHT}🚨 Fraud test complete!{Style.RESET_ALL}")

                    elif choice == "4":
                        try:
                            count = int(input(f"  {Fore.WHITE}How many? : {Style.RESET_ALL}") or "20")
                        except ValueError:
                            count = 20
                        print(f"\n{Fore.YELLOW}{Style.BRIGHT}⚡ STRESS TEST: {count} transactions...{Style.RESET_ALL}")
                        for i in range(count):
                            tx_data = {
                                "sender": f"C{random.randint(100000000, 999999999)}",
                                "receiver": f"C{random.randint(100000000, 999999999)}",
                                "amount": round(random.uniform(10, 100000), 2),
                                "type": random.choice(["PAYMENT", "TRANSFER", "CASH_OUT"]),
                                "timestamp": time.time()
                            }
                            try:
                                await websocket.send(json.dumps({"type": "ADD_TRANSACTION", "transaction": tx_data}))
                                print(f"  {Fore.GREEN}⚡ [{i+1}/{count}]{Style.RESET_ALL} ${tx_data['amount']:,.2f}")
                            except websockets.exceptions.ConnectionClosed:
                                print(f"\n{Fore.RED}❌ Connection lost.{Style.RESET_ALL}")
                                return
                        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Stress test complete!{Style.RESET_ALL}")

                    else:
                        print(f"{Fore.RED}  ❌ Invalid option.{Style.RESET_ALL}")

                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Interrupted.{Style.RESET_ALL}")
                    break

    except ConnectionRefusedError:
        print(f"""
{Fore.RED}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║  ❌  CONNECTION FAILED                       ║
║  Server not running on ws://localhost:8765   ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}""")
    except websockets.exceptions.ConnectionClosed:
        print(f"\n{Fore.RED}🔌 Server disconnected.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        asyncio.run(sender_loop())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Terminated.{Style.RESET_ALL}")
