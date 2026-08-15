// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentNexusVault
 * @notice The institutional clearinghouse and firewall for ERC-8004 AI Agents on BSC.
 *         Handles task escrow, agent staking, and the deterministic "Kill Switch".
 */
contract AgentNexusVault {
    // --- STATE VARIABLES ---
    address public immutable protocolOwner;

    struct Task {
        address client;
        uint256 rewardAmount;
        address assignedAgent;
        uint256 agentStake;
        bool isActive;
        bool isCompleted;
    }

    mapping(uint256 => Task) public tasks;
    uint256 public taskCounter;

    // --- EVENTS (Our frontend dashboard will listen to these) ---
    event TaskCreated(uint256 indexed taskId, address indexed client, uint256 reward);
    event AgentAssigned(uint256 indexed taskId, address indexed agent, uint256 stakeLocked);
    event TaskCompleted(uint256 indexed taskId, address indexed agent, uint256 rewardPaid);
    event FirewallTriggered(uint256 indexed taskId, address indexed rogueAgent, uint256 slashedAmount, string reason);

    // --- MODIFIERS ---
    modifier onlyClient(uint256 _taskId) {
        require(tasks[_taskId].client == msg.sender, "AgentNexus: Not the task client");
        _;
    }

    modifier onlyActiveTask(uint256 _taskId) {
        require(tasks[_taskId].isActive, "AgentNexus: Task not active");
        _;
    }

    constructor() {
        protocolOwner = msg.sender;
    }

    // --- CORE FUNCTIONS ---

    /// @notice Client deposits BNB to escrow a task for the AI Swarm.
    function createTask() external payable returns (uint256) {
        require(msg.value > 0, "AgentNexus: Must escrow funds");

        taskCounter++;
        tasks[taskCounter] = Task({
            client: msg.sender,
            rewardAmount: msg.value,
            assignedAgent: address(0),
            agentStake: 0,
            isActive: true,
            isCompleted: false
        });

        emit TaskCreated(taskCounter, msg.sender, msg.value);
        return taskCounter;
    }

    /// @notice An ERC-8004 Agent stakes BNB to accept the task (skin in the game).
    function acceptTask(uint256 _taskId) external payable onlyActiveTask(_taskId) {
        Task storage task = tasks[_taskId];
        require(task.assignedAgent == address(0), "AgentNexus: Task already assigned");

        uint256 requiredStake = task.rewardAmount / 2;
        require(msg.value >= requiredStake, "AgentNexus: Insufficient agent stake");

        task.assignedAgent = msg.sender;
        task.agentStake = msg.value;

        emit AgentAssigned(_taskId, msg.sender, msg.value);
    }

    /// @notice Happy Path: Client verifies the AI output and releases funds.
    function releaseFunds(uint256 _taskId) external onlyClient(_taskId) onlyActiveTask(_taskId) {
        Task storage task = tasks[_taskId];
        require(!task.isCompleted, "AgentNexus: Already completed");

        task.isCompleted = true;
        task.isActive = false;

        uint256 totalPayout = task.rewardAmount + task.agentStake;

        (bool success, ) = payable(task.assignedAgent).call{value: totalPayout}("");
        require(success, "AgentNexus: Payout transfer failed");

        emit TaskCompleted(_taskId, task.assignedAgent, totalPayout);
    }

    /// @notice THE KILL SWITCH. Triggered when the off-chain AgentNexus Supervisor
    ///         detects a malicious or hallucinated agent transaction.
    function triggerFirewall(uint256 _taskId, string calldata _reason)
        external
        onlyClient(_taskId)
        onlyActiveTask(_taskId)
    {
        Task storage task = tasks[_taskId];
        require(!task.isCompleted, "AgentNexus: Already completed");

        address rogueAgent = task.assignedAgent;
        uint256 slashedStake = task.agentStake;
        uint256 clientRefund = task.rewardAmount;

        task.isActive = false;
        task.isCompleted = true;
        task.agentStake = 0;

        (bool refundSuccess, ) = payable(task.client).call{value: clientRefund}("");
        require(refundSuccess, "AgentNexus: Client refund failed");

        (bool slashSuccess, ) = payable(protocolOwner).call{value: slashedStake}("");
        require(slashSuccess, "AgentNexus: Stake slashing failed");

        emit FirewallTriggered(_taskId, rogueAgent, slashedStake, _reason);
    }
}