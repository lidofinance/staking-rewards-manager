import os
import sys
from brownie import network, accounts


lp_token_address = '0x06325440d014e39736583c165c2963ba99faf14e'
ldo_token_address = '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32'
lido_dao_agent_address = '0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c'
lido_dao_finance_address = '0xB9E5CBB9CA5b0d659238807E84D0176930753d86'
lido_dao_voting_address = '0x2e59A20f205bB85a89C53f1936454680651E618e'
lido_dao_token_manager_address = '0xf73a1260d222f447210581DDf212D915c09a3249'


initial_rewards_duration_sec = 60 * 60 * 24 * 30 # one month


gas_price = "90 gwei"


def get_is_live():
    return network.show_active() != 'development'


def get_deployer_account(is_live):
    if is_live and 'DEPLOYER' not in os.environ:
        raise EnvironmentError('Please set DEPLOYER env variable to the deployer account name')

    return accounts.load(os.environ['DEPLOYER']) if is_live else accounts[0]


def prompt_bool():
    choice = input().lower()
    if choice in {'yes', 'y'}:
       return True
    elif choice in {'no', 'n'}:
       return False
    else:
       sys.stdout.write("Please respond with 'yes' or 'no'")
