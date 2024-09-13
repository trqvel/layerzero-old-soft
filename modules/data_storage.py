import json
import random

data_blockchains = {
    "Polygon": {
        "network_id": 137,
        "chain_id": 109,
        "native": "MATIC",
        "rpc": ["https://rpc.ankr.com/polygon/d9c2280cd743801583b1f88c68d6c51f25a5adc3e8c0b1808fb15b49e60c0143"],
        "explorer": "https://polygonscan.com/",
        "stargate_bridge_contract": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
        "btcb_bridge_contract": "0x2297aebd383787a160dd0d9f71508148769342e3",
        "btcb_contract": "0x2297aEbD383787A160DD0d9F71508148769342E3",
        "usdc_contract": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "usdt_contract": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
        "stg_contract": "0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590",
        "stg_stake_contract": "0x3ab2da31bbd886a7edf68a6b60d3cde657d3a15d",
        "aptos_contract": "0x488863d609f3a673875a914fbee7508a1de45ec6",
        "sushi_contract": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        "woofi_contract": "0x817Eb46D60762442Da3D931Ff51a30334CA39B74",
    },
    "Avalanche": {
        "network_id": 43114,
        "chain_id": 106,
        "native": "AVAX",
        "rpc": ["https://rpc.ankr.com/avalanche/d9c2280cd743801583b1f88c68d6c51f25a5adc3e8c0b1808fb15b49e60c0143"],
        "explorer": "https://snowtrace.io/",
        "stargate_bridge_contract": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
        "btcb_bridge_contract": "0x2297aebd383787a160dd0d9f71508148769342e3",
        "btcb_contract": "0x152b9d0FdC40C096757F570A51E494bd4b943E50",
        "usdc_contract": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "usdt_contract": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
        "stg_contract": "0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590",
        "stg_stake_contract": "0xca0f57d295bbce554da2c07b005b7d6565a58fce",
        "aptos_contract": "0x2297aebd383787a160dd0d9f71508148769342e3",
        "sushi_contract": "0x717b7948aa264decf4d780aa6914482e5f46da3e",
        "woofi_contract": "0xC22FBb3133dF781E6C25ea6acebe2D2Bb8CeA2f9",
    },
    "Arbitrum": {
        "network_id": 42161,
        "chain_id": 110,
        "native": "ETH",
        "explorer": "https://arbiscan.io/",
        "rpc": ["https://rpc.ankr.com/arbitrum/d9c2280cd743801583b1f88c68d6c51f25a5adc3e8c0b1808fb15b49e60c0143"],
        "stargate_bridge_contract": "0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614",
        "btcb_bridge_contract": "0x2297aebd383787a160dd0d9f71508148769342e3",
        "btcb_contract": "0x2297aEbD383787A160DD0d9F71508148769342E3",
        "usdc_contract": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        "usdt_contract": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
        "stg_contract": "0x6694340fc020c5E6B96567843da2df01b2CE1eb6",
        "stg_stake_contract": "0xfbd849e6007f9bc3cc2d6eb159c045b8dc660268",
        "testnet_contract": "0x0a9f824c05a74f577a536a8a0c673183a872dff4",
        "testnetGetFee_contract": "0xdd69db25f6d620a7bad3023c5d32761d353d3de9",
        "aptos_contract": "0x1BAcC2205312534375c8d1801C27D28370656cFf",
        "sushi_contract": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        "woofi_contract": "0x9aed3a8896a85fe9a8cac52c9b402d092b629a30",
    },
    "Fantom": {
        "network_id": 250,
        "chain_id": 112,
        "native": "FTM",
        "rpc": ["https://rpc.fantom.network", "https://rpc.ftm.tools", "https://rpc.ankr.com/fantom",
                "https://rpc2.fantom.network"],
        "explorer": "https://ftmscan.com/",
        "stargate_bridge_contract": "0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6",
        "usdc_contract": "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75",
        "sushi_contract": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        "woofi_contract": "0x382A9b0bC5D29e96c3a0b81cE9c64d6C8F150Efb",
    },
    "BSC": {
        "network_id": 56,
        "chain_id": 102,
        "native": "BNB",
        "rpc": ["https://bsc-dataseed1.binance.org/"],
        "explorer": "https://bscscan.com/",
        "stargate_bridge_contract": "0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8",
        "core_bridge_contract": "0x52e75d318cfb31f9a2edfa2dfee26b161255b233",
        "harmony_bridge_contract": "0x0551ca9e33bada0355dfce34685ad3b73cf3ad70",
        "harmony_bridge_contract2": "0x8d1ebcda83fd905b597bf6d3294766b64ecf2aa7",
        "btcb_bridge_contract": "0x2297aebd383787a160dd0d9f71508148769342e3",
        "btcb_contract": "0x2297aEbD383787A160DD0d9F71508148769342E3",
        "usdc_contract": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "usdt_contract": "0x55d398326f99059ff775485246999027b3197955",
        "aptos_contract": "0x2762409baa1804d94d8c0bcff8400b78bf915d5b",
        "sushi_contract": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        "woofi_contract": "0x4f4Fd4290c9bB49764701803AF6445c5b03E8f06",
    },
    "Core": {
        "network_id": 1116,
        "chain_id": 0,
        "native": "CORE",
        "rpc": ["https://rpc.coredao.org"],
        "explorer": "https://scan.coredao.org/",
        "core_bridge_contract": "0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE",
        "usdc_contract": "0xa4151b2b3e269645181dccf2d426ce75fcbdeca9",
        "usdt_contract": "0x900101d06a7426441ae63e9ab3b9b0f63be145f1",
    },
    "Optimism": {
        "network_id": 10,
        "chain_id": 111,
        "native": "ETH",
        "rpc": ["https://optimism-mainnet.infura.io/v3/2d7301a045e641c0a6c364e627e76399",
                "https://optimism-mainnet.infura.io/v3/e0bd9ebf6e484765a7832582e890ef49",
                "https://optimism-mainnet.infura.io/v3/17e1b3e290484b34a70e6285ed99a89c"],
        "explorer": "https://optimistic.etherscan.io/",
        "stargate_bridge_contract": "0xB0D502E938ed5f4df2E681fE6E419ff29631d62b",
        "core_bridge_contract": "0x52e75d318cfb31f9a2edfa2dfee26b161255b233",  # TODO
        "harmony_bridge_contract": "0x0551ca9e33bada0355dfce34685ad3b73cf3ad70",  # TODO
        "harmony_bridge_contract2": "0x8d1ebcda83fd905b597bf6d3294766b64ecf2aa7",  # TODO
        "usdc_contract": "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
        "usdt_contract": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
        "stg_contract": "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97",
        "stg_stake_contract": "0xfbd849e6007f9bc3cc2d6eb159c045b8dc660268",  # TODO
        "testnet_contract": "0x0a9f824c05a74f577a536a8a0c673183a872dff4",  # TODO
        "testnetGetFee_contract": "0xdd69db25f6d620a7bad3023c5d32761d353d3de9",  # TODO
        "aptos_contract": "0x2762409baa1804d94d8c0bcff8400b78bf915d5b",  # TODO
        "sushi_contract": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",  # TODO
        "woofi_contract": "0x4f4Fd4290c9bB49764701803AF6445c5b03E8f06",  # TODO
    }
}



data_decimals = {
        "BSC": {
            "USDC": 18,
            "USDT": 18,
            "STG": 18,
            "BTCB": 8,
        },
        "Avalanche": {
            "USDC": 6,
            "USDT": 6,
            "STG": 18,
            "BTCB": 8,
        },
        "Fantom": {
            "USDC": 6,
            "STG": 18,
            "BTCB": 8,
        },
        "Polygon": {
            "USDC": 6,
            "USDT": 6,
            "STG": 18,
            "BTCB": 8,
        },
        "Arbitrum": {
            "USDC": 6,
            "USDT": 6,
            "STG": 18,
            "BTCB": 8,
            "ETH": 18,
        },
        "Core": {
            "USDC": 6,
            "USDT": 6,
        },
        "Optimism": {
            "USDC": 6,
            "USDT": 6,
            "STG": 18,
            "BTCB": 8,
            "ETH": 18
        }
    }


data_network_id = {
    'Avalanche': {'binance': 'AVAXC', 'okx': 'Avalanche C-Chain', 'mexc': 'AVAX_CCHAIN'},
    'Arbitrum': {'binance': 'ARBITRUM', 'okx': 'Arbitrum One', 'mexc': 'error'},
    'Polygon': {'binance': 'MATIC', 'okx': 'Polygon', 'mexc': 'MATIC'},
    'Fantom': {'binance': 'FTM', 'okx': 'Fantom', 'mexc': 'FTM'},
    'BSC': {'binance': 'BSC', 'okx': 'BSC', 'mexc': 'BEP20(BSC)'},
    'Core': {'binance': 'CORE', 'okx': 'CORE', 'mexc': 'CORE'},
    'Optimism': {'binance': '', 'okx': '', 'mexc': ''}  # TODO
}


data_gas_limit = {
    'Core': random.randint(380_000, 500_000),
    'Arbitrum': random.randint(3_000_000, 4_000_000),
    'Optimism': random.randint(700_000, 900_000),
    'Fantom': random.randint(800_000, 1_000_000),
    'Polygon': random.randint(580_000, 630_000),
    'BSC': random.randint(560_000, 600_000),
    'Avalanche': random.randint(580_000, 700_000)
}

chains_fee = {
    "Avalanche": 0.15,
    "Arbitrum": 0.23,
    "Polygon": 0.05,
    "BSC": 0.28,
    "Core": 0.1,
    "Optimism": 0.26
}

data_boost_gas = {
    "Arbitrum": {
        "gasPrice": 1.01,
        "gasLimit": 1.2
    },
    "Core": {
        "gasPrice": 1.1,
        "gasLimit": 1.24
    },
    "Avalanche": {
        "gasPrice": 1.1,
        "gasLimit": 1.33
    },
    "Polygon": {
        "gasPrice": 1.42,
        "gasLimit": 2.5
    },
    "BSC": {
        "gasPrice": 1.3,
        "gasLimit": 1.4
    },
    "Fantom": {
        "gasPrice": 1.4,
        "gasLimit": 2.2
    },
    "Optimism": {
        "gasPrice": 1,
        "gasLimit": 2  # TODO
    }
}


class ABI:
    abi_tokens = '[{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'
    abi_stargate = '[{"inputs":[{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"uint256","name":"_srcPoolId","type":"uint256"},{"internalType":"uint256","name":"_dstPoolId","type":"uint256"},{"internalType":"address payable","name":"_refundAddress","type":"address"},{"internalType":"uint256","name":"_amountLD","type":"uint256"},{"internalType":"uint256","name":"_minAmountLD","type":"uint256"},{"components":[{"internalType":"uint256","name":"dstGasForCall","type":"uint256"},{"internalType":"uint256","name":"dstNativeAmount","type":"uint256"},{"internalType":"bytes","name":"dstNativeAddr","type":"bytes"}],"internalType":"struct IStargateRouter.lzTxObj","name":"_lzTxParams","type":"tuple"},{"internalType":"bytes","name":"_to","type":"bytes"},{"internalType":"bytes","name":"_payload","type":"bytes"}],"name":"swap","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"uint8","name":"_functionType","type":"uint8"},{"internalType":"bytes","name":"_toAddress","type":"bytes"},{"internalType":"bytes","name":"_transferAndCallPayload","type":"bytes"},{"components":[{"internalType":"uint256","name":"dstGasForCall","type":"uint256"},{"internalType":"uint256","name":"dstNativeAmount","type":"uint256"},{"internalType":"bytes","name":"dstNativeAddr","type":"bytes"}],"internalType":"struct IStargateRouter.lzTxObj","name":"_lzTxParams","type":"tuple"}],"name":"quoteLayerZeroFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    abi_harmony = '[{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"bytes","name":"_toAddress","type":"bytes"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"address payable","name":"_refundAddress","type":"address"},{"internalType":"address","name":"_zroPaymentAddress","type":"address"},{"internalType":"bytes","name":"_adapterParams","type":"bytes"}],"name":"sendFrom","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"bytes","name":"_toAddress","type":"bytes"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bool","name":"_useZro","type":"bool"},{"internalType":"bytes","name":"_adapterParams","type":"bytes"}],"name":"estimateSendFee","outputs":[{"internalType":"uint256","name":"nativeFee","type":"uint256"},{"internalType":"uint256","name":"zroFee","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    abi_core = '[{"inputs":[{"internalType":"bool","name":"useZro","type":"bool"},{"internalType":"bytes","name":"adapterParams","type":"bytes"}],"name":"estimateBridgeFee","outputs":[{"internalType":"uint256","name":"nativeFee","type":"uint256"},{"internalType":"uint256","name":"zroFee","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountLD","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"components":[{"internalType":"address payable","name":"refundAddress","type":"address"},{"internalType":"address","name":"zroPaymentAddress","type":"address"}],"internalType":"struct LzLib.CallParams","name":"callParams","type":"tuple"},{"internalType":"bytes","name":"adapterParams","type":"bytes"}],"name":"bridge","outputs":[],"stateMutability":"payable","type":"function"}]'
    abi_stg_stake = '[{"inputs":[{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"uint256","name":"_unlock_time","type":"uint256"}],"name":"create_lock","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
    abi_btcb = '[{"inputs":[{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"bytes32","name":"_toAddress","type":"bytes32"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bool","name":"_useZro","type":"bool"},{"internalType":"bytes","name":"_adapterParams","type":"bytes"}],"name":"estimateSendFee","outputs":[{"internalType":"uint256","name":"nativeFee","type":"uint256"},{"internalType":"uint256","name":"zroFee","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"bytes32","name":"_toAddress","type":"bytes32"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_minAmount","type":"uint256"},{"components":[{"internalType":"address payable","name":"refundAddress","type":"address"},{"internalType":"address","name":"zroPaymentAddress","type":"address"},{"internalType":"bytes","name":"adapterParams","type":"bytes"}],"internalType":"struct ICommonOFT.LzCallParams","name":"_callParams","type":"tuple"}],"name":"sendFrom","outputs":[],"stateMutability":"payable","type":"function"}]'
    abi_from_core = '[{"inputs":[{"name":"_endpoint","internalType":"address","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"indexed":false,"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"_srcAddress","internalType":"bytes","type":"bytes"},{"indexed":false,"name":"_nonce","internalType":"uint64","type":"uint64"},{"indexed":false,"name":"_payload","internalType":"bytes","type":"bytes"},{"indexed":false,"name":"_reason","internalType":"bytes","type":"bytes"}],"name":"MessageFailed","anonymous":false,"type":"event"},{"inputs":[{"indexed":true,"name":"previousOwner","internalType":"address","type":"address"},{"indexed":true,"name":"newOwner","internalType":"address","type":"address"}],"name":"OwnershipTransferred","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"localToken","internalType":"address","type":"address"},{"indexed":false,"name":"remoteChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"remoteToken","internalType":"address","type":"address"}],"name":"RegisterToken","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"_srcAddress","internalType":"bytes","type":"bytes"},{"indexed":false,"name":"_nonce","internalType":"uint64","type":"uint64"},{"indexed":false,"name":"_payloadHash","internalType":"bytes32","type":"bytes32"}],"name":"RetryMessageSuccess","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"_dstChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"_type","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"_minDstGas","internalType":"uint256","type":"uint256"}],"name":"SetMinDstGas","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"precrime","internalType":"address","type":"address"}],"name":"SetPrecrime","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"_remoteChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"_path","internalType":"bytes","type":"bytes"}],"name":"SetTrustedRemote","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"_remoteChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"_remoteAddress","internalType":"bytes","type":"bytes"}],"name":"SetTrustedRemoteAddress","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"useCustomAdapterParams","internalType":"bool","type":"bool"}],"name":"SetUseCustomAdapterParams","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"withdrawalFeeBps","internalType":"uint16","type":"uint16"}],"name":"SetWithdrawalFeeBps","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"localToken","internalType":"address","type":"address"},{"indexed":false,"name":"remoteToken","internalType":"address","type":"address"},{"indexed":false,"name":"remoteChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"to","internalType":"address","type":"address"},{"indexed":false,"name":"amount","internalType":"uint256","type":"uint256"}],"name":"UnwrapToken","anonymous":false,"type":"event"},{"inputs":[{"indexed":false,"name":"localToken","internalType":"address","type":"address"},{"indexed":false,"name":"remoteToken","internalType":"address","type":"address"},{"indexed":false,"name":"remoteChainId","internalType":"uint16","type":"uint16"},{"indexed":false,"name":"to","internalType":"address","type":"address"},{"indexed":false,"name":"amount","internalType":"uint256","type":"uint256"}],"name":"WrapToken","anonymous":false,"type":"event"},{"outputs":[{"name":"","internalType":"uint8","type":"uint8"}],"inputs":[],"name":"PT_MINT","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"uint8","type":"uint8"}],"inputs":[],"name":"PT_UNLOCK","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"uint16","type":"uint16"}],"inputs":[],"name":"TOTAL_BPS","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[{"name":"localToken","internalType":"address","type":"address"},{"name":"remoteChainId","internalType":"uint16","type":"uint16"},{"name":"amount","internalType":"uint256","type":"uint256"},{"name":"to","internalType":"address","type":"address"},{"name":"unwrapWeth","internalType":"bool","type":"bool"},{"components":[{"name":"refundAddress","internalType":"address payable","type":"address"},{"name":"zroPaymentAddress","internalType":"address","type":"address"}],"name":"callParams","internalType":"struct LzLib.CallParams","type":"tuple"},{"name":"adapterParams","internalType":"bytes","type":"bytes"}],"name":"bridge","stateMutability":"payable","type":"function"},{"outputs":[{"name":"nativeFee","internalType":"uint256","type":"uint256"},{"name":"zroFee","internalType":"uint256","type":"uint256"}],"inputs":[{"name":"remoteChainId","internalType":"uint16","type":"uint16"},{"name":"useZro","internalType":"bool","type":"bool"},{"name":"adapterParams","internalType":"bytes","type":"bytes"}],"name":"estimateBridgeFee","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"bytes32","type":"bytes32"}],"inputs":[{"name":"","internalType":"uint16","type":"uint16"},{"name":"","internalType":"bytes","type":"bytes"},{"name":"","internalType":"uint64","type":"uint64"}],"name":"failedMessages","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[{"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"name":"_srcAddress","internalType":"bytes","type":"bytes"}],"name":"forceResumeReceive","stateMutability":"nonpayable","type":"function"},{"outputs":[{"name":"","internalType":"bytes","type":"bytes"}],"inputs":[{"name":"_version","internalType":"uint16","type":"uint16"},{"name":"_chainId","internalType":"uint16","type":"uint16"},{"name":"","internalType":"address","type":"address"},{"name":"_configType","internalType":"uint256","type":"uint256"}],"name":"getConfig","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"bytes","type":"bytes"}],"inputs":[{"name":"_remoteChainId","internalType":"uint16","type":"uint16"}],"name":"getTrustedRemoteAddress","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"bool","type":"bool"}],"inputs":[{"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"name":"_srcAddress","internalType":"bytes","type":"bytes"}],"name":"isTrustedRemote","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"address","type":"address"}],"inputs":[{"name":"","internalType":"address","type":"address"},{"name":"","internalType":"uint16","type":"uint16"}],"name":"localToRemote","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"contract ILayerZeroEndpoint","type":"address"}],"inputs":[],"name":"lzEndpoint","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[{"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"name":"_srcAddress","internalType":"bytes","type":"bytes"},{"name":"_nonce","internalType":"uint64","type":"uint64"},{"name":"_payload","internalType":"bytes","type":"bytes"}],"name":"lzReceive","stateMutability":"nonpayable","type":"function"},{"outputs":[{"name":"","internalType":"uint256","type":"uint256"}],"inputs":[{"name":"","internalType":"uint16","type":"uint16"},{"name":"","internalType":"uint16","type":"uint16"}],"name":"minDstGasLookup","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[{"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"name":"_srcAddress","internalType":"bytes","type":"bytes"},{"name":"_nonce","internalType":"uint64","type":"uint64"},{"name":"_payload","internalType":"bytes","type":"bytes"}],"name":"nonblockingLzReceive","stateMutability":"nonpayable","type":"function"},{"outputs":[{"name":"","internalType":"address","type":"address"}],"inputs":[],"name":"owner","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"address","type":"address"}],"inputs":[],"name":"precrime","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[{"name":"localToken","internalType":"address","type":"address"},{"name":"remoteChainId","internalType":"uint16","type":"uint16"},{"name":"remoteToken","internalType":"address","type":"address"}],"name":"registerToken","stateMutability":"nonpayable","type":"function"},{"outputs":[{"name":"","internalType":"address","type":"address"}],"inputs":[{"name":"","internalType":"address","type":"address"},{"name":"","internalType":"uint16","type":"uint16"}],"name":"remoteToLocal","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[],"name":"renounceOwnership","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"name":"_srcAddress","internalType":"bytes","type":"bytes"},{"name":"_nonce","internalType":"uint64","type":"uint64"},{"name":"_payload","internalType":"bytes","type":"bytes"}],"name":"retryMessage","stateMutability":"payable","type":"function"},{"outputs":[],"inputs":[{"name":"_version","internalType":"uint16","type":"uint16"},{"name":"_chainId","internalType":"uint16","type":"uint16"},{"name":"_configType","internalType":"uint256","type":"uint256"},{"name":"_config","internalType":"bytes","type":"bytes"}],"name":"setConfig","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_dstChainId","internalType":"uint16","type":"uint16"},{"name":"_packetType","internalType":"uint16","type":"uint16"},{"name":"_minGas","internalType":"uint256","type":"uint256"}],"name":"setMinDstGas","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_precrime","internalType":"address","type":"address"}],"name":"setPrecrime","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_version","internalType":"uint16","type":"uint16"}],"name":"setReceiveVersion","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_version","internalType":"uint16","type":"uint16"}],"name":"setSendVersion","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_srcChainId","internalType":"uint16","type":"uint16"},{"name":"_path","internalType":"bytes","type":"bytes"}],"name":"setTrustedRemote","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_remoteChainId","internalType":"uint16","type":"uint16"},{"name":"_remoteAddress","internalType":"bytes","type":"bytes"}],"name":"setTrustedRemoteAddress","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_useCustomAdapterParams","internalType":"bool","type":"bool"}],"name":"setUseCustomAdapterParams","stateMutability":"nonpayable","type":"function"},{"outputs":[],"inputs":[{"name":"_withdrawalFeeBps","internalType":"uint16","type":"uint16"}],"name":"setWithdrawalFeeBps","stateMutability":"nonpayable","type":"function"},{"outputs":[{"name":"","internalType":"uint256","type":"uint256"}],"inputs":[{"name":"","internalType":"uint16","type":"uint16"},{"name":"","internalType":"address","type":"address"}],"name":"totalValueLocked","stateMutability":"view","type":"function"},{"outputs":[],"inputs":[{"name":"newOwner","internalType":"address","type":"address"}],"name":"transferOwnership","stateMutability":"nonpayable","type":"function"},{"outputs":[{"name":"","internalType":"bytes","type":"bytes"}],"inputs":[{"name":"","internalType":"uint16","type":"uint16"}],"name":"trustedRemoteLookup","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"bool","type":"bool"}],"inputs":[],"name":"useCustomAdapterParams","stateMutability":"view","type":"function"},{"outputs":[{"name":"","internalType":"uint16","type":"uint16"}],"inputs":[],"name":"withdrawalFeeBps","stateMutability":"view","type":"function"}]'
    abi_testnet = '[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"uint16","name":"dstChainId","type":"uint16"},{"internalType":"address","name":"to","type":"address"},{"internalType":"address payable","name":"refundAddress","type":"address"},{"internalType":"address","name":"zroPaymentAddress","type":"address"},{"internalType":"bytes","name":"adapterParams","type":"bytes"}],"name":"swapAndBridge","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"_dstChainId","type":"uint16"},{"internalType":"bytes","name":"_toAddress","type":"bytes"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bool","name":"_useZro","type":"bool"},{"internalType":"bytes","name":"_adapterParams","type":"bytes"}],"name":"estimateSendFee","outputs":[{"internalType":"uint256","name":"nativeFee","type":"uint256"},{"internalType":"uint256","name":"zroFee","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    abi_aptos = '[{"inputs":[{"internalType":"address","name":"_token","type":"address"},{"internalType":"bytes32","name":"_toAddress","type":"bytes32"},{"internalType":"uint256","name":"_amountLD","type":"uint256"},{"components":[{"internalType":"address payable","name":"refundAddress","type":"address"},{"internalType":"address","name":"zroPaymentAddress","type":"address"}],"internalType":"struct LzLib.CallParams","name":"_callParams","type":"tuple"},{"internalType":"bytes","name":"_adapterParams","type":"bytes"}],"name":"sendToAptos","outputs":[],"stateMutability":"payable","type":"function"}, {"inputs":[{"components":[{"internalType":"address payable","name":"refundAddress","type":"address"},{"internalType":"address","name":"zroPaymentAddress","type":"address"}],"internalType":"struct LzLib.CallParams","name":"_callParams","type":"tuple"},{"internalType":"bytes","name":"_adapterParams","type":"bytes"}],"name":"quoteForSend","outputs":[{"internalType":"uint256","name":"nativeFee","type":"uint256"},{"internalType":"uint256","name":"zroFee","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    abi_sushi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
    abi_woofi_swap = '[{"inputs":[{"internalType":"address","name":"_weth","type":"address"},{"internalType":"address","name":"_pool","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newPool","type":"address"}],"name":"WooPoolChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"enum IWooRouterV2.SwapType","name":"swapType","type":"uint8"},{"indexed":true,"internalType":"address","name":"fromToken","type":"address"},{"indexed":true,"internalType":"address","name":"toToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"fromAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"toAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"address","name":"rebateTo","type":"address"}],"name":"WooRouterSwap","type":"event"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"approveTarget","type":"address"},{"internalType":"address","name":"swapTarget","type":"address"},{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"internalType":"uint256","name":"minToAmount","type":"uint256"},{"internalType":"address payable","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"externalSwap","outputs":[{"internalType":"uint256","name":"realToAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"stuckToken","type":"address"}],"name":"inCaseTokenGotStuck","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"isWhitelisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"}],"name":"querySwap","outputs":[{"internalType":"uint256","name":"toAmount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"quoteToken","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newPool","type":"address"}],"name":"setPool","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"whitelisted","type":"bool"}],"name":"setWhitelisted","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"internalType":"uint256","name":"minToAmount","type":"uint256"},{"internalType":"address payable","name":"to","type":"address"},{"internalType":"address","name":"rebateTo","type":"address"}],"name":"swap","outputs":[{"internalType":"uint256","name":"realToAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"}],"name":"tryQuerySwap","outputs":[{"internalType":"uint256","name":"toAmount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"wooPool","outputs":[{"internalType":"contract IWooPPV2","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]'
    abi_jumper = '[{"inputs":[{"internalType":"bytes32","name":"_transactionId","type":"bytes32"},{"internalType":"string","name":"_integrator","type":"string"},{"internalType":"string","name":"_referrer","type":"string"},{"internalType":"address payable","name":"_receiver","type":"address"},{"internalType":"uint256","name":"_minAmount","type":"uint256"},{"components":[{"internalType":"address","name":"callTo","type":"address"},{"internalType":"address","name":"approveTo","type":"address"},{"internalType":"address","name":"sendingAssetId","type":"address"},{"internalType":"address","name":"receivingAssetId","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"internalType":"bytes","name":"callData","type":"bytes"},{"internalType":"bool","name":"requiresDeposit","type":"bool"}],"internalType":"struct LibSwap.SwapData[]","name":"_swapData","type":"tuple[]"}],"name":"swapTokensGeneric","outputs":[],"stateMutability":"payable","type":"function"}]'


    BTCB_ABI = json.loads('''
    [
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "_lzEndpoint",
            "type": "address"
        }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": true,
            "internalType": "address",
            "name": "owner",
            "type": "address"
        },
        {
            "indexed": true,
            "internalType": "address",
            "name": "spender",
            "type": "address"
        },
        {
            "indexed": false,
            "internalType": "uint256",
            "name": "value",
            "type": "uint256"
        }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": true,
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "indexed": false,
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "indexed": false,
            "internalType": "bytes32",
            "name": "_hash",
            "type": "bytes32"
        }
        ],
        "name": "CallOFTReceivedSuccess",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "indexed": false,
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_reason",
            "type": "bytes"
        }
        ],
        "name": "MessageFailed",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "address",
            "name": "_address",
            "type": "address"
        }
        ],
        "name": "NonContractAddress",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": true,
            "internalType": "address",
            "name": "previousOwner",
            "type": "address"
        },
        {
            "indexed": true,
            "internalType": "address",
            "name": "newOwner",
            "type": "address"
        }
        ],
        "name": "OwnershipTransferred",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": true,
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "indexed": true,
            "internalType": "address",
            "name": "_to",
            "type": "address"
        },
        {
            "indexed": false,
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        }
        ],
        "name": "ReceiveFromChain",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "indexed": false,
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "indexed": false,
            "internalType": "bytes32",
            "name": "_payloadHash",
            "type": "bytes32"
        }
        ],
        "name": "RetryMessageSuccess",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": true,
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "indexed": true,
            "internalType": "address",
            "name": "_from",
            "type": "address"
        },
        {
            "indexed": true,
            "internalType": "bytes32",
            "name": "_toAddress",
            "type": "bytes32"
        },
        {
            "indexed": false,
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        }
        ],
        "name": "SendToChain",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "feeBp",
            "type": "uint16"
        }
        ],
        "name": "SetDefaultFeeBp",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "dstchainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "bool",
            "name": "enabled",
            "type": "bool"
        },
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "feeBp",
            "type": "uint16"
        }
        ],
        "name": "SetFeeBp",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "address",
            "name": "feeOwner",
            "type": "address"
        }
        ],
        "name": "SetFeeOwner",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "_type",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "uint256",
            "name": "_minDstGas",
            "type": "uint256"
        }
        ],
        "name": "SetMinDstGas",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "address",
            "name": "precrime",
            "type": "address"
        }
        ],
        "name": "SetPrecrime",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "_remoteChainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_path",
            "type": "bytes"
        }
        ],
        "name": "SetTrustedRemote",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "uint16",
            "name": "_remoteChainId",
            "type": "uint16"
        },
        {
            "indexed": false,
            "internalType": "bytes",
            "name": "_remoteAddress",
            "type": "bytes"
        }
        ],
        "name": "SetTrustedRemoteAddress",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": false,
            "internalType": "bool",
            "name": "_useCustomAdapterParams",
            "type": "bool"
        }
        ],
        "name": "SetUseCustomAdapterParams",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
        {
            "indexed": true,
            "internalType": "address",
            "name": "from",
            "type": "address"
        },
        {
            "indexed": true,
            "internalType": "address",
            "name": "to",
            "type": "address"
        },
        {
            "indexed": false,
            "internalType": "uint256",
            "name": "value",
            "type": "uint256"
        }
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "BP_DENOMINATOR",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "NO_EXTRA_GAS",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "PT_SEND",
        "outputs": [
        {
            "internalType": "uint8",
            "name": "",
            "type": "uint8"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "PT_SEND_AND_CALL",
        "outputs": [
        {
            "internalType": "uint8",
            "name": "",
            "type": "uint8"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "owner",
            "type": "address"
        },
        {
            "internalType": "address",
            "name": "spender",
            "type": "address"
        }
        ],
        "name": "allowance",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "spender",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
        }
        ],
        "name": "approve",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "account",
            "type": "address"
        }
        ],
        "name": "balanceOf",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "internalType": "bytes32",
            "name": "_from",
            "type": "bytes32"
        },
        {
            "internalType": "address",
            "name": "_to",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        },
        {
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        },
        {
            "internalType": "uint256",
            "name": "_gasForCall",
            "type": "uint256"
        }
        ],
        "name": "callOnOFTReceived",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        }
        ],
        "name": "chainIdToFeeBps",
        "outputs": [
        {
            "internalType": "uint16",
            "name": "feeBP",
            "type": "uint16"
        },
        {
            "internalType": "bool",
            "name": "enabled",
            "type": "bool"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "circulatingSupply",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "",
            "type": "uint64"
        }
        ],
        "name": "creditedPackets",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
        {
            "internalType": "uint8",
            "name": "",
            "type": "uint8"
        }
        ],
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "spender",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "subtractedValue",
            "type": "uint256"
        }
        ],
        "name": "decreaseAllowance",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "defaultFeeBp",
        "outputs": [
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes32",
            "name": "_toAddress",
            "type": "bytes32"
        },
        {
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        },
        {
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "_dstGasForCall",
            "type": "uint64"
        },
        {
            "internalType": "bool",
            "name": "_useZro",
            "type": "bool"
        },
        {
            "internalType": "bytes",
            "name": "_adapterParams",
            "type": "bytes"
        }
        ],
        "name": "estimateSendAndCallFee",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "nativeFee",
            "type": "uint256"
        },
        {
            "internalType": "uint256",
            "name": "zroFee",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes32",
            "name": "_toAddress",
            "type": "bytes32"
        },
        {
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        },
        {
            "internalType": "bool",
            "name": "_useZro",
            "type": "bool"
        },
        {
            "internalType": "bytes",
            "name": "_adapterParams",
            "type": "bytes"
        }
        ],
        "name": "estimateSendFee",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "nativeFee",
            "type": "uint256"
        },
        {
            "internalType": "uint256",
            "name": "zroFee",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "",
            "type": "uint64"
        }
        ],
        "name": "failedMessages",
        "outputs": [
        {
            "internalType": "bytes32",
            "name": "",
            "type": "bytes32"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "feeOwner",
        "outputs": [
        {
            "internalType": "address",
            "name": "",
            "type": "address"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        }
        ],
        "name": "forceResumeReceive",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_version",
            "type": "uint16"
        },
        {
            "internalType": "uint16",
            "name": "_chainId",
            "type": "uint16"
        },
        {
            "internalType": "address",
            "name": "",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "_configType",
            "type": "uint256"
        }
        ],
        "name": "getConfig",
        "outputs": [
        {
            "internalType": "bytes",
            "name": "",
            "type": "bytes"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_remoteChainId",
            "type": "uint16"
        }
        ],
        "name": "getTrustedRemoteAddress",
        "outputs": [
        {
            "internalType": "bytes",
            "name": "",
            "type": "bytes"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "spender",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "addedValue",
            "type": "uint256"
        }
        ],
        "name": "increaseAllowance",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        }
        ],
        "name": "isTrustedRemote",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "lzEndpoint",
        "outputs": [
        {
            "internalType": "contract ILayerZeroEndpoint",
            "name": "",
            "type": "address"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        }
        ],
        "name": "lzReceive",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        },
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        }
        ],
        "name": "minDstGasLookup",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
        {
            "internalType": "string",
            "name": "",
            "type": "string"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        }
        ],
        "name": "nonblockingLzReceive",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
        {
            "internalType": "address",
            "name": "",
            "type": "address"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "precrime",
        "outputs": [
        {
            "internalType": "address",
            "name": "",
            "type": "address"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        }
        ],
        "name": "quoteOFTFee",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "fee",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_srcAddress",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "_nonce",
            "type": "uint64"
        },
        {
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        }
        ],
        "name": "retryMessage",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "_from",
            "type": "address"
        },
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes32",
            "name": "_toAddress",
            "type": "bytes32"
        },
        {
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        },
        {
            "internalType": "uint256",
            "name": "_minAmount",
            "type": "uint256"
        },
        {
            "internalType": "bytes",
            "name": "_payload",
            "type": "bytes"
        },
        {
            "internalType": "uint64",
            "name": "_dstGasForCall",
            "type": "uint64"
        },
        {
            "components": [
            {
                "internalType": "address payable",
                "name": "refundAddress",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "zroPaymentAddress",
                "type": "address"
            },
            {
                "internalType": "bytes",
                "name": "adapterParams",
                "type": "bytes"
            }
            ],
            "internalType": "struct ICommonOFT.LzCallParams",
            "name": "_callParams",
            "type": "tuple"
        }
        ],
        "name": "sendAndCall",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "_from",
            "type": "address"
        },
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes32",
            "name": "_toAddress",
            "type": "bytes32"
        },
        {
            "internalType": "uint256",
            "name": "_amount",
            "type": "uint256"
        },
        {
            "internalType": "uint256",
            "name": "_minAmount",
            "type": "uint256"
        },
        {
            "components": [
            {
                "internalType": "address payable",
                "name": "refundAddress",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "zroPaymentAddress",
                "type": "address"
            },
            {
                "internalType": "bytes",
                "name": "adapterParams",
                "type": "bytes"
            }
            ],
            "internalType": "struct ICommonOFT.LzCallParams",
            "name": "_callParams",
            "type": "tuple"
        }
        ],
        "name": "sendFrom",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_version",
            "type": "uint16"
        },
        {
            "internalType": "uint16",
            "name": "_chainId",
            "type": "uint16"
        },
        {
            "internalType": "uint256",
            "name": "_configType",
            "type": "uint256"
        },
        {
            "internalType": "bytes",
            "name": "_config",
            "type": "bytes"
        }
        ],
        "name": "setConfig",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_feeBp",
            "type": "uint16"
        }
        ],
        "name": "setDefaultFeeBp",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "bool",
            "name": "_enabled",
            "type": "bool"
        },
        {
            "internalType": "uint16",
            "name": "_feeBp",
            "type": "uint16"
        }
        ],
        "name": "setFeeBp",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "_feeOwner",
            "type": "address"
        }
        ],
        "name": "setFeeOwner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_dstChainId",
            "type": "uint16"
        },
        {
            "internalType": "uint16",
            "name": "_packetType",
            "type": "uint16"
        },
        {
            "internalType": "uint256",
            "name": "_minGas",
            "type": "uint256"
        }
        ],
        "name": "setMinDstGas",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "_precrime",
            "type": "address"
        }
        ],
        "name": "setPrecrime",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_version",
            "type": "uint16"
        }
        ],
        "name": "setReceiveVersion",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_version",
            "type": "uint16"
        }
        ],
        "name": "setSendVersion",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_srcChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_path",
            "type": "bytes"
        }
        ],
        "name": "setTrustedRemote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "_remoteChainId",
            "type": "uint16"
        },
        {
            "internalType": "bytes",
            "name": "_remoteAddress",
            "type": "bytes"
        }
        ],
        "name": "setTrustedRemoteAddress",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "bool",
            "name": "_useCustomAdapterParams",
            "type": "bool"
        }
        ],
        "name": "setUseCustomAdapterParams",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "sharedDecimals",
        "outputs": [
        {
            "internalType": "uint8",
            "name": "",
            "type": "uint8"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "bytes4",
            "name": "interfaceId",
            "type": "bytes4"
        }
        ],
        "name": "supportsInterface",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
        {
            "internalType": "string",
            "name": "",
            "type": "string"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "token",
        "outputs": [
        {
            "internalType": "address",
            "name": "",
            "type": "address"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "to",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
        }
        ],
        "name": "transfer",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "from",
            "type": "address"
        },
        {
            "internalType": "address",
            "name": "to",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
        }
        ],
        "name": "transferFrom",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "address",
            "name": "newOwner",
            "type": "address"
        }
        ],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {
            "internalType": "uint16",
            "name": "",
            "type": "uint16"
        }
        ],
        "name": "trustedRemoteLookup",
        "outputs": [
        {
            "internalType": "bytes",
            "name": "",
            "type": "bytes"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "useCustomAdapterParams",
        "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    }
    ]
    ''')

    ERC20_ABI = json.loads('''
[
    {
        "constant": true,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "_from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "_to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "_owner",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "_spender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "NAME",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "SYMBOL",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "DECIMALS",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
''')
