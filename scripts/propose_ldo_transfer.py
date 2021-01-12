import os
import sys
from brownie import network, accounts, Wei, interface
from utils.evm_script import encode_call_script

from utils.config import (
    lido_dao_voting_address,
    lido_dao_token_manager_address,
    lido_dao_finance_address,
    ldo_token_address,
    gas_price,
    get_is_live,
    get_deployer_account,
    prompt_bool
)


EMPTY_CALLSCRIPT = '0x00000001'


def create_vote(voting, token_manager, vote_desc, evm_script, tx_params):
    new_vote_script = encode_call_script([(
        voting.address,
        voting.newVote.encode_input(
            evm_script if evm_script is not None else EMPTY_CALLSCRIPT,
            vote_desc,
            False,
            False
        )
    )])
    tx = token_manager.forward(new_vote_script, tx_params)
    vote_id = tx.events['StartVote']['voteId']
    return (vote_id, tx)


def propose_payment(
    voting,
    token_manager,
    finance,
    token_address,
    recipient,
    amount,
    reference,
    tx_params
):
    payment_script = encode_call_script([(
        finance.address,
        finance.newImmediatePayment.encode_input(
            token_address,
            recipient,
            amount,
            reference
        )
    )])
    return create_vote(
        voting=voting,
        token_manager=token_manager,
        vote_desc=f'Send {amount} tokens at {token_address} to {recipient}: {reference}',
        evm_script=payment_script,
        tx_params=tx_params
    )



def propose_ldo_transfer(recipient, amount, reference, tx_params):
    return propose_payment(
        voting=interface.Voting(lido_dao_voting_address),
        token_manager=interface.TokenManager(lido_dao_token_manager_address),
        finance=interface.Finance(lido_dao_finance_address),
        token_address=ldo_token_address,
        recipient=recipient,
        amount=amount,
        reference=reference,
        tx_params=tx_params
    )


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(True)

    if 'TO' not in os.environ:
        raise EnvironmentError('Please set the TO env variable to the recipient address')

    if 'AMOUNT' not in os.environ:
        raise EnvironmentError('Please set the AMOUNT env variable, e.g. "1 ether" of "1 gwei"')

    if 'REFERENCE' not in os.environ:
        raise EnvironmentError('Please set the REFERENCE env variable')

    amount = Wei(os.environ['AMOUNT'])
    recipient = os.environ['TO']
    reference = os.environ['REFERENCE']

    print(f"You're going to propose sending {amount} LDO token-wei to {recipient} (reference: '{reference}').")
    sys.stdout.write('Are you sure (y/n)? ')

    if not prompt_bool():
        print('Aborting')
        return

    vote_id = propose_ldo_transfer(
        recipient=recipient,
        amount=amount,
        reference=reference,
        tx_params={"from": deployer, "gas_price": Wei(gas_price), "required_confs": 1}
    )[0]

    print('Vote ID:', vote_id)
