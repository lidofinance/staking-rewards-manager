import os
from brownie import network, accounts


lp_token_address = '0x06325440d014e39736583c165c2963ba99faf14e'
ldo_token_address = '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32'
lido_dao_agent_address = '0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c'


initial_rewards_duration_sec = 60 * 60 * 24 * 7 # one week


gas_price = "10 gwei"


def get_is_live():
    return network.show_active() != 'development'


def get_deployer_account(is_live):
    if is_live and 'DEPLOYER' not in os.environ:
        raise EnvironmentError('Please set DEPLOYER env variable to the deployer account name')

    return accounts.load(os.environ['DEPLOYER']) if is_live else accounts[0]

