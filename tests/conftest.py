import pytest
from brownie import Wei, ZERO_ADDRESS
from scripts.deploy import deploy_manager_and_rewards
from utils.config import (
    lp_token_address,
    ldo_token_address,
    lido_dao_agent_address,
    lido_dao_finance_address,
    lido_dao_voting_address,
    lido_dao_token_manager_address
)


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope='module')
def ape(accounts):
    return accounts[0]


@pytest.fixture()
def steth_whale(accounts, steth_token, lido, lp_token):
    acct = accounts[1]
    lido.submit(ZERO_ADDRESS, {"from": acct, "value": "10 ether"})
    assert steth_token.balanceOf(acct) > 0
    assert lp_token.balanceOf(acct) == 0
    return acct


@pytest.fixture(scope='module')
def stranger(accounts):
    return accounts[9]


@pytest.fixture(scope='module')
def curve_farmer(accounts, gauge):
    # already deposited to the steth gauge
    acct = accounts.at("0x32199f1fFD5C9a5745A98FE492570a8D1601Dc4C", force=True)
    assert gauge.balanceOf(acct) > 0
    return acct


@pytest.fixture(scope='module')
def dao_voting_impersonated(accounts):
    return accounts.at("0x2e59A20f205bB85a89C53f1936454680651E618e", force=True)


@pytest.fixture(scope='module')
def dao_voting(interface):
    return interface.Voting(lido_dao_voting_address)


@pytest.fixture(scope='module')
def dao_token_manager(interface):
    return interface.TokenManager(lido_dao_token_manager_address)


@pytest.fixture(scope='module')
def dao_finance(interface):
    return interface.Finance(lido_dao_finance_address)


@pytest.fixture(scope='module')
def dao_holder(accounts):
    return accounts.at('0x537dfB5f599A3d15C50E2d9270e46b808A52559D', force=True)


@pytest.fixture(scope='module')
def lido(interface):
    return interface.Lido("0xae7ab96520de3a18e5e111b5eaab095312d7fe84")


@pytest.fixture(scope='module')
def steth_token(interface, lido):
    return interface.ERC20(lido.address)


# Lido DAO Agent app
@pytest.fixture(scope='module')
def dao_agent(interface):
    return interface.Agent(lido_dao_agent_address)


@pytest.fixture(scope='module')
def steth_pool(interface):
    return interface.StableSwapSTETH("0xDC24316b9AE028F1497c275EB9192a3Ea0f67022")


@pytest.fixture(scope='module')
def lp_token(interface):
    return interface.ERC20(lp_token_address)


@pytest.fixture(scope='module')
def ldo_token(interface):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope='module')
def gauge(interface):
    return interface.LiquidityGaugeV2("0x182B723a58739a9c974cFDB385ceaDb237453c28")


@pytest.fixture(scope='module')
def gauge_admin(gauge, accounts):
    return accounts.at(gauge.admin(), force=True)


class RewardsHelpers:
    @staticmethod
    def deploy_rewards(rewards_period, deployer):
        return deploy_manager_and_rewards(
            rewards_duration=rewards_period,
            tx_params={"from": deployer},
            publish_source=False
        )

    @staticmethod
    def install_rewards(gauge, gauge_admin, rewards_token, rewards):
        sigs = [
            rewards.stake.signature[2:],
            rewards.withdraw.signature[2:],
            rewards.getReward.signature[2:]
        ]
        gauge.set_rewards(
            rewards, # _reward_contract
            f"0x{sigs[0]}{sigs[1]}{sigs[2]}{'00' * 20}", # _sigs
            [rewards_token] + [ZERO_ADDRESS] * 7, # _reward_tokens
            {"from": gauge_admin}
        )
        assert gauge.reward_contract() == rewards
        assert gauge.reward_tokens(0) == rewards_token
        assert gauge.reward_tokens(1) == ZERO_ADDRESS


@pytest.fixture(scope='module')
def rewards_helpers():
    return RewardsHelpers


class Helpers:
    @staticmethod
    def filter_events_from(addr, events):
      return list(filter(lambda evt: evt.address == addr, events))

    @staticmethod
    def assert_single_event_named(evt_name, tx, evt_keys_dict):
      receiver_events = Helpers.filter_events_from(tx.receiver, tx.events[evt_name])
      assert len(receiver_events) == 1
      assert dict(receiver_events[0]) == evt_keys_dict


@pytest.fixture(scope='module')
def helpers():
    return Helpers
