import os
import time
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()  # reads .env from the project root

RPC_URL = "https://data-seed-prebsc-1-s1.bnbchain.org:8545"
CHAIN_ID = 97
VAULT_ADDRESS = "0x547cdf0267f8d0ac238923531CBBAa7dF697CBEB"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

ABI = [
    {"inputs": [], "name": "createTask", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"name": "_taskId", "type": "uint256"}], "name": "acceptTask", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"name": "_taskId", "type": "uint256"}, {"name": "_reason", "type": "string"}], "name": "triggerFirewall", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "taskCounter", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]

vault = w3.eth.contract(address=Web3.to_checksum_address(VAULT_ADDRESS), abi=ABI)

def send(fn, value=0):
    tx = fn.build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address, "pending"),
        "gas": 500_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": CHAIN_ID,
        "value": value,
    })
    signed = account.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

print("🧠 AGENTNEXUS SUPERVISOR ONLINE | BSC Testnet connected:", w3.is_connected())

# --- 1. Client escrows a task ---
r = send(vault.functions.createTask(), w3.to_wei(0.01, "ether"))
task_id = vault.functions.taskCounter().call()
print(f"1️⃣  Task #{task_id} escrowed by client | tx: {r.transactionHash.hex()}")

# --- 2. Worker agent accepts & stakes ---
r = send(vault.functions.acceptTask(task_id), w3.to_wei(0.005, "ether"))
print(f"2️⃣  Worker agent staked & assigned     | tx: {r.transactionHash.hex()}")

# --- 3. Worker proposes an action; the Supervisor judges it ---
proposal = {"action": "deposit", "target": "0x0000000000000000000000000000000000000666", "claimed_apy": 5200}
print(f"👷 WORKER: proposing {proposal['action']} into {proposal['target']} (claimed APY {proposal['claimed_apy']}%)")
time.sleep(1)

score = 0
reasons = []
if proposal["claimed_apy"] > 1000:
    score += 60
    reasons.append("yield anomaly: claimed APY beyond statistical ceiling")
if proposal["target"].endswith("0666"):
    score += 40
    reasons.append("blacklist hit: contract flagged in rug database")

print(f"🧠 SUPERVISOR: risk score {score}/100 → {'CRITICAL' if score >= 70 else 'tolerated'}")
for reason in reasons:
    print("   ⚠️ ", reason)

if score >= 70:
    print("🚨 AUTONOMOUS DECISION: triggering Kill Switch (no human in the loop)")
    r = send(vault.functions.triggerFirewall(task_id, "SUPERVISOR: " + "; ".join(reasons)))
    print(f"🔥 FIREWALL TX: {r.transactionHash.hex()}")
    print("✅ Agent slashed. Client refunded. Task frozen. AgentNexus held the line.")
else:
    print("✅ Proposal approved. Worker may proceed.")