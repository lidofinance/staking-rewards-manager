from brownie import Wei

ONE_WEEK = 60 * 60 * 24 * 7

def test_deploy(ldo_token, rewards, rewards_manager, dao_voting, dao_agent):
    print("Rewards:", rewards)
    print("Rewards manager:", rewards_manager)

    reward_period = ONE_WEEK
    reward_amount = Wei("1 ether")

    assert ldo_token.balanceOf(dao_agent) > 0
    approve_calldata = ldo_token.approve.encode_input(rewards_manager, reward_amount)

    dao_agent.execute(ldo_token, 0, approve_calldata, {"from": dao_voting})
    assert ldo_token.allowance(dao_agent, rewards_manager) == reward_amount
