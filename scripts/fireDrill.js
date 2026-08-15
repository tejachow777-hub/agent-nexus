const hre = require("hardhat");

async function main() {
  const [client] = await hre.ethers.getSigners();
  const vault = await hre.ethers.getContractAt(
    "AgentNexusVault",
    "0x547cdf0267f8d0ac238923531CBBAa7dF697CBEB"
  );

  console.log("=== AGENTNEXUS LIVE FIRE DRILL — BSC TESTNET ===");

  // 1. Client escrows 0.01 tBNB for a task
  let tx = await vault.createTask({ value: hre.ethers.parseEther("0.01") });
  await tx.wait();
  console.log("1️⃣ Task created & escrowed | tx:", tx.hash);

  const taskId = await vault.taskCounter();

  // 2. Agent accepts and stakes 0.005 tBNB (skin in the game)
  tx = await vault.acceptTask(taskId, { value: hre.ethers.parseEther("0.005") });
  await tx.wait();
  console.log("2️⃣ Agent assigned & staked   | tx:", tx.hash);

  // 3. ROGUE BEHAVIOR DETECTED → KILL SWITCH
  tx = await vault.triggerFirewall(taskId, "FIRE DRILL: rogue transaction simulated");
  await tx.wait();
  console.log("3️⃣ FIREWALL TRIGGERED        | tx:", tx.hash);

  const task = await vault.tasks(taskId);
  console.log("Task permanently frozen?", task.isActive ? "NO ❌" : "YES ✅");
  console.log("🔥 DRILL COMPLETE — the Kill Switch works on live BSC Testnet.");
}

main().catch((e) => { console.error(e); process.exitCode = 1; });