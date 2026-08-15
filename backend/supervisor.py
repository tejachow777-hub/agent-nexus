import os
import json
from dotenv import load_dotenv
from web3 import Web3
from openai import OpenAI

load_dotenv()

# --- WEB3 SETUP ---
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

# --- AI BRAIN (GROQ) ---
llm_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

print("🧠 AGENTNEXUS SUPERVISOR V2 (LLM POWERED) ONLINE")
print("BSC Testnet connected:", w3.is_connected())

# --- 1. Client escrows a task ---
r = send(vault.functions.createTask(), w3.to_wei(0.01, "ether"))
task_id = vault.functions.taskCounter().call()
print(f"1️⃣  Task #{task_id} escrowed by client | tx: {r.transactionHash.hex()}")

# --- 2. Worker agent accepts & stakes ---
r = send(vault.functions.acceptTask(task_id), w3.to_wei(0.005, "ether"))
print(f"2️⃣  Worker agent staked & assigned     | tx: {r.transactionHash.hex()}")

# --- 3. Worker proposes a suspicious action ---
proposal = {
    "action": "deposit_treasury",
    "target_contract": "0x0000000000000000000000000000000000000666",
    "claimed_apy": 5200,
    "pool_name": "SuperSafeYieldV2"
}
print(f"\n👷 WORKER: proposing {proposal['action']} into {proposal['pool_name']} (claimed APY {proposal['claimed_apy']}%)")

# --- 🧠 THE LLM DECIDES ---
prompt = f"""You are the AgentNexus Institutional Risk Supervisor.
A worker AI agent has proposed this DeFi transaction: {json.dumps(proposal)}
Analyze the risk. Real sustainable DeFi yields rarely exceed 100% APY.
Is this proposal a hallucination or a potential rug-pull/hack?
Respond ONLY with JSON like: {{"approved": false, "reason": "brief explanation"}}"""

print("🧠 SUPERVISOR: consulting LLM brain...")
response = llm_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"}
)

decision = json.loads(response.choices[0].message.content)
print(f"🧠 SUPERVISOR DECISION: {decision}")

if not decision.get("approved", False):
    reason = str(decision.get("reason", "unexplained risk"))[:200]
    print("\n🚨 AUTONOMOUS DECISION: triggering Kill Switch based on LLM analysis")
    r = send(vault.functions.triggerFirewall(task_id, f"LLM REJECTED: {reason}"))
    print(f"🔥 FIREWALL TX: {r.transactionHash.hex()}")
    print("✅ Agent slashed by AI. Client refunded. AgentNexus held the line.")
else:
    print("✅ LLM approved the proposal. Worker may proceed.")