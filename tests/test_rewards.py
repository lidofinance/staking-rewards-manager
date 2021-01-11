from brownie import Wei
from brownie.network.state import Chain

ONE_WEEK = 60 * 60 * 24 * 7


def test_happy_path(
    steth_token,
    lp_token,
    steth_pool,
    gauge,
    gauge_admin,
    ldo_token,
    dao_voting,
    dao_agent,
    ape,
    stranger,
    steth_whale,
    curve_farmer,
    rewards_helpers
):
    chain = Chain()

    # deploying and installing the rewards contract

    rewards_period = ONE_WEEK
    reward_amount = Wei("1 ether")
    approve_amount = 4 * reward_amount

    deployed = rewards_helpers.deploy_rewards(
        rewards_period=rewards_period,
        reward_amount=reward_amount,
        dao_agent=dao_agent,
        lp_token=lp_token,
        rewards_token=ldo_token,
        deployer=ape
    )

    rewards_manager = deployed["manager"]
    rewards_contract = deployed["rewards"]

    rewards_helpers.install_rewards(
        gauge=gauge,
        gauge_admin=gauge_admin,
        rewards_token=ldo_token,
        rewards=rewards_contract
    )

    # DAO approves the rewards contract to spend LDO

    assert ldo_token.balanceOf(dao_agent) >= approve_amount
    approve_calldata = ldo_token.approve.encode_input(rewards_contract, approve_amount)
    dao_agent.execute(ldo_token, 0, approve_calldata, {"from": dao_voting})
    assert ldo_token.allowance(dao_agent, rewards_contract) == approve_amount

    # someone starts the first rewards period

    rewards_manager.start_next_rewards_period({"from": stranger})
    assert rewards_manager.is_rewards_period_finished() == False

    # the whale provides liquidity and locks their LP tokens into the gauge

    steth_deposit_amount = steth_token.balanceOf(steth_whale)
    assert steth_deposit_amount > 0

    steth_token.approve(steth_pool, steth_deposit_amount, {"from": steth_whale})
    steth_pool.add_liquidity([0, steth_deposit_amount], 0, {"from": steth_whale})

    lp_token_deposit_amount = lp_token.balanceOf(steth_whale)
    assert lp_token_deposit_amount > 0
    assert steth_token.balanceOf(steth_whale) <= 1

    lp_token.approve(gauge, lp_token_deposit_amount, {"from": steth_whale})
    gauge.deposit(lp_token_deposit_amount, {"from": steth_whale})

    assert lp_token.balanceOf(steth_whale) == 0
    assert gauge.balanceOf(steth_whale) > 0

    # the farmer already has theor LP tokens locked into the gauge

    assert gauge.balanceOf(curve_farmer) > 0

    whale_ldo_prev_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_prev_balance = ldo_token.balanceOf(curve_farmer)

    assert whale_ldo_prev_balance == 0

    # rewards period partially passes; folks claim their rewards

    chain.sleep(rewards_period // 2)
    gauge.claim_rewards({"from": steth_whale})
    gauge.claim_rewards({"from": curve_farmer})

    whale_ldo_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_balance = ldo_token.balanceOf(curve_farmer)

    assert whale_ldo_balance > 0
    assert farmer_ldo_balance > farmer_ldo_prev_balance
    whale_ldo_prev_balance, farmer_ldo_prev_balance = whale_ldo_balance, farmer_ldo_balance

    # rewards period fully passes; folks claim their rewards once again

    assert rewards_manager.is_rewards_period_finished() == False
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.is_rewards_period_finished() == True

    gauge.claim_rewards({"from": steth_whale})
    gauge.claim_rewards({"from": curve_farmer})

    whale_ldo_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_balance = ldo_token.balanceOf(curve_farmer)

    assert whale_ldo_balance > whale_ldo_prev_balance
    assert farmer_ldo_balance > farmer_ldo_prev_balance
