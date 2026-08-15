const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentNexusVault", function () {
  let vault, owner, client, agent;
  const TASK_REWARD = ethers.parseEther("1");    // 1 BNB reward
  const AGENT_STAKE = ethers.parseEther("0.5");  // 0.5 BNB stake (50%)

  beforeEach(async function () {
    [owner, client, agent] = await ethers.getSigners();
    const Vault = await ethers.getContractFactory("AgentNexusVault");
    vault = await Vault.deploy();
    await vault.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Sets the protocol owner", async function () {
      expect(await vault.protocolOwner()).to.equal(owner.address);
    });
  });

  describe("Task Lifecycle", function () {
    it("Client can create a task with escrowed funds", async function () {
      await vault.connect(client).createTask({ value: TASK_REWARD });
      const task = await vault.tasks(1);
      expect(task.client).to.equal(client.address);
      expect(task.rewardAmount).to.equal(TASK_REWARD);
      expect(task.isActive).to.equal(true);
    });

    it("Rejects an agent who stakes less than 50% of the reward", async function () {
      await vault.connect(client).createTask({ value: TASK_REWARD });
      await expect(
        vault.connect(agent).acceptTask(1, { value: ethers.parseEther("0.1") })
      ).to.be.revertedWith("AgentNexus: Insufficient agent stake");
    });
  });

  describe("THE KILL SWITCH (Firewall)", function () {
    beforeEach(async function () {
      await vault.connect(client).createTask({ value: TASK_REWARD });
      await vault.connect(agent).acceptTask(1, { value: AGENT_STAKE });
    });

    it("Slashes the rogue agent and refunds the client", async function () {
      const ownerBefore = await ethers.provider.getBalance(owner.address);
      const clientBefore = await ethers.provider.getBalance(client.address);

      const tx = await vault
        .connect(client)
        .triggerFirewall(1, "ROGUE TX DETECTED: unauthorized contract call");
      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed * receipt.gasPrice;

      const ownerAfter = await ethers.provider.getBalance(owner.address);
      const clientAfter = await ethers.provider.getBalance(client.address);

      // Treasury receives the slashed agent stake
      expect(ownerAfter - ownerBefore).to.equal(AGENT_STAKE);

      // Client receives the full escrow refund (minus their gas)
      expect(clientAfter).to.equal(clientBefore - gasCost + TASK_REWARD);

      // Task is permanently frozen
      const task = await vault.tasks(1);
      expect(task.isActive).to.equal(false);
      expect(task.isCompleted).to.equal(true);
    });

    it("Blocks anyone except the client from triggering the Firewall", async function () {
      await expect(
        vault.connect(agent).triggerFirewall(1, "hack attempt")
      ).to.be.revertedWith("AgentNexus: Not the task client");
    });
  });
});