import pytest
import brownie
from brownie.network.state import Chain

ZERO_ADDRESS = brownie.ZERO_ADDRESS
ONE_WEEK = 60 * 60 * 24 * 7
rewards_period = ONE_WEEK


@pytest.fixture()
def rewards_manager(RewardsManager, ape):
    return RewardsManager.deploy({"from": ape})


@pytest.fixture()
def another_rewards_manager(RewardsManager, ape):
    return RewardsManager.deploy({"from": ape})


@pytest.fixture()
def deployed_contracts(rewards_helpers, ape):
    return rewards_helpers.deploy_rewards(
        rewards_period=rewards_period,
        deployer=ape
    )


def test_owner_is_deployer(rewards_manager, ape):
    assert rewards_manager.owner() == ape


def test_stranger_can_not_transfer_ownership(rewards_manager, ape, stranger):
    with brownie.reverts("not permitted"):
        rewards_manager.transfer_ownership(stranger, {"from": stranger})


def test_ownership_can_be_transferred(rewards_manager, ape, stranger):
    rewards_manager.transfer_ownership(stranger, {"from": ape})
    assert rewards_manager.owner() == stranger


def test_ownership_can_be_transferred_to_zero_address(rewards_manager, ape):
    rewards_manager.transfer_ownership(ZERO_ADDRESS, {"from": ape})
    assert rewards_manager.owner() == ZERO_ADDRESS


def test_stranger_can_not_set_rewards_contract(rewards_manager, another_rewards_manager, stranger):
    with brownie.reverts("not permitted"):
        rewards_manager.set_rewards_contract(
            another_rewards_manager, {"from": stranger})


def test_owner_can_set_rewards_contract(rewards_manager, another_rewards_manager, ape):
    rewards_manager.set_rewards_contract(
        another_rewards_manager, {"from": ape})
    assert rewards_manager.rewards_contract() == another_rewards_manager


def test_owner_can_set_rewards_contract_to_zero_address(rewards_manager, ape):
    rewards_manager.set_rewards_contract(ZERO_ADDRESS, {"from": ape})
    assert rewards_manager.rewards_contract() == ZERO_ADDRESS


def test_stranger_can_not_recover_erc20(rewards_manager, ldo_token, stranger):
    with brownie.reverts("not permitted"):
        rewards_manager.recover_erc20(ldo_token, {"from": stranger})


def test_owner_recovers_erc20(rewards_manager, ldo_token, ape):
    rewards_manager.recover_erc20(ldo_token, {"from": ape})


def test_stranger_can_check_is_rewards_period_finished(deployed_contracts, stranger):
    (manager, _) = deployed_contracts
    assert manager.is_rewards_period_finished({"from": stranger}) == True


def test_stranger_can_not_start_next_rewards_period_without_rewards_contract_set(rewards_manager, stranger):
    with brownie.reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": stranger})


def test_stranger_can_not_start_next_rewards_period_with_zero_amount(deployed_contracts, stranger, ape):
    (manager, _) = deployed_contracts
    with brownie.reverts("manager: rewards disabled"):
        manager.start_next_rewards_period({"from": stranger})


def test_stranger_starts_next_rewards_period(deployed_contracts, ldo_token, dao_agent, stranger):
    (manager, _) = deployed_contracts
    rewards_amount = brownie.Wei("1 ether")
    ldo_token.transfer(manager, rewards_amount, {"from": dao_agent})
    assert manager.is_rewards_period_finished({"from": stranger}) == True
    manager.start_next_rewards_period({"from": stranger})
    assert manager.is_rewards_period_finished({"from": stranger}) == False


def test_stranger_can_not_start_next_rewards_period_while_current_is_active(deployed_contracts, ldo_token, dao_agent, stranger):
    (manager, _) = deployed_contracts
    rewards_amount = brownie.Wei("1 ether")
    ldo_token.transfer(manager, rewards_amount, {"from": dao_agent})
    assert manager.is_rewards_period_finished({"from": stranger}) == True
    manager.start_next_rewards_period({"from": stranger})
    chain = Chain()
    chain.sleep(1)
    chain.mine()

    ldo_token.transfer(manager, rewards_amount, {"from": dao_agent})
    assert manager.is_rewards_period_finished({"from": stranger}) == False
    with brownie.reverts("manager: rewards period not finished"):
        manager.start_next_rewards_period({"from": stranger})


def test_stranger_can_start_next_rewards_period_after_current_is_finished(deployed_contracts, ldo_token, dao_agent, stranger):
    (manager, _) = deployed_contracts
    rewards_amount = brownie.Wei("1 ether")
    ldo_token.transfer(manager, rewards_amount, {"from": dao_agent})
    assert manager.is_rewards_period_finished({"from": stranger}) == True
    manager.start_next_rewards_period({"from": stranger})
    chain = Chain()
    chain.sleep(rewards_period)
    chain.mine()

    ldo_token.transfer(manager, rewards_amount, {"from": dao_agent})
    assert manager.is_rewards_period_finished({"from": stranger}) == True
    manager.start_next_rewards_period({"from": stranger})
    assert manager.is_rewards_period_finished({"from": stranger}) == False
