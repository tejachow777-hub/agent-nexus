import os
import random
import time
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = "https://data-seed-prebsc-1-s1.bnbchain.org:8545"
CHAIN_ID = 97
VAULT = "0x547cdf0267f8d0ac238923531CBBAa7dF697CBEB"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

ABI = [
    {"inputs": [], "name": "createTask", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"name": "_taskId", "type": "uint256"}], "name": "acceptTask", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"name": "_taskId", "type": "uint256"}], "name": "releaseFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "_taskId", "type": "uint256"}, {"name": "_reason", "type": "string"}], "name": "triggerFirewall", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "taskCounter", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]
vault = w3.eth.contract(address=Web3.to_checksum_address(VAULT), abi=ABI)

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
    return w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(raw))

REASONS = [
    "AUTO-AUDIT: slippage breach on OTC route",
    "AUTO-AUDIT: unauthorized token approval detected",
    "AUTO-AUDIT: counterparty not in whitelist",
    "AUTO-AUDIT: yield anomaly beyond statistical ceiling",
]

TASKS = 12
print(f"🌊 AGENTNEXUS TRAFFIC SIMULATOR — firing {TASKS} live tasks at BSC Testnet")
print("Keep the war room open. Watch it work.\n")

clean, slashed = 0, 0
for i in range(TASKS):
    send(vault.functions.createTask(), w3.to_wei(0.002, "ether"))
    tid = vault.functions.taskCounter().call()
    send(vault.functions.acceptTask(tid), w3.to_wei(0.001, "ether"))

    if random.random() < 0.7:
        send(vault.functions.releaseFunds(tid))
        clean += 1
        print(f"✅ Task #{tid} settled cleanly — reward released")
    else:
        reason = random.choice(REASONS)
        send(vault.functions.triggerFirewall(tid, reason))
        slashed += 1
        print(f"🔥 Task #{tid} SLASHED — {reason}")
    time.sleep(0.6)

print(f"\n🌊 BURST COMPLETE — {clean} settled, {slashed} slashed. The war room remembers everything.")