# AgentNexus
**The institutional risk & clearing layer for ERC-8004 AI agents on BNB Smart Chain.**

> HUMI tells institutions which agents to trust. AgentNexus guarantees that even when trust fails, capital survives.

## The Problem
Autonomous AI agents now hold real capital — but a single hallucination, rogue transaction, or rug-pull interaction drains a treasury in one block. Institutions will not deploy agents at scale without **deterministic, on-chain risk enforcement**.

## The Solution: Three-Layer Defense
1. **Reputation Gate (HUMI-style)** — agents scoring below 60/100 never touch capital.
2. **LLM Behavior Monitor** — every proposed transaction is reasoned over by an autonomous AI supervisor (Llama 3.3 70B via Groq). No human in the loop.
3. **On-Chain Kill Switch** — a verified smart contract slashes the rogue agent's stake and refunds the client in a single transaction.

## Live on BSC Testnet (source verified ✅)
| Artifact | Link |
|---|---|
| AgentNexusVault (verified source) | https://testnet.bscscan.com/address/0x547cdf0267f8d0ac238923531CBBAa7dF697CBEB#code |
| Autonomous LLM slash — AI reasoning stored on-chain | https://testnet.bscscan.com/tx/0x6d2b13d766e8ee4cdb921b6d54464106ae3f87702a0a959989c7727a80029796 |
| Three-layer defense run | https://testnet.bscscan.com/tx/0x888532bcb5833f8554e7f0fd1876c579deeeaab48592d11dba893edb11303ddc1 |

## Architecture
- `contracts/AgentNexusVault.sol` — task escrow, agent staking, firewall (Hardhat + test suite)
- `backend/supervisor.py` — autonomous supervisor: HUMI gate → LLM monitor → on-chain enforcement (Python, web3.py, Groq)
- `frontend/index.html` — live war-room terminal streaming contract events in real time

## Ecosystem Integration
Designed to consume **Global Score Agent** HUMI/WAMI indices as the reputation layer (mock feed for the demo; production API post-hackathon). Reputation measures trust — AgentNexus enforces it.

## Run It Locally
```bash
npm install
npx hardhat test                 # 5 passing: slashing, refunds, access control
npx hardhat run scripts/deploy.js --network bscTestnet
python -m pip install web3 python-dotenv openai
python backend/supervisor.py     # watch the 3-layer defense fire live
# open frontend/index.html for the war-room dashboard
```

## Roadmap
- Real GSA reputation API integration
- Scenario modules: OTC slippage guard, multi-validator audit consensus
- Mainnet deployment via BNB Agent Studio gas sponsorship

*Built for the BNB AI Agents Hackathon — Sept 2026.*
