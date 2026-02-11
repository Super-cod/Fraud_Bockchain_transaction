import asyncio
import json
import time
import logging
import websockets
from colorama import init, Fore, Back, Style
from blockchain import Blockchain, Transaction, Block
from fraud_engine import FraudDetectionEngine

init(autoreset=True)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Server")

# Initialize core components
blockchain = Blockchain()
fraud_engine = FraudDetectionEngine()

# Connected clients
connected = set()

# Stats
stats = {
    "total_tx": 0,
    "total_blocks": 1,  # genesis
    "fraud_detected": 0,
    "start_time": time.time()
}

def print_banner():
    print(f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║          🏗️  BLOCKCHAIN SERVER — NODE ACTIVE                ║
║          SHA-256 Proof-of-Work Consensus Engine              ║
╠══════════════════════════════════════════════════════════════╣
║  Protocol  : WebSocket (ws://localhost:8765)                 ║
║  Hashing   : SHA-256                                         ║
║  Difficulty : {blockchain.difficulty} leading zeros                                 ║
║  Mining     : Auto every 10 seconds                          ║
║  Fraud AI   : {'ACTIVE' if fraud_engine.models_loaded else 'RULES ONLY'}                                     ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

def print_tx_received(tx, analysis):
    risk_color = Fore.GREEN if analysis.risk_level == "LOW" else (Fore.YELLOW if analysis.risk_level == "MEDIUM" else Fore.RED)
    print(f"""
{Fore.WHITE}{Style.BRIGHT}┌─────────────── 📨 TRANSACTION RECEIVED ───────────────┐{Style.RESET_ALL}
│  {Fore.CYAN}TX Hash  :{Style.RESET_ALL} {tx.id[:16]}...{tx.id[-8:]}
│  {Fore.CYAN}Sender   :{Style.RESET_ALL} {tx.sender}
│  {Fore.CYAN}Receiver :{Style.RESET_ALL} {tx.receiver}
│  {Fore.CYAN}Amount   :{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}${tx.amount:,.2f}{Style.RESET_ALL}
│  {Fore.CYAN}Type     :{Style.RESET_ALL} {tx.type}
│  {Fore.CYAN}Time     :{Style.RESET_ALL} {time.strftime('%H:%M:%S', time.localtime(tx.timestamp))}
│  ────────── 🔍 FRAUD ANALYSIS (SHA-256 Verified) ──────────
│  {Fore.CYAN}Score    :{Style.RESET_ALL} {risk_color}{analysis.score}/100{Style.RESET_ALL}
│  {Fore.CYAN}Risk     :{Style.RESET_ALL} {risk_color}{Style.BRIGHT}{analysis.risk_level}{Style.RESET_ALL}
│  {Fore.CYAN}Decision :{Style.RESET_ALL} {risk_color}{analysis.decision}{Style.RESET_ALL}
│  {Fore.CYAN}Details  :{Style.RESET_ALL} {'; '.join(analysis.details) if analysis.details else 'No anomalies'}
{Fore.WHITE}{Style.BRIGHT}└───────────────────────────────────────────────────────┘{Style.RESET_ALL}""")

def print_block_mined(block):
    print(f"""
{Fore.GREEN}{Style.BRIGHT}╔═══════════════════ ⛏️  BLOCK MINED ═══════════════════╗{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Index         :{Style.RESET_ALL} #{block.index}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Hash          :{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{block.hash}{Style.RESET_ALL}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Previous Hash :{Style.RESET_ALL} {block.previous_hash[:32]}...
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Merkle Root   :{Style.RESET_ALL} {block.merkle_root[:32]}...
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Nonce         :{Style.RESET_ALL} {block.nonce}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Transactions  :{Style.RESET_ALL} {len(block.transactions)} tx(s)
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Timestamp     :{Style.RESET_ALL} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))}
{Fore.GREEN}║{Style.RESET_ALL}  {Fore.YELLOW}Chain Valid   :{Style.RESET_ALL} {'✅ YES' if blockchain.is_chain_valid() else '❌ NO'}
{Fore.GREEN}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}""")




async def broadcast(message):
    """Broadcast message to all connected clients, removing dead connections."""
    if not connected:
        return
    
    dead_connections = set()
    for ws in connected:
        try:
            await ws.send(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")
            dead_connections.add(ws)
    
    # Remove dead connections
    for ws in dead_connections:
        connected.discard(ws)


async def handle_transaction(websocket, data):
    try:
        tx_data = data.get("transaction")
        if not tx_data:
            return

        sender = tx_data.get("sender")
        receiver = tx_data.get("receiver")
        amount = float(tx_data.get("amount", 0))
        tx_type = tx_data.get("type", "PAYMENT")
        timestamp = tx_data.get("timestamp", time.time())

        tx = Transaction(sender, receiver, amount, tx_type, timestamp)

        # Fraud Analysis
        analysis_result = fraud_engine.evaluate_transaction(tx_data)
        tx.fraud_analysis = {
            "score": analysis_result.score,
            "risk_level": analysis_result.risk_level,
            "decision": analysis_result.decision,
            "details": analysis_result.details
        }

        # Beautiful print
        print_tx_received(tx, analysis_result)

        stats["total_tx"] += 1
        if analysis_result.risk_level == "HIGH":
            stats["fraud_detected"] += 1

        # Add to Mempool
        blockchain.mempool.append(tx)

        # Notify Clients
        try:
            await broadcast({
                "type": "NEW_TRANSACTION",
                "transaction": tx.to_dict()
            })
        except Exception as broadcast_error:
            logger.warning(f"Broadcast failed (client may have disconnected): {broadcast_error}")

    except Exception as e:
        logger.error(f"Error handling transaction: {e}", exc_info=True)
        # Send error response to client if possible
        try:
            await websocket.send(json.dumps({
                "type": "ERROR",
                "message": f"Transaction processing failed: {str(e)}"
            }))
        except:
            pass  # Client already disconnected

async def mine_blocks():
    while True:
        await asyncio.sleep(10)
        if blockchain.mempool:
            new_block = blockchain.mine_pending_transactions(miner_address="SYSTEM_MINER")
            if new_block:
                stats["total_blocks"] += 1
                print_block_mined(new_block)
                try:
                    await broadcast({
                        "type": "NEW_BLOCK",
                        "block": {
                            "index": new_block.index,
                            "timestamp": new_block.timestamp,
                            "transactions": new_block.transactions,
                            "hash": new_block.hash,
                            "previous_hash": new_block.previous_hash,
                            "nonce": new_block.nonce,
                            "merkle_root": new_block.merkle_root
                        }
                    })
                except Exception as e:
                    logger.warning(f"Block broadcast failed: {e}")

async def handler(websocket):
    connected.add(websocket)
    client_id = id(websocket)
    try:
        logger.info(f"Client {client_id} connected. Total clients: {len(connected)}")
        print(f"{Fore.GREEN}🔗 Client connected. Total clients: {len(connected)}{Style.RESET_ALL}")
        
        try:
            await websocket.send(json.dumps({
                "type": "WELCOME",
                "message": "Connected to Blockchain Server",
                "chain_height": len(blockchain.chain),
                "difficulty": blockchain.difficulty
            }))
        except Exception as e:
            logger.error(f"Failed to send welcome to client {client_id}: {e}")
            return

        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                logger.debug(f"Client {client_id} sent {msg_type}")

                if msg_type == "ADD_TRANSACTION":
                    await handle_transaction(websocket, data)
                elif msg_type == "GET_CHAIN":
                    try:
                        await websocket.send(json.dumps({
                            "type": "CHAIN_DATA",
                            "chain": blockchain.to_list(),
                            "stats": stats
                        }))
                    except Exception as e:
                        logger.error(f"Failed to send chain data: {e}")
                elif msg_type == "GET_STATS":
                    try:
                        await websocket.send(json.dumps({
                            "type": "STATS_DATA",
                            "stats": {
                                **stats,
                                "mempool_size": len(blockchain.mempool),
                                "chain_valid": blockchain.is_chain_valid(),
                                "uptime": time.time() - stats["start_time"]
                            }
                        }))
                    except Exception as e:
                        logger.error(f"Failed to send stats: {e}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from client {client_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {e}", exc_info=True)

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {client_id} disconnected normally")
        print(f"{Fore.YELLOW}🔌 Client disconnected. Remaining: {len(connected) - 1}{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Unexpected error with client {client_id}: {e}", exc_info=True)
        print(f"{Fore.RED}❌ Client {client_id} error: {e}{Style.RESET_ALL}")
    finally:
        connected.discard(websocket)
        logger.info(f"Client {client_id} cleaned up. Remaining: {len(connected)}")

async def main():
    print_banner()
    server = await websockets.serve(handler, "localhost", 8765)
    print(f"{Fore.GREEN}{Style.BRIGHT}🚀 Server listening on ws://localhost:8765{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   Waiting for connections...{Style.RESET_ALL}\n")
    asyncio.create_task(mine_blocks())
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Server stopped.{Style.RESET_ALL}")
