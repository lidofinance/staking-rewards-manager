import pytest
import brownie


@pytest.fixture()
def rewards_manager(RewardsManager, ape):
    return RewardsManager.deploy({"from": ape})


def test_owner_recovers_erc20_without_balance(rewards_manager, ldo_token, ape):
    assert ldo_token.balanceOf(ape) == 0
    tx = rewards_manager.recover_erc20(ldo_token, {"from": ape})
    assert len(tx.events) == 0


def test_owner_recovers_erc20_with_balance(rewards_manager, ldo_token, dao_agent, ape, stranger):
    recipient = stranger
    transfer_amount = brownie.Wei("1 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": dao_agent})
    assert ldo_token.balanceOf(rewards_manager) == transfer_amount

    recipient_balance_before = ldo_token.balanceOf(recipient)
    tx = rewards_manager.recover_erc20(ldo_token, recipient, {"from": ape})
    recipient_balance_after = ldo_token.balanceOf(recipient)

    assert ldo_token.balanceOf(rewards_manager) == 0
    assert recipient_balance_after - recipient_balance_before == transfer_amount
    assert len(tx.events) == 1
    assert tx.events[0].name == "Transfer"
    assert tx.events[0]["_from"] == rewards_manager
    assert tx.events[0]["_to"] == recipient
    assert tx.events[0]["_value"] == transfer_amount


def test_owner_recovers_erc20_to_the_caller_by_default(rewards_manager, ldo_token, dao_agent, ape):
    transfer_amount = brownie.Wei("1 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": dao_agent})

    recipient_balance_before = ldo_token.balanceOf(ape)
    tx = rewards_manager.recover_erc20(ldo_token, {"from": ape})
    recipient_balance_after = ldo_token.balanceOf(ape)

    assert ldo_token.balanceOf(rewards_manager) == 0
    assert recipient_balance_after - recipient_balance_before == transfer_amount
    assert len(tx.events) == 1
    assert tx.events[0].name == "Transfer"
    assert tx.events[0]["_from"] == rewards_manager
    assert tx.events[0]["_to"] == ape
    assert tx.events[0]["_value"] == transfer_amount
