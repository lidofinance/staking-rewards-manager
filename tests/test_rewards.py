from brownie import Wei

ONE_WEEK = 60 * 60 * 24 * 7

def test_deploy(ldo_token, rewards, dao_voting, dao_agent):
    print("Rewards:", rewards)

    reward_period = ONE_WEEK
    reward_amount = Wei("1 ether")

    approve_calldata = ldo_token.approve.encode_input(rewards, reward_amount)
    print("approve_calldata:",  approve_calldata)

    assert ldo_token.balanceOf(dao_agent) > 0

    dao_agent.execute(ldo_token, 0, approve_calldata, {"from": dao_voting})

    assert ldo_token.allowance(dao_agent, rewards) == reward_amount
