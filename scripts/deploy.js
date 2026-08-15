const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("🚀 Launching AgentNexus with account:", deployer.address);

  const Vault = await hre.ethers.getContractFactory("AgentNexusVault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();

  console.log("✅ AgentNexusVault is LIVE at:", await vault.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});