# @version 0.2.8
# @notice A manager contract for the StakingRewards contract.
# @author skozin
# @license MIT
from vyper.interfaces import ERC20


interface StakingRewards:
    def periodFinish() -> uint256: view
    def notifyRewardAmount(reward: uint256, rewardHolder: address): nonpayable


owner: public(address)
rewards_contract: public(address)
reward_amount: public(uint256)


@external
def __init__():
    self.owner = msg.sender


@external
def transfer_ownership(_to: address):
    """
    @notice Changes the contract owner. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "not permitted"
    assert _to != ZERO_ADDRESS, "zero owner"
    self.owner = _to


@external
def set_rewards_contract(_rewards_contract: address):
    """
    @notice Sets the StakingRewards contract. Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"
    assert _rewards_contract != ZERO_ADDRESS, "zero rewards contract"
    self.rewards_contract = _rewards_contract


@external
def set_reward_amount(_reward_amount: uint256):
    """
    @notice
        Sets the amount of reward tokens that is to be distributed throughout
        the next rewards period. Setting this to 0 disables rewards distribution.
        Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"
    self.reward_amount = _reward_amount


@view
@internal
def _is_rewards_period_finished(rewards_contract: address) -> bool:
    return block.timestamp >= StakingRewards(rewards_contract).periodFinish()


@view
@external
def is_rewards_period_finished() -> bool:
    """
    @notice Whether the current rewards period has finished.
    """
    return self._is_rewards_period_finished(self.rewards_contract)


@external
def start_next_rewards_period():
    """
    @notice
        Starts the next rewards period of duration `rewards_contract.rewardsDuration()`,
        distributing `self.reward_amount()` tokens throughout the period.
    """
    rewards: address = self.rewards_contract
    amount: uint256 = self.reward_amount

    assert rewards != ZERO_ADDRESS and amount != 0, "manager: rewards disabled"
    assert self._is_rewards_period_finished(rewards), "manager: rewards period not finished"

    StakingRewards(rewards).notifyRewardAmount(amount, self.owner)
