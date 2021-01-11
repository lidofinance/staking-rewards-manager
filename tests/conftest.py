import pytest
from brownie import Wei, ZERO_ADDRESS


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope='module')
def ape(accounts):
    return accounts[0]


# holds a lot of stETH
@pytest.fixture(scope='module')
def whale(accounts, steth_token):
    address = "0x32199f1ffd5c9a5745a98fe492570a8d1601dc4c"
    assert steth_token.balanceOf(address) > 0
    # assert lp_token.balanceOf(address) == 0
    return accounts.at(address, force=True)


# Lido DAO Voting app
@pytest.fixture(scope='module')
def dao_voting(accounts):
    return accounts.at("0x2e59A20f205bB85a89C53f1936454680651E618e", force=True)


# Lido DAO Agent app
@pytest.fixture(scope='module')
def dao_agent(interface):
    return interface.Agent("0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c")


@pytest.fixture(scope='module')
def steth_pool(interface):
    return interface.StableSwapSTETH("0xDC24316b9AE028F1497c275EB9192a3Ea0f67022")


@pytest.fixture(scope='module')
def lp_token(steth_pool, interface):
    token_address = steth_pool.lp_token()
    return interface.ERC20(token_address)


@pytest.fixture(scope='module')
def steth_token(interface):
    return interface.ERC20("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")


@pytest.fixture(scope='module')
def ldo_token(interface):
    return interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")


@pytest.fixture(scope='module')
def gauge(interface):
    return interface.LiquidityGaugeV2("0x182B723a58739a9c974cFDB385ceaDb237453c28")


@pytest.fixture(scope='module')
def gauge_admin(gauge, accounts):
    return accounts.at(gauge.admin(), force=True)


ONE_WEEK = 60 * 60 * 24 * 7

@pytest.fixture()
def rewards(StakingRewards, gauge, lp_token, ldo_token, ape, gauge_admin):
    rewards = StakingRewards.deploy(
        ape, # _owner
        ape, # _rewardsDistribution
        ldo_token, # _rewardsToken
        lp_token, # _stakingToken
        ONE_WEEK, # _rewardsDuration
        {"from": ape}
    )
    sigs = [
        rewards.stake.signature[2:],
        rewards.withdraw.signature[2:],
        rewards.getReward.signature[2:]
    ]
    gauge.set_rewards(
        rewards, # _reward_contract
        f"0x{sigs[0]}{sigs[1]}{sigs[2]}{'00' * 20}", # _sigs
        [ldo_token] + [ZERO_ADDRESS] * 7, # _reward_tokens
        {"from": gauge_admin}
    )
    assert gauge.reward_contract() == rewards
    assert gauge.reward_tokens(0) == ldo_token
    assert gauge.reward_tokens(1) == ZERO_ADDRESS
    return rewards


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
