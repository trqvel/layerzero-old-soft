import requests
import time
import math

from functools import lru_cache
from decimal import Decimal

from config import buy_stg_amount
from web3 import Web3
from web3 import Account
from modules.data_storage import *
import datetime
import random
from dateutil.relativedelta import relativedelta


def get_token_decimals(network, token_name):
    network = network.strip()
    token_name = token_name.strip().upper()
    network_tokens = data_decimals.get(network)
    decimals = network_tokens.get(token_name.upper())
    if decimals is None:
        print_with_time(f"  Network: {network}, Token name: {token_name}")
    elif decimals == 0:
        print_with_time(f"  Decimals for token {token_name} on network {network} is 0")
        raise ValueError(
            f"  Не знаю такой токен {network} {token_name}, чтобы получить decimal [function: get_token_decimals]")
    return decimals


def get_network_format(network, exchange):

    if network not in data_network_id:
        raise ValueError(f"  Неизвестная сеть: {network} [function: get_network_format]")

    if exchange not in data_network_id[network]:
        raise ValueError(f"  Неизвестная биржа: {exchange} [function: get_network_format]")

    return data_network_id[network][exchange]


def get_unlock_time(months):
    now = datetime.datetime.now()
    unlock_date = now + relativedelta(months=months) - datetime.timedelta(days=1)
    unlock_date = unlock_date.replace(hour=3, minute=0, second=0, microsecond=0)  # установите время разблокировки на начало дня
    unlock_datetime = int(unlock_date.timestamp())
    if unlock_datetime > 0:
        return unlock_datetime
    else:
        print(f'  Ошибка при получении времени для стейкинга STG, установите текущую дату на компьютере | unlock_datetime: {unlock_datetime}')
        return


def get_token_swap_code(from_token_name, to_token_name):
    token_codes = {
        "USDC": 1,
        "USDT": 2,
    }

    from_token_code = token_codes.get(from_token_name.upper())
    to_token_code = token_codes.get(to_token_name.upper())

    if from_token_code is None or to_token_code is None:
        raise ValueError("  Не могу получить код токена для Stargate  [function: get_token_swap_code]")

    return from_token_code, to_token_code


def get_address_wallet(private_key):
    if private_key.startswith("0x"):
        private_key = private_key[2:]
    account = Account.from_key(private_key)
    return account.address


@lru_cache(maxsize=None)
def get_value_stg(from_chain, to_chain):
    from_chain_info = data_blockchains[from_chain]
    to_chain_info = data_blockchains[to_chain]
    available_rpc = from_chain_info["rpc"]
    to_chain_id = to_chain_info["chain_id"]

    stargate_contract_address = from_chain_info["stargate_bridge_contract"]
    payload = b''
    lz_tx_params = {
        'dstGasForCall': 0,
        'dstNativeAmount': 0,
        'dstNativeAddr': bytes.fromhex('0000000000000000000000000000000000000001')
    }

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = web3.eth.contract(address=web3.to_checksum_address(stargate_contract_address), abi=ABI.abi_stargate)
            get_value = contract.functions.quoteLayerZeroFee(
                to_chain_id,
                1,
                "0x0000000000000000000000000000000000000001",
                payload,
                lz_tx_params
            ).call()
            value = get_value[0]

            return value
        except Exception as error:
            print_with_time(f"  Не удалось получить value {from_chain} -> {to_chain} [get_value_stg]")
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_value_stg] | {from_chain} to {to_chain}")


@lru_cache(maxsize=None)
def get_value_harmony(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]

    contract_address = "0x8d1ebcda83fd905b597bf6d3294766b64ecf2aa7"
    dst_chain_id = 116
    useZRO = True
    adapterParams = "0x0001000000000000000000000000000000000000000000000000000000000007a120"

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=ABI.abi_harmony)
            get_value = contract.functions.estimateSendFee(
                dst_chain_id,
                "0x303175c889263D8fD7Bc95887a0cE92A93AEe671",
                1,
                useZRO,
                adapterParams
            ).call()
            value = get_value[0]

            return value
        except Exception as error:
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_value_harmony] | {from_chain}")


@lru_cache(maxsize=None)
def get_value_in_core(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]

    contract_address = from_chain_info["core_bridge_contract"]
    useZRO = False

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=ABI.abi_core)
            get_value = contract.functions.estimateBridgeFee(useZRO, bytes()).call()
            value = get_value[0]

            return value
        except Exception as error:
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_value_in_core] | {from_chain}")


@lru_cache(maxsize=None)
def get_value_aptos(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]

    aptos_address = "0xa399684d4ee2484ad564ccb5659273beea4807a715a8345fe506fb4a63a98c76"
    contract_address = from_chain_info["aptos_contract"]
    call_params = {'refundAddress': "0x303175c889263D8fD7Bc95887a0cE92A93AEe671", 'zroPaymentAddress': "0x0000000000000000000000000000000000000000"}
    adapter_params = f"0x000200000000000000000000000000000000000000000000000000000000000027100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000{aptos_address[2:]}"

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=ABI.abi_aptos)
            get_value = contract.functions.quoteForSend(call_params, adapter_params).call()
            value = get_value[0]

            return value
        except Exception as error:
            print(error)
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_value_aptos] | {from_chain}")


@lru_cache(maxsize=None)
def get_value_testnet(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]

    contractGetFee_address = from_chain_info["testnetGetFee_contract"]
    useZRO = False

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract_get_fee = web3.eth.contract(address=web3.to_checksum_address(contractGetFee_address), abi=ABI.abi_testnet)
            get_value = contract_get_fee.functions.estimateSendFee(
                154,
                "0x303175c889263D8fD7Bc95887a0cE92A93AEe671",
                0,
                useZRO,
                b''
            ).call()
            value = int(get_value[0] * 1.5)

            return value
        except Exception as error:
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_value_testnet] | {from_chain}")


@lru_cache(maxsize=None)
def get_value_out_core(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]

    contract_address = from_chain_info["core_bridge_contract"]
    useZRO = False

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=ABI.abi_from_core)
            get_value = contract.functions.estimateBridgeFee(102, useZRO, b'').call()
            value = get_value[0]

            return value
        except Exception as error:
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_value_out_core] | {from_chain}")


@lru_cache(maxsize=None)
def get_value_approve(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]

    contract_address = from_chain_info["usdc_contract"]
    random_address = "0x0000000000000000000000000000000000000001"

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=ABI.abi_tokens)
            contract_txn = contract.functions.approve(random_address, 0)
            gas_estimate = contract_txn.estimate_gas({'from': random_address})

            gas_price = web3.eth.gas_price
            transaction_cost = gas_estimate * gas_price

            return transaction_cost
        except Exception as error:
            print(error)
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку. [get_value_approve] | {from_chain}")


@lru_cache(maxsize=None)
def get_current_gas_price(from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = from_chain_info["rpc"]
    gas_limit = data_gas_limit[from_chain]

    for rpc_url in available_rpc:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            gas_price = web3.eth.gas_price
            gas = int(gas_price * gas_limit)
            return gas
        except Exception as error:
            pass

    raise Exception(f"  Все доступные RPC-URL вызвали ошибку [get_current_gas_price] | {from_chain}")


def get_status_by_api(transaction_hash, private_key):
    base_url = "https://api-mainnet.layerzero-scan.com/tx/"
    transaction_url = base_url + transaction_hash

    response = requests.get(transaction_url)
    if response.status_code == 200:
        transaction_data = response.json()
        if transaction_data["messages"]:
            status = transaction_data["messages"][0]["status"]

            if status in ["INFLIGHT", "PENDING"]:
                print_with_time(f'  Транзакция {transaction_hash} все еще в ожидании, ждем еще немного...')
                print(f'          {get_address_wallet(private_key)}')
                time.sleep(random.uniform(10, 30))
            elif status == "DELIVERED":
                return True
            elif status == "FAILED":
                return False
        else:
            time.sleep(random.uniform(10, 30))
    else:
        time.sleep(random.uniform(10, 30))


def get_transaction_status(transaction_hash,private_key):
    while True:
        api_status = get_status_by_api(transaction_hash,private_key)

        if api_status:
            return True


def smart_round(number):
    if isinstance(number, (int, float, Decimal)):
        abs_num = abs(number)
        if abs_num == 0:
            return 0
        elif abs_num >= 1:
            return round(number, 2)
        elif 0 < abs_num < 1e-4:
            return "{:.8f}".format(number)
        else:
            return round(number, 3 - int(math.floor(math.log10(abs_num)) + 1))
    else:
        raise ValueError("    Функция принимает только числа (целые и с плавающей точкой) [function smart_round]")


def load_wallets():
    try:
        with open("private_keys.txt", "r") as f:
            return [row.strip() for row in f if row.strip()]
    except FileNotFoundError:
        print_with_time(
            "Файл 'private_keys.txt' не найден. Пожалуйста, поместите файл с приватными ключами кошельков в корневую папку проекта.")
        exit(1)


def load_withdrawal_addresses(wallets_list):
    try:
        with open("withdrawal_address.txt", "r") as f:
            withdrawal_addresses = [row.strip() for row in f if row.strip()]

        if len(wallets_list) != len(withdrawal_addresses):
            raise ValueError(
                "Количество адресов в withdrawal_address.txt должно совпадать с количеством приватных ключей в wallets.txt")

        return dict(zip(wallets_list, withdrawal_addresses))
    except FileNotFoundError:
        print(
            "Файл 'withdrawal_address.txt' не найден. Выключите withdrawal_out в config.py или поместите файл в корень проекта")
        exit(1)


def load_aptos_addresses(wallets_list):
    try:
        with open("aptos_address.txt", "r") as f:
            withdrawal_addresses = [row.strip() for row in f if row.strip()]

        if len(wallets_list) != len(withdrawal_addresses):
            raise ValueError(
                "Количество адресов в aptos.txt должно совпадать с количеством приватных ключей в wallets.txt")

        return dict(zip(wallets_list, withdrawal_addresses))
    except FileNotFoundError:
        print(
            "Файл 'aptos_address.txt' не найден. Выключите use_aptos в config.py или поместите файл в корень проекта")
        exit(1)


def process_wallet_data(wallet_address):
    with open(f'logs/paths/{wallet_address}.json', 'r') as file:
        wallet_data = json.load(file)

    bridge_count = 0
    amount_in = 0

    for item in wallet_data:
        if item['type'] == 'Bridge' and item['project'] == 'Stargate':
            bridge_count += 1
        elif item['type'] == 'Bridge' and item['project'] == 'Core':
            bridge_count += 1
        if item['project'] == 'amount in':
            amount_in = item['amount']
        if item['project'] == 'native':
            native = item['amount']

    return bridge_count, amount_in * bridge_count, native


def get_withdrawal_address(wallet_address):
    with open(f'logs/paths/{wallet_address}.json', 'r') as file:
        wallet_data = json.load(file)

    withdrawal_address = None
    for item in wallet_data:
        if item['project'] == 'amount out':
            withdrawal_address = item['address']
            break

    return withdrawal_address


def get_adapter_params(gas_amount, native_gas_amount, destination_address):
    version = 2
    version_hex = hex(version)[2:].rjust(4, '0')
    gas_amount_hex = hex(gas_amount)[2:].rjust(64, '0')
    native_gas_amount_hex = hex(native_gas_amount)[2:].rjust(64, '0')
    destination_address_hex = destination_address[2:].rjust(64, '0')

    formatted_params = version_hex + gas_amount_hex + native_gas_amount_hex + destination_address_hex

    return formatted_params


def get_native_token_balance(private_key, network):
    available_rpc = get_valid_rpc(network)
    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        account = web3.eth.account.from_key(private_key)
    except ValueError as e:
        raise ValueError(f"  Недействительный приватный ключ: {private_key}") from e

    address = account.address
    balance_wei = web3.eth.get_balance(address)
    balance = round(web3.from_wei(balance_wei, 'ether'), 6)
    return balance


def delay(delay_txn):
    time.sleep(random.uniform(delay_txn[0], delay_txn[1]))


def delayTh(delay_threads):
    time.sleep(random.uniform(delay_threads[0], delay_threads[1]))


def update_status_and_write(paths, file_path, i, status, txn_hash=None):
    paths[i]["status"] = status
    if txn_hash:
        paths[i]["hash"] = txn_hash
    with open(file_path, "w") as f:
        json.dump(paths, f)


def print_with_time(msg):
    current_time = datetime.datetime.now().strftime('[%H:%M]')
    print(f'\n{current_time} {msg}')


def get_stake_stg_status(private_key, from_chain):
    from_chain_info = data_blockchains[from_chain]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        contract_address = Web3.to_checksum_address(from_chain_info["stg_stake_contract"])
        contract = web3.eth.contract(address=contract_address, abi=ABI.abi_tokens)
        balanceOf = contract.functions.balanceOf(address_wallet).call()

        token_contract_address = Web3.to_checksum_address(from_chain_info["stg_contract"])
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        amount = token_contract.functions.balanceOf(address_wallet).call()

        if balanceOf == 0 or amount >= int(buy_stg_amount[0] * 10 ** 18):
            return True
        return False

    except ValueError as e:
        return False


def check_proxy(proxy):
    try:
        r = requests.get('https://ifconfig.co/', proxies={"http": proxy, "https": proxy}, timeout=15)
        if r.status_code == 200:
            print_with_time(f"  [OKX-PROXY] валидный")
            return True
        else:
            print_with_time(f"  [OKX-PROXY] не валидный, status-code: {r.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_with_time(f"  [OKX-PROXY] не валидный. Ошибка: {e}")
        return False


def get_valid_rpc(from_chain):
    rpc_list = data_blockchains[from_chain]['rpc']
    for rpc in rpc_list:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc))
            latest_block = web3.eth.block_number
            if latest_block is not None:
                return rpc
        except Exception as e:
            print_with_time(f"  Не удалось получить номер последнего блока с RPC {rpc}: {e}")
            continue
    return None


def check_rpc_availability(rpc_url):
    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        latest_block = web3.eth.block_number
        if latest_block is not None:
            return True
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False


def check_all_rpcs():
    all_rpcs_work = True
    """print_with_time(f'  Проверяем все RPC...')
    for network_name, network_data in data_blockchains.items():
        rpcs = network_data.get('rpc', [])
        for rpc_index, rpc in enumerate(rpcs, start=1):
            is_available = check_rpc_availability(rpc)
            time.sleep(1)
            if not is_available:
                print_with_time(f'  RPC {rpc} в сети {network_name} не работает с запросами от вашего IP.\n '
                                f'          Пожалуйста, удалите этот RPC под индексом {rpc_index} в списке RPC для {network_name} в файле modules/data_storage.py.')
                all_rpcs_work = False"""
    return all_rpcs_work


def get_token_balance(private_key, from_chain, from_token):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    available_rpc = get_valid_rpc(from_chain)
    web3 = Web3(Web3.HTTPProvider(available_rpc))
    address_wallet = get_address_wallet(private_key)
    token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
    token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
    balance = token_contract.functions.balanceOf(address_wallet).call()
    balance = balance / (10 ** from_token_decimals)

    return smart_round(balance)

