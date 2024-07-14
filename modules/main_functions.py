from modules.exchange_withdrawals import *
import traceback

lock = Lock()
import random

BRIDGE_GAS_LIMIT = {
    'Ethereum': (580_000, 630_000),
    'Arbitrum': (3_000_000, 4_000_000),
    'Optimism': (700_000, 900_000),
    'Polygon': (580_000, 630_000),
    'BSC': (700_000, 900_000),
    'Avalanche': (900_000, 1_000_000)
}

SWAP_GAS_LIMIT = {
    'Ethereum': (580_000, 630_000),
    'Arbitrum': (3_000_000, 4_000_000),
    'Optimism': (700_000, 900_000),
    'Fantom': (800_000, 1_000_000),
    'Polygon': (580_000, 630_000),
    'BSC': (560_000, 600_000),
    'Avalanche': (580_000, 700_000)
}


def get_randomized_swap_gas_limit(network_name: str) -> int:
    return random.randint(SWAP_GAS_LIMIT[network_name][0],
                          SWAP_GAS_LIMIT[network_name][1])


def get_gas_parameters(network, web3, multiply):
    if network in ['BSC', 'Optimism', 'Core']:
        return {'gasPrice': int(web3.eth.gas_price * data_boost_gas[network]['gasPrice'] * multiply)}
    else:
        return {'type': '0x2', 'maxFeePerGas': int(web3.eth.gas_price * 1.1 * multiply),
                'maxPriorityFeePerGas': int(web3.eth.gas_price * multiply)}


def add_gas_limit(web3, contract_txn):
    value = contract_txn['value']
    contract_txn['value'] = 0
    pluser = [1.02, 1.05]
    gasLimit = web3.eth.estimate_gas(contract_txn)
    contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))

    contract_txn['value'] = value
    return contract_txn


def estimate_layerzero_swap_fee(src_network, dst_network, dst_address, chain_id, web3) -> int:
    """ Method that estimates LayerZero fee to make the swap in native token """

    contract = web3.eth.contract(
        address=web3.to_checksum_address(data_blockchains[src_network]["stargate_bridge_contract"]),
        abi=ABI.abi_stargate)

    quote_data = contract.functions.quoteLayerZeroFee(
        chain_id,  # destination chainId
        1,  # function type (1 - swap): see Bridge.sol for all types
        dst_address,  # destination of tokens
        "0x",  # payload, using abi.encode()
        [0,  # extra gas, if calling smart contract
         0,  # amount of dust dropped in destination wallet
         "0x"  # destination wallet for dust
         ]
    ).call()

    return quote_data[0]


def stargate_bridge(private_key, from_chain, to_chain, from_token, to_token, paths, file_path, i,
                    step_percentage=0.00002):
    from_chain_info = data_blockchains[from_chain]
    to_chain_info = data_blockchains[to_chain]
    from_token_code, to_token_code = get_token_swap_code(from_token, to_token)
    from_token_decimals = get_token_decimals(from_chain, from_token)
    to_chain_id = to_chain_info["chain_id"]
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        stargate_contract_address = web3.to_checksum_address(from_chain_info["stargate_bridge_contract"])
        token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        amount = token_contract.functions.balanceOf(address_wallet).call()
        amount = int(amount * (1 - step_percentage))
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        print_with_time(
            f'  [STARGATE-BRIDGE] Начинаем выполнять транзакцию на {readable_amount} ${from_token} из {from_chain} в {to_chain}')
        print(f'          {address_wallet}')
        if float(readable_amount) < 1:
            print_with_time(
                f'  [STARGATE-BRIDGE] Баланс {readable_amount} ${from_token} в {from_chain} мал. Предположу что объем еще не поступил, жду 5 минут...')
            print(f'          {address_wallet}')
            if float(readable_amount) < 1:
                return True
        min_amount = amount - abs(int(amount * 0.05))
        lz_tx_params = {
            'dstGasForCall': 0,
            'dstNativeAmount': 0,
            'dstNativeAddr': bytes.fromhex('0000000000000000000000000000000000000001')
        }

        try:
            contract = web3.eth.contract(address=stargate_contract_address, abi=ABI.abi_stargate)
            allowance = token_contract.functions.allowance(address_wallet, stargate_contract_address).call()
            print_with_time(
                f'  [STARGATE-BRIDGE] Начинаем выполнять апрув на {readable_amount} ${from_token} из {from_chain} в {to_chain}')
            print(f'          {address_wallet}')
            approve(private_key, from_chain, from_token, stargate_contract_address, token_contract_address)
            delay(delay_approve)

            value = estimate_layerzero_swap_fee(from_chain, to_chain, address_wallet, to_chain_id, web3)
            gasPrice = int(web3.eth.gas_price * data_boost_gas[from_chain]['gasPrice'])
            try:
                gasLimit = get_randomized_swap_gas_limit(from_chain)
            except Exception as e:
                gasLimit = data_gas_limit[from_chain]
                print_with_time("  Проблема с оценкой газа, установлено значение по умолчанию")
                print(f'          {address_wallet}')

            if from_chain == "Polygon":
                time.sleep(60)

            gasParams = get_gas_parameters(from_chain, web3, 1)
            amount_with_slippage = amount - int(amount * 0.01)
            contract_txn = contract.functions.swap(
                to_chain_id,  # destination chainId
                from_token_code,  # source poolId
                to_token_code,  # destination poolId
                address_wallet,  # refund address. extra gas (if any) is returned to this address
                int(amount),  # quantity to swap
                int(amount_with_slippage),  # the min qty you would accept on the destination
                [0,  # extra gas, if calling smart contract
                 0,  # amount of dust dropped in destination wallet
                 "0x0000000000000000000000000000000000000001"  # destination wallet for dust
                 ],
                address_wallet,  # the address to send the tokens to on the destination
                "0x",  # "fee" is the native gas to pay for the cross chain message fee
            ).build_transaction(
                {
                    'from': address_wallet,
                    'value': value,
                    'gas': get_randomized_swap_gas_limit(from_chain),
                    **gasParams,
                    'nonce': web3.eth.get_transaction_count(address_wallet)
                }
            )
            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            print(hex_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']

            if transaction_status == 1:
                print_with_time(
                    f'  [STARGATE-BRIDGE] Отправлено {readable_amount} ${from_token} из {from_chain} в {to_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Pending", hex_hash)
                if get_transaction_status(hex_hash, private_key):
                    process_log(private_key, address_wallet, "STARGATE-BRIDGE", "SUCCESS", from_chain, to_chain,
                                from_token,
                                readable_amount, error=None)
                    print_with_time(
                        f'  [STARGATE-BRIDGE] Депозит {readable_amount} ${from_token} в {to_chain} подтвержден | https://layerzeroscan.com/tx/{hex_hash}')
                    print(f'          {address_wallet}')
                    update_status_and_write(paths, file_path, i, "Success")
                    return True
            else:
                process_log(private_key, address_wallet, "STARGATE-BRIDGE", "ERROR", from_chain, to_chain, from_token,
                            readable_amount, {transaction_receipt["status"]})
                print_with_time(
                    f'  [STARGATE-BRIDGE] Ошибка при отправке {readable_amount} ${from_token} из {from_chain} в {to_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False

        except Exception as error:
            # print(hex_hash)
            print(error)
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [STARGATE-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                stargate_bridge(private_key, from_chain, to_chain, from_token, to_token, paths, file_path, i)
            elif re.search("insufficient balance for transfer", str(error), re.IGNORECASE) or re.search(
                    "FeeLibrary: not enough balance", str(error), re.IGNORECASE):
                step_percentage += 0.00002
                stargate_bridge(private_key, from_chain, to_chain, from_token, to_token, paths, file_path, i,
                                step_percentage)
            elif re.search("TRANSFER_FROM_FAILED", str(error), re.IGNORECASE):
                time.sleep(240)
                stargate_bridge(private_key, from_chain, to_chain, from_token, to_token, paths, file_path, i)
            elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                time.sleep(180)
                stargate_bridge(private_key, from_chain, to_chain, from_token, to_token, paths, file_path, i)
            elif re.search("max fee per gas less than block base fee", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [STARGATE-BRIDGE] Установленная комиссия меньше базовой комиссии блока | Повторяем операцию через 3 минуты...')
                print(f'          {address_wallet}')
                time.sleep(180)
                stargate_bridge(private_key, from_chain, to_chain, from_token, to_token, paths, file_path, i)
            else:
                process_log(private_key, address_wallet, "STARGATE-BRIDGE", "ERROR", from_chain, to_chain, from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [STARGATE-BRIDGE] При создании транзакции {readable_amount} ${from_token} из {from_chain} в {to_chain} возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()
                return True

    except Exception as error:
        process_log(private_key, address_wallet, "STARGATE-BRIDGE", "ERROR", from_chain, to_chain, from_token,
                    0, error)
        print_with_time(
            f'  [STARGATE-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'           {address_wallet}')
        traceback.print_exc()
        return True
    return True


def approve(private_key, from_chain, from_token, bridge_contract_address, token_contract_address, amount=0):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    if from_chain == "Polygon":
        time.sleep(60)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        bridge_contract_address = web3.to_checksum_address(bridge_contract_address)
        token_contract_address = web3.to_checksum_address(token_contract_address)
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        amount = token_contract.functions.balanceOf(address_wallet).call()
        readable_amount = smart_round(amount / 10 ** from_token_decimals)

        try:
            contract_txn = token_contract.functions.approve(bridge_contract_address, amount)
            gas = contract_txn.estimate_gas({'from': address_wallet})
            tx = contract_txn.build_transaction({
                'from': address_wallet,
                **gasParams,
                'gas': int(gas * data_boost_gas[from_chain]['gasLimit']),
                'nonce': web3.eth.get_transaction_count(address_wallet)
            })
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                process_log(private_key, address_wallet, "APPROVE", "SUCCESS", from_chain, from_chain, from_token,
                            readable_amount, error=None)
                print_with_time(
                    f'  [APPROVE] Апрувнул {readable_amount} ${from_token} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
            else:
                process_log(private_key, address_wallet, "APPROVE", "ERROR", from_chain, from_chain, from_token,
                            readable_amount, transaction_receipt["status"])
                print_with_time(
                    f'  [APPROVE] Ошибка при апруве {readable_amount} ${from_token} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')

        except Exception as error:
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [APPROVE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                approve(private_key, from_chain, from_token, bridge_contract_address, token_contract_address)
            elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                time.sleep(180)
                approve(private_key, from_chain, from_token, bridge_contract_address, token_contract_address)
            else:
                process_log(private_key, address_wallet, "APPROVE", "ERROR", from_chain, from_chain, from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [APPROVE] Ошибка при апруве {readable_amount} {from_token} | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()

    except Exception as error:
        process_log(private_key, address_wallet, "APPROVE", "ERROR", from_chain, from_chain, from_token,
                    0, error)
        print_with_time(
            f'  [APPROVE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()


def harmony_bridge(private_key, amount: float, from_chain, from_token, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        if from_token == "USDC":
            contract_address = from_chain_info["harmony_bridge_contract2"]
        else:
            contract_address = from_chain_info["harmony_bridge_contract"]

        bridge_contract_address = web3.to_checksum_address(contract_address)

        try:
            token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
            token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
            amount_wei = int(amount * 10 ** from_token_decimals)
            dst_chain_id = 116
            useZRO = True
            contractZRO = "0x0000000000000000000000000000000000000000"
            adapterParams = "0x0001000000000000000000000000000000000000000000000000000000000007a120"
            print_with_time(
                f'  [HARMONY-BRIDGE] Начинаем выполнять транзакцию на {smart_round(amount)} {from_token} из {from_chain} в Harmony')
            print(f'          {address_wallet}')
            contract = web3.eth.contract(address=bridge_contract_address, abi=ABI.abi_harmony)
            allowance = token_contract.functions.allowance(address_wallet, bridge_contract_address).call()
            if allowance < amount_wei:
                approve(private_key, from_chain, from_token, bridge_contract_address, token_contract_address)
                delay(delay_approve)

            get_value = contract.functions.estimateSendFee(
                dst_chain_id,
                address_wallet,
                amount_wei,
                useZRO,
                adapterParams
            ).call()
            value = get_value[0]

            contract_txn = contract.functions.sendFrom(
                address_wallet,
                dst_chain_id,
                address_wallet,
                amount_wei,
                address_wallet,
                contractZRO,
                adapterParams
            ).build_transaction({
                **gasParams,
                'gas': int((contract.functions.sendFrom(
                    address_wallet,
                    dst_chain_id,
                    address_wallet,
                    amount_wei,
                    address_wallet,
                    contractZRO,
                    adapterParams
                ).estimate_gas({'from': address_wallet, 'value': value})) * data_boost_gas[from_chain]['gasPrice']),
                'nonce': web3.eth.get_transaction_count(address_wallet),
                'value': value
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                process_log(private_key, address_wallet, "HARMONY-BRIDGE", "SUCCESS", from_chain, "Harmony", from_token,
                            smart_round(amount), error=None)
                print_with_time(
                    f'  [HARMONY-BRIDGE] Отправил {smart_round(amount)} {from_token} в Harmony | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Success")
                return True
            else:
                process_log(private_key, address_wallet, "HARMONY-BRIDGE", "ERROR", from_chain, "Harmony", from_token,
                            smart_round(amount), transaction_receipt["status"])
                print_with_time(
                    f'  [HARMONY-BRIDGE] Ошибка при отправке {smart_round(amount)} {from_token} в Harmony | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False
        except Exception as error:
            print(error)
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [HARMONY-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                harmony_bridge(private_key, amount, from_chain, from_token, paths, file_path, i)
            elif re.search("transfer amount exceeds balance", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [HARMONY-BRIDGE] Не достаточно {from_token} для отправки в Harmony, похоже слишком поздно...')
                print(f'          {address_wallet}')
            else:
                process_log(private_key, address_wallet, "HARMONY-BRIDGE", "ERROR", from_chain, "Harmony", from_token,
                            smart_round(amount), error)
                print_with_time(
                    f'  [HARMONY-BRIDGE] При создании транзакции для отправки {smart_round(amount)} {from_token} в Harmony возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()

    except Exception as error:
        process_log(private_key, address_wallet, "HARMONY-BRIDGE", "ERROR", from_chain, "Harmony", from_token,
                    smart_round(amount), error)
        print_with_time(
            f'  [HARMONY-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()


def core_bridge(private_key, from_chain, from_token, paths, file_path, i, step_percentage=0.00002):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        contract_address = web3.to_checksum_address(from_chain_info["core_bridge_contract"])
        token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        useZRO = False
        call_params = {'refundAddress': address_wallet,
                       'zroPaymentAddress': "0x0000000000000000000000000000000000000000"}
        adapter_params = bytes()
        amount = token_contract.functions.balanceOf(address_wallet).call()
        amount = int(amount * (1 - step_percentage))
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        print_with_time(
            f'  [CORE-BRIDGE] Начинаем транзакцию {readable_amount} ${from_token} из BSC в Core ')
        print(f'          {address_wallet}')
        if readable_amount < 1:
            print_with_time(
                f'  [CORE-BRIDGE] Баланс {readable_amount} ${from_token} в {from_chain} мал. Предположу что объем еще не поступил, жду 5 минут...')
            print(f'          {address_wallet}')
            time.sleep(300)

        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_core)
            allowance = token_contract.functions.allowance(address_wallet, contract_address).call()
            if allowance < amount:
                print_with_time(
                    f'  [CORE-BRIDGE] Начинаем апрув на {readable_amount} ${from_token} в Core ')
                print(f'          {address_wallet}')
                approve(private_key, from_chain, from_token, contract_address, token_contract_address)
                delay(delay_approve)

            get_value = contract.functions.estimateBridgeFee(useZRO, bytes()).call()
            value = get_value[0]

            contract_txn = contract.functions.bridge(
                token_contract_address,
                amount,
                address_wallet,
                call_params,
                adapter_params
            ).build_transaction({
                **gasParams,
                'gas': int((contract.functions.bridge(
                    token_contract_address,
                    amount,
                    address_wallet,
                    call_params,
                    adapter_params
                ).estimate_gas({'from': address_wallet, 'value': value})) * data_boost_gas[from_chain]['gasPrice']),
                'nonce': web3.eth.get_transaction_count(address_wallet),
                'value': value
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                print_with_time(
                    f'  [CORE-BRIDGE] Отправлено {readable_amount} ${from_token} в Core | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Pending", hex_hash)

                if get_transaction_status(hex_hash, private_key):
                    process_log(private_key, address_wallet, "CORE-BRIDGE", "SUCCESS", from_chain, "Core", from_token,
                                readable_amount, error=None)
                    print_with_time(
                        f'  [CORE-BRIDGE] Депозит {readable_amount} ${from_token} в Core подтвержден | https://layerzeroscan.com/tx/{hex_hash}')
                    print(f'          {address_wallet}')
                    update_status_and_write(paths, file_path, i, "Success")
                    return True
            else:
                process_log(private_key, address_wallet, "CORE-BRIDGE", "ERROR", from_chain, "Core", from_token,
                            readable_amount, transaction_receipt["status"])
                print_with_time(
                    f'  [CORE-BRIDGE] Ошибка при отправке {readable_amount} ${from_token} в Core | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False

        except Exception as error:
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [CORE-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим с биржи дополнительно и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                core_bridge(private_key, from_token, from_chain, paths, file_path, i)
            elif re.search("insufficient balance for transfer", str(error), re.IGNORECASE):
                step_percentage += 0.00002
                core_bridge(private_key, from_chain, from_token, paths, file_path, i, step_percentage)
            else:
                process_log(private_key, address_wallet, "CORE-BRIDGE", "ERROR", from_chain, "Core", from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [CORE-BRIDGE] При создании транзакции для отправки {readable_amount} ${from_token} в Core возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()
                return True

    except Exception as error:
        process_log(private_key, address_wallet, "CORE-BRIDGE", "ERROR", from_chain, "Core", from_token,
                    000, error)
        print_with_time(
            f'  [CORE-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()
        return True


def from_core_bridge(private_key, from_token, from_chain, paths, file_path, i, step_percentage=0.00002):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        contract_address = web3.to_checksum_address(from_chain_info["core_bridge_contract"])
        token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        call_params = (address_wallet, "0x0000000000000000000000000000000000000000")
        chain_id = 102
        unwrapWeth = False
        useZRO = False
        amount = token_contract.functions.balanceOf(address_wallet).call()
        amount = int(amount * (1 - step_percentage))
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        print_with_time(
            f'  [CORE-BRIDGE] Начинаем выполнять транзакцию {readable_amount} ${from_token} из Core в BSC')
        print(f'          {address_wallet}')
        if readable_amount < 1:
            print_with_time(
                f'  [CORE-BRIDGE] Баланс {readable_amount} ${from_token} в {from_chain} мал. Предположу что объем еще не поступил, жду 5 минут...')
            print(f'          {address_wallet}')
            time.sleep(300)

        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_from_core)
            allowance = token_contract.functions.allowance(address_wallet, contract_address).call()
            if allowance < amount:
                approve(private_key, from_chain, from_token, contract_address, token_contract_address)
                delay(delay_approve)

            get_value = contract.functions.estimateBridgeFee(chain_id, useZRO, b'').call()
            value = get_value[0]

            contract_txn = contract.functions.bridge(
                token_contract_address,
                chain_id,
                amount,
                address_wallet,
                unwrapWeth,
                call_params,
                b''
            ).build_transaction({
                **gasParams,
                'gas': int((contract.functions.bridge(
                    token_contract_address,
                    chain_id,
                    amount,
                    address_wallet,
                    unwrapWeth,
                    call_params,
                    b''
                ).estimate_gas({'from': address_wallet, 'value': value})) * data_boost_gas[from_chain]['gasPrice']),
                'nonce': web3.eth.get_transaction_count(address_wallet),
                'value': value
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                print_with_time(
                    f'  [CORE-BRIDGE] Отправил {readable_amount} ${from_token} из Core | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Pending", hex_hash)
                if get_transaction_status(hex_hash, private_key):
                    process_log(private_key, address_wallet, "CORE-BRIDGE", "SUCCESS", "Core", "BSC", from_token,
                                readable_amount, error=None)
                    print_with_time(
                        f'  [CORE-BRIDGE] Вывод {readable_amount} ${from_token} в BSC подтвержден | https://layerzeroscan.com/tx/{hex_hash}')
                    print(f'          {address_wallet}')
                    update_status_and_write(paths, file_path, i, "Success")
                    return True
            else:
                process_log(private_key, address_wallet, "CORE-BRIDGE", "ERROR", "Core", "BSC", from_token,
                            readable_amount, transaction_receipt["status"])
                print_with_time(
                    f'  [CORE-BRIDGE] Ошибка при отправке {readable_amount} ${from_token}  из Core | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False

        except Exception as error:
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [CORE-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                from_core_bridge(private_key, from_token, from_chain, paths, file_path, i)
            elif re.search("insufficient balance for transfer", str(error), re.IGNORECASE):
                step_percentage += 0.00002
                from_core_bridge(private_key, from_token, from_chain, paths, file_path, i, step_percentage)
            else:
                process_log(private_key, address_wallet, "CORE-BRIDGE", "ERROR", "Core", "BSC", from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [CORE-BRIDGE] При создании транзакции для отправки {readable_amount} ${from_token} из Core возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()
                return True

    except Exception as error:
        process_log(private_key, address_wallet, "CORE-BRIDGE", "ERROR", "Core", "BSC", from_token,
                    000, error)
        print_with_time(
            f'  [CORE-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()
        return True


def stake_stg(private_key, from_chain, from_token, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        contract_address = Web3.to_checksum_address(from_chain_info["stg_stake_contract"])
        token_contract_address = Web3.to_checksum_address(from_chain_info["stg_contract"])
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        amount = token_contract.functions.balanceOf(address_wallet).call()
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        months = random.randint(months_to_lock[0], months_to_lock[1])
        unlock_time = 1783555200  # 1782345600  # get_unlock_time(36)
        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_stg_stake)
            allowance = token_contract.functions.allowance(address_wallet, contract_address).call()
            if allowance < amount:
                approve(private_key, from_chain, from_token, contract_address, token_contract_address)
                delay(delay_approve)
            contract_txn = contract.functions.create_lock(amount, unlock_time).build_transaction({
                'from': address_wallet,
                'value': 0,
                'gas': int((contract.functions.create_lock(
                    amount,
                    unlock_time
                ).estimate_gas({'from': address_wallet, 'value': 0})) * data_boost_gas[from_chain]['gasPrice']),
                **gasParams,
                'nonce': web3.eth.get_transaction_count(address_wallet)
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                process_log(private_key, address_wallet, "STAKE-STG", "SUCCESS", from_chain, from_chain, "STG",
                            readable_amount, error=None)
                print_with_time(
                    f'  [STAKE-STG] Застейкал {readable_amount} $STG на {months} месяцев в {from_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Success")
                return True
            else:
                process_log(private_key, address_wallet, "STAKE-STG", "ERROR", from_chain, from_chain, "STG",
                            readable_amount, transaction_receipt["status"])
                print_with_time(
                    f'  [STAKE-STG] Ошибка при стейкинге {readable_amount} $STG на {months} месяцев в {from_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False

        except Exception as error:
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [STAKE-STG] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                stake_stg(private_key, from_chain, from_token, paths, file_path, i)
            elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE) or \
                    re.search("nonce too low", str(error), re.IGNORECASE):
                delay(delay_txn)
                stake_stg(private_key, from_chain, from_token, paths, file_path, i)
            elif re.search("Withdraw old tokens first", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [STAKE-STG] На кошельке уже есть застейканные $STG, нет возможности застейкать еще, пропускаем...')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Success")
            else:
                process_log(private_key, address_wallet, "STAKE-STG", "ERROR", from_chain, from_chain, "STG",
                            readable_amount, error)
                print_with_time(
                    f'  [STAKE-STG] Ошибка при создании транзакции для стейка $STG в {from_chain} | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()

    except Exception as error:
        process_log(private_key, address_wallet, "STAKE-STG", "ERROR", from_chain, from_chain, "STG",
                    000, error)
        print_with_time(
            f'  [STAKE-STG] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()


def get_randomized_bridge_gas_limit(network_name):
    return random.randint(BRIDGE_GAS_LIMIT[network_name][0],
                          BRIDGE_GAS_LIMIT[network_name][1])


def get_adapter_params(from_chain, to_chain, address_wallet):
    if to_chain == 'Arbitrum':
        return f"0x00020000000000000000000000000000000000000000000000000000000000" \
               f"2dc6c00000000000000000000000000000000000000000000000000000000000000000" \
               f"{address_wallet[2:]}"
    else:
        return f"0x000200000000000000000000000000000000000000000000000000000000000" \
               f"3d0900000000000000000000000000000000000000000000000000000000000000000" \
               f"{address_wallet[2:]}"


def estimate_layerzero_bridge_fee(from_chain, to_chain, address_wallet, web3, layerzero_chain_id):
    btcb_contract = web3.eth.contract(
        address=web3.to_checksum_address(data_blockchains[from_chain]['btcb_bridge_contract']), abi=ABI.abi_btcb)

    to_address = '0x000000000000000000000000' + address_wallet[2:]

    amount = 100  # Doesn't matter in fee calculation

    quote_data = btcb_contract.functions.estimateSendFee(layerzero_chain_id, to_address,
                                                         amount, False,
                                                         get_adapter_params(from_chain, to_chain, address_wallet)
                                                         ).call()
    return quote_data[0]


def btcb_bridge(private_key, from_chain, to_chain, from_token, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, "BTCb")
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)
    print_with_time(
        f'  [BTC.b-BRIDGE] Начинаем выполнять транзакцию для BTCb из {from_chain} в {to_chain}')
    print(f'          {address_wallet}')
    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))

        gasParams = get_gas_parameters(from_chain, web3, 1)
        btcb_contract = web3.eth.contract(address=web3.to_checksum_address(from_chain_info["btcb_bridge_contract"]),
                                          abi=ABI.BTCB_ABI)
        token_contract = web3.eth.contract(address=web3.to_checksum_address(from_chain_info["btcb_contract"]),
                                           abi=ABI.ERC20_ABI)

        amount = int(token_contract.functions.balanceOf(address_wallet).call() * (1 - 0.003))
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        dst_chain_id = data_blockchains[to_chain]['chain_id']
        try:
            approve(private_key, from_chain, from_token, from_chain_info["btcb_bridge_contract"],
                    from_chain_info["btcb_contract"])

            delay(delay_approve)
            # allowance = token_contract.functions.allowance(address_wallet, web3.to_checksum_address(from_chain_info["btcb_bridge_contract"])).call()
            # if allowance < amount:
            #     approve(private_key, from_chain, from_token, btcb_contract, token_contract)
            # delay(delay_txn)
            layerzero_fee = estimate_layerzero_bridge_fee(from_chain, to_chain, address_wallet, web3, dst_chain_id)
            contract_txn = btcb_contract.functions.sendFrom(
                address_wallet,  # _from
                dst_chain_id,  # _dstChainId
                f"0x000000000000000000000000{address_wallet[2:]}",  # _toAddress
                amount,  # _amount
                amount,  # _minAmount
                [address_wallet,  # _callParams.refundAddress
                 "0x0000000000000000000000000000000000000000",  # _callParams.zroPaymentAddress
                 get_adapter_params(from_chain, to_chain, address_wallet)]
            ).build_transaction(
                {
                    'from': address_wallet,
                    'value': layerzero_fee,
                    'gas': get_randomized_bridge_gas_limit(from_chain),
                    **gasParams,
                    'nonce': web3.eth.get_transaction_count(address_wallet)
                }
            )

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                if get_transaction_status(hex_hash, private_key):
                    process_log(private_key, address_wallet, "BTC-BRIDGE", "SUCCESS", from_chain, from_chain, "BTC.b",
                                readable_amount, error=None)
                    print_with_time(
                        f'  [BTC.b-BRIDGE] Отправил {readable_amount} $BTC.b через BTC.b Bridge из {from_chain} в {to_chain} | {explorer}tx/{hex_hash}')
                    print(f'          {address_wallet}')
                    update_status_and_write(paths, file_path, i, "Success")
                    return True
                else:
                    process_log(private_key, address_wallet, "BTC-BRIDGE", "ERROR", from_chain, from_chain, "BTC.b",
                                readable_amount, transaction_receipt["status"])
                    print_with_time(
                        f'  [BTC.b-BRIDGE] Ошибка при отправке {readable_amount} $BTC.b через BTC.b Bridge | {explorer}tx/{hex_hash}')
                    print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                    return False

        except Exception as error:
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [BTC.b-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                btcb_bridge(private_key, from_chain, to_chain, from_token, paths, file_path, i)
            elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                delay(delay_txn)
                btcb_bridge(private_key, from_chain, to_chain, from_token, paths, file_path, i)
            else:
                process_log(private_key, address_wallet, "BTC-BRIDGE", "ERROR", from_chain, from_chain, "BTC.b",
                            readable_amount, error)
                print_with_time(
                    f'  [BTC.b-BRIDGE] При отправке {readable_amount} $BTC.b через BTC.b Bridge возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()

    except Exception as error:
        process_log(private_key, address_wallet, "BTC-BRIDGE", "ERROR", from_chain, from_chain, "BTC.b",
                    000, error)
        print_with_time(
            f'  [BTC.b-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()


def withdrawal_from(private_key, withdrawal_address, from_chain, from_token, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    reserve_amount = (random.uniform(reserve_balance[0], reserve_balance[1])) * 10 ** from_token_decimals
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        withdrawal_address = web3.to_checksum_address(withdrawal_address)
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        amount = token_contract.functions.balanceOf(address_wallet).call()
        #print(amount)
        if amount < 1000:
            process_log(private_key, address_wallet, "END-WITHDRAW", "ERROR", from_chain, withdrawal_address,
                        from_token,
                        000, "Too small balance")
            print_with_time(
                f'  [END-WITHDRAW] Ошибка при выводе, слишком маленькая сумма ${from_token} в {from_chain}')
            print(f'          {address_wallet} >>> {withdrawal_address}')
            return
        amount = amount * (1 - 0.00002)
        #print('amount = ',amount)
        amount = int(amount - reserve_amount)
        #print('reserve_amount = ',reserve_amount)
        #print('amount = int(amount - reserve_amount) = ', amount)
        readable_amount = smart_round(amount / 10 ** from_token_decimals)

        try:
            transaction = token_contract.functions.transfer(withdrawal_address, amount).build_transaction({
                'from': address_wallet,
                'gas': int((token_contract.functions.transfer(
                    withdrawal_address,
                    amount
                ).estimate_gas({'from': address_wallet})) * random.uniform(1.1, 1.2)),
                **gasParams,
                'nonce': web3.eth.get_transaction_count(address_wallet)
            })
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']

            if transaction_status == 1:
                process_log(private_key, address_wallet, "END-WITHDRAW", "SUCCESS", from_chain, withdrawal_address,
                            from_token,
                            readable_amount, error=None)
                print_with_time(
                    f'  [END-WITHDRAW] Успешно вывел {readable_amount} ${from_token} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} >>> {withdrawal_address}')
                update_status_and_write(paths, file_path, i, "Success")
                return True
            else:
                process_log(private_key, address_wallet, "END-WITHDRAW", "ERROR", from_chain, withdrawal_address,
                            from_token,
                            readable_amount, transaction_status["status"])
                print_with_time(
                    f'  [END-WITHDRAW] Ошибка при выводе {readable_amount} ${from_token} | {explorer}tx/{hex_hash}')
                print(
                    f'          {address_wallet} >>> {withdrawal_address} | код ошибки: {transaction_status["status"]}')
                return False

        except Exception as error:
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [END-WITHDRAW] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                withdrawal_from(private_key, withdrawal_address, from_chain, from_token, paths, file_path, i)
            elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                time.sleep(180)
                withdrawal_from(private_key, withdrawal_address, from_chain, from_token, paths, file_path, i)
            elif re.search("max fee per gas less than block base fee", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [END-WITHDRAW] Установленная комиссия меньше базовой комиссии блока | Повторяем операцию через 3 минуты...')
                print(f'          {address_wallet}')
                time.sleep(180)
                withdrawal_from(private_key, withdrawal_address, from_chain, from_token, paths, file_path, i)
            else:
                process_log(private_key, address_wallet, "END-WITHDRAW", "ERROR", from_chain, withdrawal_address,
                            from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [END-WITHDRAW] Ошибка при создании транзакции для вывода {readable_amount} ${from_token} | {error}')
                print(f'          {address_wallet} >>> {withdrawal_address}')
                traceback.print_exc()

    except Exception as error:
        process_log(private_key, address_wallet, "END-WITHDRAW", "ERROR", from_chain, withdrawal_address, from_token,
                    000, error)
        print_with_time(
            f'  [END-WITHDRAW] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()


def testnet_bridge(private_key, amount: float, from_chain, from_token, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        contract_address = web3.to_checksum_address(from_chain_info["testnet_contract"])
        contractGetFee_address = web3.to_checksum_address(from_chain_info["testnetGetFee_contract"])
        zroPaymentAddress = "0x0000000000000000000000000000000000000000"
        chain_id = 154
        useZro = False
        readable_amount = smart_round(amount)
        amount = int(amount * 10 ** from_token_decimals)
        amountOut = 0
        print_with_time(
            f'  [TESTNET-BRIDGE] Начинаем выполнять транзакцию {readable_amount} ${from_token} из Arbitrum')
        print(f'          {address_wallet}')
        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_testnet)
            contract_get_fee = web3.eth.contract(address=contractGetFee_address, abi=ABI.abi_testnet)
            get_value = contract_get_fee.functions.estimateSendFee(
                154,
                address_wallet,
                amount,
                useZro,
                b''
            ).call()
            value = int(get_value[0])

            contract_txn = contract.functions.swapAndBridge(
                amount,
                amountOut,
                chain_id,
                address_wallet,
                address_wallet,
                zroPaymentAddress,
                b''
            ).build_transaction({
                **gasParams,
                'gas': int((contract.functions.swapAndBridge(
                    amount,
                    amountOut,
                    chain_id,
                    address_wallet,
                    address_wallet,
                    zroPaymentAddress,
                    b''
                ).estimate_gas({'from': address_wallet, 'value': int(value + amount)})) * data_boost_gas[from_chain][
                               'gasPrice']),
                'nonce': web3.eth.get_transaction_count(address_wallet),
                'value': int(value + amount)
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                print_with_time(
                    f'  [TESTNET-BRIDGE] Отправил {readable_amount} ${from_token} из Arbitrum | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                update_status_and_write(paths, file_path, i, "Success")
                return True
            else:
                process_log(private_key, address_wallet, "TESTNET-BRIDGE", "ERROR", "Arbitrum", "Goerli", from_token,
                            readable_amount, transaction_receipt["status"])
                print_with_time(
                    f'  [TESTNET-BRIDGE] Ошибка при отправке {readable_amount} ${from_token}  из Arbitrum | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False

        except Exception as error:
            print(error)
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [TESTNET-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                testnet_bridge(private_key, amount, from_chain, from_token, paths, file_path, i)
            else:
                process_log(private_key, address_wallet, "TESTNET-BRIDGE", "ERROR", "Arbitrum", "Goerli", from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [TESTNET-BRIDGE] При создании транзакции для отправки {readable_amount} ${from_token} из Arbitrum возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()

    except Exception as error:
        process_log(private_key, address_wallet, "TESTNET-BRIDGE", "ERROR", "Arbitrum", "Goerli", from_token,
                    000, error)
        print_with_time(
            f'  [TESTNET-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()


def aptos_bridge(private_key, amount: float, from_chain, from_token, aptos_address, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        contract_address = web3.to_checksum_address(from_chain_info["aptos_contract"])
        token_contract_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
        call_params = {'refundAddress': address_wallet,
                       'zroPaymentAddress': "0x0000000000000000000000000000000000000000"}
        adapter_params = f"0x000200000000000000000000000000000000000000000000000000000000000027100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000{aptos_address[2:]}"
        amount_wei = int(amount * 10 ** from_token_decimals)
        readable_amount = smart_round(amount)
        print_with_time(
            f'  [APTOS-BRIDGE] Начинаем выполнять транзакцию {readable_amount} ${from_token} из {from_chain} в APTOS')
        print(f'          {address_wallet}')
        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_aptos)
            allowance = token_contract.functions.allowance(address_wallet, contract_address).call()
            if allowance < amount_wei:
                approve(private_key, from_chain, from_token, contract_address, token_contract_address)
                delay(delay_approve)

            get_value = contract.functions.quoteForSend(call_params, adapter_params).call()
            value = get_value[0]

            if from_chain == "Polygon":
                time.sleep(60)

            contract_txn = contract.functions.sendToAptos(
                token_contract_address,
                aptos_address,
                amount_wei,
                call_params,
                adapter_params
            ).build_transaction({
                **gasParams,
                'gas': int((contract.functions.sendToAptos(
                    token_contract_address,
                    aptos_address,
                    amount_wei,
                    call_params,
                    adapter_params
                ).estimate_gas({'from': address_wallet, 'value': value})) * data_boost_gas[from_chain]['gasPrice']),
                'nonce': web3.eth.get_transaction_count(address_wallet),
                'value': value
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            if transaction_status == 1:
                print_with_time(
                    f'  [APTOS-BRIDGE] Отправлено {readable_amount} ${from_token} в APTOS | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                process_log(private_key, address_wallet, "APTOS-BRIDGE", "SUCCESS", from_chain, "APTOS", from_token,
                            readable_amount, error=None)
                update_status_and_write(paths, file_path, i, "Success")
                return True
            else:
                process_log(private_key, address_wallet, "APTOS-BRIDGE", "ERROR", from_chain, "APTOS", from_token,
                            readable_amount, transaction_receipt["status"])
                print_with_time(
                    f'  [APTOS-BRIDGE] Ошибка при отправке {readable_amount} ${from_token} в APTOS | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False

        except Exception as error:
            print(error)
            if re.search("insufficient funds", str(error), re.IGNORECASE):
                print_with_time(
                    f'  [APTOS-BRIDGE] Не достаточно нативного токена для оплаты газа | Выводим с биржи дополнительно и повторяем операцию...')
                print(f'          {address_wallet}')
                exception_withdraw(private_key, from_chain)
                delay(delay_txn)
                aptos_bridge(private_key, amount, from_chain, from_token, aptos_address, paths, file_path, i)
            elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE) or \
                    re.search("nonce too low", str(error), re.IGNORECASE):
                time.sleep(180)
                aptos_bridge(private_key, amount, from_chain, from_token, aptos_address, paths, file_path, i)
            else:
                process_log(private_key, address_wallet, "APTOS-BRIDGE", "ERROR", from_chain, "Core", from_token,
                            readable_amount, error)
                print_with_time(
                    f'  [APTOS-BRIDGE] При создании транзакции для отправки {readable_amount} ${from_token} в APTOS возникла ошибка | {error}')
                print(f'          {address_wallet}')
                traceback.print_exc()

    except Exception as error:
        print(error)
        process_log(private_key, address_wallet, "APTOS-BRIDGE", "ERROR", from_chain, "APTOS", from_token,
                    000, error)
        print_with_time(
            f'  [APTOS-BRIDGE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        traceback.print_exc()