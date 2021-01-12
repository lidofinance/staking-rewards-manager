from brownie import *
from utils.evm_script import encode_call_script

def main():
    actions = [
        (
            '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32',
            '0x095ea7b3000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84000000000000000000000000000000000000000000000000000000000000002a'
        )
    ]

    print(encode_call_script(actions))


