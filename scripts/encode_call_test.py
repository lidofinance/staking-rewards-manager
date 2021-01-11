from brownie import *

import eth_abi
from web3 import Web3
from eth_typing.evm import HexAddress

def create_executor_id(id):
    return '0x' + str(id).zfill(8)

def strip_byte_prefix(hexstr):
    return hexstr[2:] if hexstr[0:2] == '0x' else hexstr

def encode_call_script(actions, spec_id = 1):
    result = create_executor_id(spec_id)
    for to, calldata in actions:
        addr_bytes = Web3.toBytes(hexstr=HexAddress(to)).hex()
        calldata_bytes = strip_byte_prefix(calldata)
        length = eth_abi.encode_single('int256', len(calldata_bytes) // 2).hex()

        result += addr_bytes + length[56:] + calldata_bytes

    return result

def main():
    actions = [
        (
            '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32',
            '0x095ea7b3000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84000000000000000000000000000000000000000000000000000000000000002a'
        )
    ]

    print(encode_call_script(actions))



