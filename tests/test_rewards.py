from brownie import Wei

ONE_WEEK = 60 * 60 * 24 * 7

def test_deploy(ldo_token, rewards, rewards_manager, dao_voting, dao_agent, ape, stranger):
    print("Rewards:", rewards)
    print("Rewards manager:", rewards_manager)

    reward_period = ONE_WEEK
    reward_amount = Wei("1 ether")
    approve_amount = 4 * reward_amount

    rewards_manager.set_rewards_contract(rewards, {"from": ape})
    assert rewards_manager.rewards_contract() == rewards

    rewards_manager.set_reward_amount(reward_amount)
    rewards_manager.transfer_ownership(dao_agent)

    assert ldo_token.balanceOf(dao_agent) > 0
    approve_calldata = ldo_token.approve.encode_input(rewards, approve_amount)

    dao_agent.execute(ldo_token, 0, approve_calldata, {"from": dao_voting})
    assert ldo_token.allowance(dao_agent, rewards) == approve_amount

    rewards_manager.start_next_rewards_period({"from": stranger})
