import sys

from brownie import (
    network,
    accounts,
    RewardsManager,
    StakingRewards,
    Wei
)

from utils.config import (
    lp_token_address,
    ldo_token_address,
    lido_dao_agent_address,
    initial_rewards_duration_sec,
    gas_price,
    get_is_live,
    get_deployer_account,
    prompt_bool
)


def deploy_manager(tx_params):
    # Etherscan doesn't support Vyper verification yet
    return RewardsManager.deploy(tx_params, publish_source=False)


def deploy_rewards(manager_contract, rewards_duration, tx_params, publish_source=True):
    return StakingRewards.deploy(
        lido_dao_agent_address, # _owner
        manager_contract, # _rewardsDistribution
        ldo_token_address, # _rewardsToken
        lp_token_address, # _stakingToken
        rewards_duration, # _rewardsDuration
        tx_params,
        publish_source=publish_source,
    )


def deploy_manager_and_rewards(rewards_duration, tx_params, publish_source=True):
    manager = deploy_manager(tx_params)

    rewards = deploy_rewards(
        manager_contract=manager,
        rewards_duration=rewards_duration,
        tx_params=tx_params,
        publish_source=publish_source
    )

    manager.set_rewards_contract(rewards, tx_params)
    assert manager.rewards_contract() == rewards
    manager.transfer_ownership(lido_dao_agent_address, tx_params)

    return (manager, rewards)


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)

    print('Deployer:', deployer)
    print('Initial rewards duration:', initial_rewards_duration_sec)
    print('LP token address:', lp_token_address)
    print('LDO token address:', ldo_token_address)
    print('Gas price:', gas_price)

    sys.stdout.write('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_manager_and_rewards(
        rewards_duration=initial_rewards_duration_sec,
        tx_params={"from": deployer, "gas_price": Wei(gas_price), "required_confs": 1},
        publish_source=is_live
    )
