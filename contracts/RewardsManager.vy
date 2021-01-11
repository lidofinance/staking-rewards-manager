# @version 0.2.8
# @notice A manager contract for the StakingRewards contract.
# @author skozin
# @license MIT
from vyper.interfaces import ERC20


interface StakingRewards:
    def owner() -> address: view
    def rewardsDistribution() -> address: view
    def rewardsDuration() -> uint256: view
    def periodFinish() -> uint256: view
    def notifyRewardAmount(reward: uint256): nonpayable
    def setRewardsDuration(_rewardsDuration: uint256): nonpayable
    def setRewardsDistribution(_rewardsDistribution: address): nonpayable
    def nominateNewOwner(_owner: address): nonpayable
    def acceptOwnership(): nonpayable


owner: public(address)
rewards_token: public(address)
rewards_contract: public(address)
rewards_duration: public(uint256)
rewards_per_duration: public(uint256)


@external
def __init__(_rewards_token: address, _owner: address):
    assert _rewards_token != ZERO_ADDRESS, "zero rewards token"
    assert _owner != ZERO_ADDRESS, "zero owner"
    self.owner = _owner
    self.rewards_token = _rewards_token


@external
def transfer_ownership(_new_owner: address):
    """
    @notice
        Sets new manager contract owner — the address that's allowed to configure rewards
        period duration, amount and contract, and to interrupt the current rewards period.
        Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "not permitted"
    assert _new_owner != ZERO_ADDRESS, "zero owner"
    self.owner = _new_owner


@external
def configure(
    _rewards_per_duration: uint256,
    _rewards_duration: uint256 = 0,
    _rewards_contract: address = ZERO_ADDRESS
):
    """
    @notice
        Configures the next rewards period (duration and amount), allowing to
        set the new rewards contract as well. Can only be called by the owner.

    @param _rewards_per_duration
        How much tokens to distribute throughout the next rewards period.

    @param _rewards_duration
        The length of the next rewards period. Pass zero (the default value) to keep the same.

    @param _rewards_contract
        The address of the rewards contract. Pass zero (the default value) to keep the same.
    """
    assert msg.sender == self.owner, "not permitted"
    assert _rewards_contract != ZERO_ADDRESS, "zero rewards contract"

    self.rewards_per_duration = _rewards_per_duration

    if _rewards_duration != 0:
        self.rewards_duration = _rewards_duration

    if _rewards_contract != ZERO_ADDRESS and _rewards_contract != self.rewards_contract:
        assert StakingRewards(_rewards_contract).rewardsDistribution() == self, (
            "manager is not rewards distr")
        if StakingRewards(_rewards_contract).owner() != self:
            # will fail unless self is a nominated owner
            StakingRewards(_rewards_contract).acceptOwnership()
        self.rewards_contract = _rewards_contract


@internal
def _recover_erc20(_token: address, _recipient: address):
    token_balance: uint256 = ERC20(_token).balanceOf(self)
    if token_balance != 0:
        assert ERC20(_token).transfer(_recipient, token_balance), "token transfer failed"


@external
def recover_erc20(_token: address, _recipient: address = msg.sender):
    """
    @notice
        Transfers the whole balance of the given ERC20 token from self
        to the recipient. Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"
    self._recover_erc20(_token, _recipient)


@external
def unmount(_new_rewards_owner: address = msg.sender):
    """
    @notice
        Sets the new rewards contract owner and transfers Ether and rewards token
        balances to that address. Can only be called by the manager contract owner.

    @dev
        The new rewards owner will have to call rewards_contract.acceptOwnership()
        to finish the ownership transfer.
    """
    assert msg.sender == self.owner, "not permitted"
    assert _new_rewards_owner != ZERO_ADDRESS, "zero rewards owner"

    _rewards_contract: address = self.rewards_contract
    StakingRewards(_rewards_contract).setRewardsDistribution(_new_rewards_owner)
    StakingRewards(_rewards_contract).nominateNewOwner(_new_rewards_owner)

    self._recover_erc20(self.rewards_token, _new_rewards_owner)

    if self.balance > 0:
        send(_new_rewards_owner, self.balance)


@internal
def _start_next_rewards_period():
    _rewards_contract: address = self.rewards_contract
    _rewards_token: address = self.rewards_token
    _rewards_duration: uint256 = self.rewards_duration
    _rewards_per_duration: uint256 = self.rewards_per_duration

    assert _rewards_contract != ZERO_ADDRESS, "manager: rewards not set"
    assert _rewards_duration != 0 and _rewards_per_duration != 0, "manager: rewards disabled"

    rewards_token_balance: uint256 = ERC20(_rewards_token).balanceOf(self)
    if _rewards_per_duration > rewards_token_balance:
        amount: uint256 = _rewards_per_duration - rewards_token_balance
        assert ERC20(_rewards_token).transferFrom(self.owner, self, amount), (
            "manager: transfer failed")

    assert ERC20(_rewards_token).approve(_rewards_contract, _rewards_per_duration), (
        "manager: approve failed")

    if StakingRewards(_rewards_contract).rewardsDuration() != _rewards_duration:
        StakingRewards(_rewards_contract).setRewardsDuration(_rewards_duration)

    StakingRewards(_rewards_contract).notifyRewardAmount(_rewards_per_duration)


@external
def start_next_rewards_period(_force: bool = False):
    """
    @notice
        Starts the next rewards period.

    @param _force
        Pass True to start the new period even if the current one hasn't finished yet.
        Only the owner is allowed to do this. If False is passed, the tx will revert
        unless the current period has finished.
    """
    if _force:
        assert msg.sender == self.owner, "not permitted"
    else:
        assert block.timestamp >= StakingRewards(self.rewards_contract).periodFinish(), (
            "rewards period not finished")
    self._start_next_rewards_period()
