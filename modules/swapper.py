from modules.main_functions import *
from aiohttp import ClientSession
import requests
import asyncio

def get_gas_parameters(network, web3, multiply):
    if network in ['BSC', 'Optimism', 'Core']:
        return {'gasPrice': int(web3.eth.gas_price * data_boost_gas[network]['gasPrice'] * multiply)}
    else:
        return {'type': '0x2',
                'maxFeePerGas': int(web3.eth.gas_price * data_boost_gas[network]['gasPrice'] * 1.1 * multiply),
                'maxPriorityFeePerGas': int(web3.eth.gas_price * data_boost_gas[network]['gasPrice'] * multiply)}


def inch_api_call(url):
    try:
        call_data = requests.get(url)
    except Exception as e:
        return inch_api_call(url)
    try:
        api_data = call_data.json()
        return api_data
    except Exception as e:
        return


def add_gas_limit____(web3: Web3, tx: dict,from_chain) -> int:
    tx['value'] = 0
    gas_limit = int(web3.eth.estimate_gas(tx) * data_boost_gas[from_chain]['gasLimit'])
    return gas_limit



def send_requests(url):
    while True:
        response = requests.get(url)
        if response.status_code != 429:
            return response.json()
        retry_after = int(response.headers.get('Retry-After', 1))  # по умолчанию 1 секунда
        time.sleep(retry_after)

def inch_approve(private_key, from_token, from_chain, amount: float, token_to_buy):
    from_chain_info = data_blockchains[from_chain]
    explorer = from_chain_info["explorer"]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)
    inch_url = 'https://api-defillama.1inch.io'

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, 1)
        amount = int(amount)
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        token_address = from_chain_info.get(f"{from_token.lower()}_contract")
        if token_address is None:
            print(f"Error: No contract for {from_token}")
            return
        contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=ABI.abi_tokens)
        try:
            # _1inchurl = f'{inch_url}/v5.0/{from_chain_info["network_id"]}/approve/transaction?tokenAddress={token_address}&walletAddress={address_wallet}&amount={amount}'
            # json_data = inch_api_call(_1inchurl)
            # print(_1inchurl)
            # print(json_data)
            #contract = web3.eth.contract(address=web3.to_checksum_address(json_data["to"]), abi=ABI.abi_tokens)
            # gas_estimate = contract.functions.approve(address_wallet, amount).estimate_gas({'from': address_wallet})

            # tx = {
            #     "nonce": web3.eth.get_transaction_count(address_wallet),
            #     "to": web3.to_checksum_address(json_data["to"]),
            #     "data": json_data["data"],
            #     **gasParams,
            #     "gas": int(gas_estimate * data_boost_gas[from_chain]['gasLimit']),
            #     "chainId": from_chain_info["network_id"]
            # }
            # print(f'from_chain: {from_chain}')
            # print(f'from_chain_info: {from_chain_info}')

            network_id = int(from_chain_info["network_id"])
            url=f"https://api-defillama.1inch.io/v5.0/{network_id}/approve/spender"
            # print(f'url: {url}')
            response =  send_requests(url)
            if response is not None:
                spender =  web3.to_checksum_address(response['address'])
                # print(spender)
            else:
                print(f"Error: Response is None when calling {url}")
                return
            tx = contract.functions.approve(
                spender,
                amount
            ).build_transaction(
                {
                    'chainId': from_chain_info["network_id"],
                    'from': address_wallet,
                    'nonce': web3.eth.get_transaction_count(address_wallet),
                    **gasParams,
                    'gas': 0,
                    'value': 0
                }
            )
            #print(tx)
            gas_limit = add_gas_limit____(web3, tx,from_chain) 
            tx['gas'] = gas_limit 
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']
            
            if transaction_status == 1:
                process_log(private_key, address_wallet, "APPROVE 1INCH", "SUCCESS", from_chain, from_chain, from_token,
                            readable_amount, error=None)
                print_with_time(
                    f'  [APPROVE 1INCH] Апрувнул {readable_amount} ${from_token} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                return True
            else:
                print_with_time(
                    f'  [APPROVE 1INCH] Ошибка при апруве {readable_amount} ${from_token} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet} | код ошибки: {transaction_receipt["status"]}')
                return False
        except Exception as error:
            print_with_time(
                f'  [APPROVE 1INCH] Ошибка при создании транзакции для покупки ${token_to_buy} на 1inch | {error}')
            print(f'          {address_wallet}')
            return False
    except Exception as error:
        print_with_time(
            f'  [APPROVE 1INCH] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {address_wallet}')
        return False


def inch_swap(private_key, from_token, from_chain, amount: float, token_to_buy, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)
    inch_url = 'https://api-defillama.1inch.io'
    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, multiply=1.27)
        amount_ = int((amount*0.9) * 10 ** from_token_decimals)
        readable_amount = smart_round(amount_ / 10 ** from_token_decimals)
        from_token_address = from_chain_info[f"{from_token.lower()}_contract"]
        to_token_address = from_chain_info[f"{token_to_buy.lower()}_contract"]
        try:
            # print("before allowance")
            # allowance_url = f'{inch_url}/v5.0/{from_chain_info["network_id"]}/approve/allowance?tokenAddress={from_token_address}&walletAddress={address_wallet}'
            # allowance_data = inch_api_call(allowance_url)
            # allowance = int(allowance_data["allowance"])
            # print("after allowance")
            # to_token_address = web3.to_checksum_address(from_chain_info[f"{token_to_buy.lower()}_contract"])
            # token_contract = web3.eth.contract(address=from_token_address, abi=ABI.abi_tokens)
            # contract_address = web3.to_checksum_address(from_chain_info[f"sushi_contract"])
            # allowance = token_contract.functions.allowance(address_wallet, contract_address).call()
            # if allowance < amount_:
            #     delay(delay_approve)
            inch_approve(private_key, from_token, from_chain, amount_, token_to_buy)
            print(amount_)
            # _1inchurl = f'{inch_url}/v5.0/{from_chain_info["network_id"]}/swap?fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&amount={amount}&fromAddress={address_wallet}&slippage=7'
            # json_data = inch_api_call(_1inchurl)

            response = send_requests(
            url=f'{inch_url}/v5.0/{from_chain_info["network_id"]}/swap?fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&amount={amount_}&fromAddress={address_wallet}&slippage=7')
            
            print(f'{inch_url}/v5.0/{from_chain_info["network_id"]}/swap?fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&amount={amount_}&fromAddress={address_wallet}&slippage=7')
            # print('nonce - ', web3.eth.get_transaction_count(web3.to_checksum_address(address_wallet)))
            try:
                tx = response['tx']
                tx['chainId'] = from_chain_info["network_id"]
                tx['nonce'] =  web3.eth.get_transaction_count(web3.to_checksum_address(address_wallet))
                tx['to'] = Web3.to_checksum_address(tx['to'])
                tx['gasPrice'] = int(tx['gasPrice'])
                tx['gas'] = int(int(tx['gas']))
                tx['value'] = int(tx['value'])
            except Exception as e:
                print(e)
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']

            if transaction_status == 1:
                process_log(private_key, address_wallet, "BUY 1INCH", "SUCCESS", from_chain, from_chain, from_token,
                            readable_amount, error=None)
                update_status_and_write(paths, file_path, i, "Success")
                print_with_time(
                    f'  [BUY 1INCH] Купил ${token_to_buy} за {readable_amount} ${from_token} в {from_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                return True
            else:
                return False
        except Exception as error:
            print(error)
            return False
    except Exception as error:
        print(error)
        return False


def get_sushi_amountOutMin(contract, value, from_token, to_token):
    contract_txn = contract.functions.getAmountsOut(
        value,
        [from_token, to_token],
    ).call()

    return int(contract_txn[1] * 0.90)


def sushi_swap(private_key, from_token, from_chain, amount: float, token_to_buy, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, multiply=1)
        amount = int(amount * 10 ** from_token_decimals)
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        from_token_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        to_token_address = web3.to_checksum_address(from_chain_info[f"{token_to_buy.lower()}_contract"])
        contract_address = web3.to_checksum_address(from_chain_info[f"sushi_contract"])
        token_contract = web3.eth.contract(address=from_token_address, abi=ABI.abi_tokens)
        nonce = web3.eth.get_transaction_count(address_wallet)

        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_sushi)
            amountOutMin = get_sushi_amountOutMin(contract, amount, from_token_address, to_token_address)

            allowance = token_contract.functions.allowance(address_wallet, contract_address).call()
            if allowance < amount:
                approve(private_key, from_chain, from_token, contract_address, from_token_address, amount)
                delay(delay_approve)
                nonce = web3.eth.get_transaction_count(address_wallet)

            contract_txn = contract.functions.swapExactTokensForTokens(
                amount,
                amountOutMin,
                [from_token_address, to_token_address],
                address_wallet,
                (int(time.time()) + 10000)
            ).build_transaction(
                {
                    "from": address_wallet,
                    "nonce": nonce,
                    **gasParams,
                    'gas': int((contract.functions.swapExactTokensForTokens(
                        amount,
                        amountOutMin,
                        [from_token_address, to_token_address],
                        address_wallet,
                        (int(time.time()) + 10000)
                    ).estimate_gas({'from': address_wallet, 'value': 0})) * data_boost_gas[from_chain]['gasPrice']),
                }
            )

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']

            if transaction_status == 1:
                process_log(private_key, address_wallet, "BUY SUSHI", "SUCCESS", from_chain, from_chain, from_token,
                            readable_amount, error=None)
                update_status_and_write(paths, file_path, i, "Success")
                print_with_time(
                    f'  [BUY SUSHI] Купил ${token_to_buy} за {readable_amount} ${from_token} в {from_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                return True
            else:
                return False
        except Exception as error:
            if re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                delay(delay_txn)
                sushi_swap(private_key, from_token, from_chain, amount, token_to_buy, paths, file_path, i)
            else:
                return False
    except Exception as error:
        print(error)
        return False


def get_woofi_amountOutMin(contract, from_token, to_token, amount):
    try:
        amountOutMin = contract.functions.tryQuerySwap(
            from_token,
            to_token,
            amount
        ).call()
        return int(amountOutMin * 0.90)
    except Exception as error:
        print(error)
        return 0


def woofi_swap(private_key, from_token, from_chain, amount: float, token_to_buy, paths, file_path, i):
    from_chain_info = data_blockchains[from_chain]
    from_token_decimals = get_token_decimals(from_chain, from_token)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)

    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, multiply=1)
        amount = int(amount * 10 ** from_token_decimals)
        readable_amount = smart_round(amount / 10 ** from_token_decimals)
        from_token_address = web3.to_checksum_address(from_chain_info[f"{from_token.lower()}_contract"])
        to_token_address = web3.to_checksum_address(from_chain_info[f"{token_to_buy.lower()}_contract"])
        contract_address = web3.to_checksum_address(from_chain_info[f"woofi_contract"])
        token_contract = web3.eth.contract(address=from_token_address, abi=ABI.abi_tokens)
        nonce = web3.eth.get_transaction_count(address_wallet)

        try:
            contract = web3.eth.contract(address=contract_address, abi=ABI.abi_woofi_swap)
            allowance = token_contract.functions.allowance(address_wallet, contract_address).call()

            if allowance < amount:
                approve(private_key, from_chain, from_token, contract_address, from_token_address, amount)
                delay(delay_approve)
                nonce = web3.eth.get_transaction_count(address_wallet)

            amountOutMin = get_woofi_amountOutMin(contract, from_token_address, to_token_address, amount)

            contract_txn = contract.functions.swap(
                from_token_address,
                to_token_address,
                amount,
                amountOutMin,
                address_wallet,
                address_wallet,
            ).build_transaction(
                {
                    "from": address_wallet,
                    "nonce": nonce,
                    **gasParams,
                    'gas': int((contract.functions.swap(
                        from_token_address,
                        to_token_address,
                        amount,
                        amountOutMin,
                        address_wallet,
                        address_wallet,
                    ).estimate_gas({'from': address_wallet})) * data_boost_gas[from_chain]['gasPrice']),
                }
            )

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            transaction_status = transaction_receipt['status']

            if transaction_status == 1:

                process_log(private_key, address_wallet, "BUY WOOFI", "SUCCESS", from_chain, from_chain, from_token,
                            readable_amount, error=None)
                update_status_and_write(paths, file_path, i, "Success")
                print_with_time(
                    f'  [BUY WOOFI] Купил ${token_to_buy} за {readable_amount} ${from_token} в {from_chain} | {explorer}tx/{hex_hash}')
                print(f'          {address_wallet}')
                return True
            else:

                return False
        except Exception as error:
            if re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                delay(delay_txn)
                woofi_swap(private_key, from_token, from_chain, amount, token_to_buy, paths, file_path, i)
            else:
                return False
    except Exception as error:
        print(f"Woofi swap error: {error}")
        return False


def choose_and_call_swap(private_key, from_token, from_chain, amount, token_to_buy, paths, file_path, i):
    address_wallet = get_address_wallet(private_key)
    dex_functions = {
        "woofi": woofi_swap,
        "sushi": sushi_swap,
        "inch": inch_swap
    }

    if token_to_buy == "STG":
        stake_status = get_stake_stg_status(private_key, from_chain)
        if not stake_status:
            print_with_time("  Токен STG уже застейкан или баланс достаточный. Пропускаем покупку...")
            print(f'          {address_wallet}')
            return

    dex_options = choose_dex.copy()
    if token_to_buy == "BTCb" and "sushi" in dex_options:
        dex_options.remove("sushi")
    success = False
    while not success and dex_options:

        dex_name = random.choice(dex_options)
        dex_options.remove(dex_name)

        try:
            dex_function = dex_functions[dex_name]
            success = dex_function(private_key, from_token, from_chain, amount, token_to_buy, paths, file_path, i)
            if success == True:
                delay(delay_txn)
                return True
            delay(delay_txn)
        except Exception as e:
            print_with_time(f" Ошибка при вызове {dex_name}_swap: {e}")
            return False


def jumper_swap(private_key, from_token, from_chain, amount, token_to_buy):
    from_chain_info = data_blockchains[from_chain]
    from_network_id = from_chain_info['network_id']
    token_contract_address = from_chain_info[f"{from_token.lower()}_contract"]
    token_to_buy_address = from_chain_info[f"{token_to_buy.lower()}_contract"]

    from_token_decimals = get_token_decimals(from_chain, from_token)
    amount = int(amount * 10 ** from_token_decimals)
    explorer = from_chain_info["explorer"]
    available_rpc = get_valid_rpc(from_chain)
    address_wallet = get_address_wallet(private_key)
    try:
        web3 = Web3(Web3.HTTPProvider(available_rpc))
        gasParams = get_gas_parameters(from_chain, web3, multiply=1)
        get_url = f"https://li.quest/v1/quote?fromChain={from_network_id}&toChain={from_network_id}&fromToken={token_contract_address}&toToken={token_to_buy_address}&fromAddress={address_wallet}&fromAmount={amount}"
        get_response = requests.get(get_url)
        get_data = json.loads(get_response.text)

        toContractCallData = get_data['transactionRequest']['data']
        toContractAddress = web3.to_checksum_address(get_data['transactionRequest']['to'])
        toAmountMin = get_data['includedSteps'][0]['estimate']['toAmountMin']
        gasLimit = get_data['includedSteps'][0]['estimate']['gasCosts']
        approvalAddress = web3.to_checksum_address(get_data['includedSteps'][0]['estimate']['approvalAddress'])
        transactionId = get_data['includedSteps'][0]['id'].replace('-', '') + get_data['id'].replace('-', '')
        transactionId_bytes32 = bytes.fromhex(transactionId)

        token_contract_address = web3.to_checksum_address(token_contract_address)
        token_to_buy_address = web3.to_checksum_address(token_to_buy_address)

        data = [
            {
                'callTo': approvalAddress,
                'approveTo': approvalAddress,
                'sendingAssetId': token_contract_address,
                'receivingAssetId': token_to_buy_address,
                'fromAmount': amount,
                'callData': toContractCallData,
                'requiresDeposit': True,
            }
        ]
        try:
            token_contract = web3.eth.contract(address=token_contract_address, abi=ABI.abi_tokens)
            contract = web3.eth.contract(address=toContractAddress, abi=ABI.abi_jumper)
            allowance = token_contract.functions.allowance(address_wallet, toContractAddress).call()
            if allowance < amount:
                approve(private_key, from_chain, from_token, toContractAddress, token_contract_address)
                delay(delay_approve)

            contract_txn = contract.functions.swapTokensGeneric(
                transactionId_bytes32,
                "jumper.exchange",
                "0x0000000000000000000000000000000000000000",
                address_wallet,
                toAmountMin,
                tuple(data),
            ).build_transaction({
                **gasParams,
                'gas': gasLimit,
                'nonce': web3.eth.get_transaction_count(address_wallet)
            })

            signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_hash = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(hex_hash)
        except Exception as error:
            traceback.print_exc()
            print(error)

    except Exception as error:
        traceback.print_exc()
        print(error)


def get_web3(chain, wallet):
    web3 = Web3(Web3.HTTPProvider(get_valid_rpc(chain)))

    return web3


def woofi_get_min_amount(privatekey, chain, from_token, to_token, amount):
    try:

        if from_token.upper() != to_token.upper():

            # cprint(f'{chain} : {from_token} => {to_token} | {amount}', 'blue')

            slippage = 0.95

            web3 = get_web3(chain, privatekey)
            address_contract = web3.to_checksum_address(data_blockchains['Avalanche']["woofi_contract"])
            contract = web3.eth.contract(address=address_contract, abi=ABI.abi_woofi_swap)

            from_token = Web3.to_checksum_address(from_token)
            to_token = Web3.to_checksum_address(to_token)

            minToAmount = contract.functions.tryQuerySwap(
                from_token,
                to_token,
                amount
            ).call()

            return int(minToAmount * slippage)

        else:

            return int(amount)

    except Exception as error:
        print(error)


def value_woofi_swap(to_token_sell):
    chain = 'Avalanche'

    from_token = '0x152b9d0FdC40C096757F570A51E494bd4b943E50'  # пусто если нативный токен сети
    to_token = data_blockchains['Avalanche'][f"{to_token_sell.lower()}_contract"]  # пусто если нативный токен сети

    amount_from = 0.1  # от какого кол-ва from_token свапаем
    amount_to = 0.2  # до какого кол-ва from_token свапаем

    swap_all_balance = True  # True / False. если True, тогда свапаем весь баланс
    min_amount_swap = 0  # если баланс будет меньше этого числа, свапать не будет
    keep_value_from = 0  # от скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)
    keep_value_to = 0  # до скольки монет оставляем на кошельке (работает только при : swap_all_balance = True)

    return chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to


def add_gas_limit(web3, contract_txn):
    value = contract_txn['value']
    contract_txn['value'] = 0
    pluser = [1.02, 1.05]
    gasLimit = web3.eth.estimate_gas(contract_txn)
    contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))

    contract_txn['value'] = value
    return contract_txn


def add_gas_price(web3, contract_txn):
    gas_price = web3.eth.gas_price
    contract_txn['maxFeePerGas'] = int(gas_price * random.uniform(1.01, 1.02) * 1.1)
    contract_txn['maxPriorityFeePerGas'] = int(gas_price * random.uniform(1.01, 1.02))
    return contract_txn


def check_status_tx(chain, tx_hash):
    start_time_stamp = int(time.time())

    while True:
        try:

            rpc_chain = get_valid_rpc(chain)
            web3 = Web3(Web3.HTTPProvider(rpc_chain))
            status_ = web3.eth.get_transaction_receipt(tx_hash)
            status = status_["status"]

            if status in [0, 1]:
                return status

        except Exception as error:
            return 1


def sign_tx(web3, contract_txn, privatekey):
    signed_tx = web3.eth.account.sign_transaction(contract_txn, privatekey)
    raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash = web3.to_hex(raw_tx_hash)

    return tx_hash, raw_tx_hash


def check_data_token(chain, token_address):
    try:
        web3 = Web3(Web3.HTTPProvider(get_valid_rpc(chain)))
        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ABI.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()
        data = {
            'contract': token_contract,
            'decimal': decimals,
            'symbol': symbol
        }

        return token_contract, decimals, symbol

    except Exception as error:
        print(error)


def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def decimalToInt(qty, decimal):
    return qty / int("".join((["1"] + ["0"] * decimal)))


def check_allowance(chain, token_address, wallet, spender):
    try:
        web3 = Web3(Web3.HTTPProvider(get_valid_rpc(chain)))
        contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ABI.ERC20_ABI)
        amount_approved = contract.functions.allowance(wallet, spender).call()
        return amount_approved
    except Exception as error:
        print(error)


def check_balance(privatekey, chain, address_contract):
    try:

        web3 = get_web3(chain, privatekey)

        try:
            wallet = web3.eth.account.from_key(privatekey).address
        except:
            wallet = privatekey

        if address_contract == '':  # eth
            balance = web3.eth.get_balance(web3.to_checksum_address(wallet))
            token_decimal = 18
        else:
            token_contract, token_decimal, symbol = check_data_token(chain, address_contract)
            balance = token_contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()

        human_readable = decimalToInt(balance, token_decimal)

        # cprint(human_readable, 'blue')

        return human_readable

    except Exception as error:
        time.sleep(1)
        check_balance(privatekey, chain, address_contract)


def approve_(amount, privatekey, chain, token_address, spender, from_token, readeable_amount, retry=0):
    try:
        from_chain_info = data_blockchains[chain]
        explorer = from_chain_info["explorer"]
        web3 = get_web3(chain, privatekey)
        # web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        spender = Web3.to_checksum_address(spender)

        wallet = web3.eth.account.from_key(privatekey).address
        contract, decimals, symbol = check_data_token(chain, token_address)

        module_str = f'approve : {symbol}'

        allowance_amount = check_allowance(chain, token_address, wallet, spender)

        if amount > allowance_amount:
            try:
                contract_txn = contract.functions.approve(
                    spender,
                    amount
                ).build_transaction(
                    {
                        "chainId": web3.eth.chain_id,
                        "from": wallet,
                        "nonce": web3.eth.get_transaction_count(wallet),
                        'type': '0x2',
                        'maxFeePerGas': 0,
                        'maxPriorityFeePerGas': 0,
                        'gas': 0,
                        "value": 0
                    }
                )

                if chain == 'bsc':
                    contract_txn['gasPrice'] = random.randint(1000000000,
                                                              1050000000)  # специально ставим 1 гвей, так транза будет дешевле
                else:
                    contract_txn = add_gas_price(web3, contract_txn)
                contract_txn = add_gas_limit(web3, contract_txn)
                tx_hash, raw_tx_hash = sign_tx(web3, contract_txn, privatekey)
                status = check_status_tx(chain, tx_hash)
                transaction_receipt = web3.eth.wait_for_transaction_receipt(raw_tx_hash)
                transaction_status = transaction_receipt['status']
                if transaction_status == 1:
                    process_log(privatekey, wallet, "APPROVE", "SUCCESS", chain, chain, from_token,
                                readeable_amount, error=None)
                    print_with_time(
                        f'  [APPROVE] Апрувнул {readeable_amount} ${from_token} | {explorer}tx/{tx_hash}')
                    print(f'          {wallet}')
                else:
                    process_log(privatekey, wallet, "APPROVE", "ERROR", chain, chain, from_token,
                                readeable_amount, status)
                    print("ERROR APROVE")
            except Exception as error:
                if re.search("insufficient funds", str(error), re.IGNORECASE):
                    print_with_time(
                        f'  [APPROVE] Не достаточно нативного токена для оплаты газа | Выводим минималку и повторяем операцию...')
                    print(f'          {wallet}')
                    exception_withdraw(privatekey, chain)
                    delay(delay_txn)
                    approve_(amount, privatekey, chain, token_address, spender, from_token, readeable_amount, retry=0)
                elif re.search("is not in the chain after 120 seconds", str(error), re.IGNORECASE):
                    time.sleep(180)
                    approve_(amount, privatekey, chain, token_address, spender, from_token, readeable_amount, retry=0)
                else:
                    process_log(privatekey, wallet, "APPROVE", "ERROR", chain, chain, from_token,
                                readeable_amount, error)
                    print_with_time(
                        f'  [APPROVE] Ошибка при апруве {readeable_amount} {from_token} | {error}')
                    print(f'          {wallet}')
                    traceback.print_exc()

    except Exception as error:
        process_log(privatekey, wallet, "APPROVE", "ERROR", chain, chain, from_token,
                    0, error)
        print_with_time(
            f'  [APPROVE] Возникла ошибка при подключении к RPC | {error}')
        print(f'          {wallet}')
        traceback.print_exc()


def woofi_swap_sell_btcb(private_key, from_token, from_chain, amount, to_token_, paths, file_path, i):
    try:

        from_chain, from_token, to_token, swap_all_balance, amount_from, amount_to, min_amount_swap, keep_value_from, keep_value_to = value_woofi_swap(
            to_token_)
        from_chain_info = data_blockchains[from_chain]
        explorer = from_chain_info["explorer"]
        keep_value = round(random.uniform(keep_value_from, keep_value_to), 8)
        if swap_all_balance == True:
            amount_ = check_balance(private_key, from_chain, from_token) - keep_value
        else:
            amount_ = round(random.uniform(amount_from, amount_to), 8)

        web3 = get_web3(from_chain, private_key)
        address_contract = web3.to_checksum_address(
            data_blockchains['Avalanche']["woofi_contract"]
        )

        if to_token == '': to_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        if from_token == '': from_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        to_token_ = to_token_
        from_token = Web3.to_checksum_address(from_token)
        to_token = Web3.to_checksum_address(to_token)

        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            token_contract, decimals, symbol = check_data_token(from_chain, from_token)
        else:
            decimals = 18

        contract = web3.eth.contract(address=address_contract, abi=ABI.abi_woofi_swap)
        wallet = web3.eth.account.from_key(private_key).address

        amount = intToDecimal(amount_, decimals)

        # если токен не нативный, тогда проверяем апрув и если он меньше нужного, делаем апруваем
        if from_token != '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            approve_(amount, private_key, from_chain, from_token, data_blockchains['Avalanche']["woofi_contract"],
                     from_token, amount_)

        if from_token == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            value = amount
        else:
            value = 0

        minToAmount = woofi_get_min_amount(private_key, from_chain, from_token, to_token, amount)

        if amount_ >= min_amount_swap:
            contract_txn = contract.functions.swap(
                from_token,
                to_token,
                amount,
                minToAmount,
                wallet,
                wallet
            ).build_transaction(
                {
                    'from': wallet,
                    'nonce': web3.eth.get_transaction_count(wallet),
                    'value': value,
                    'type': '0x2',
                    'maxFeePerGas': 0,
                    'maxPriorityFeePerGas': 0,
                    'gas': 0,
                }
            )

            if from_chain == 'bsc':
                contract_txn['gasPrice'] = random.randint(1000000000,
                                                          1050000000)  # специально ставим 1 гвей, так транза будет дешевле
            else:
                contract_txn = add_gas_price(web3, contract_txn)
            contract_txn = add_gas_limit(web3, contract_txn)

            if (from_token == '' and swap_all_balance == True):
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = contract_txn['value'] - gas_gas

            # смотрим газ, если выше выставленного значения : спим
            tx_hash, raw_tx_hash = sign_tx(web3, contract_txn, private_key)
            status = check_status_tx(from_chain, tx_hash)
            if status == 1:

                process_log(private_key, wallet, "SELL WOOFI", "SUCCESS", from_chain, from_chain, from_token,
                            amount_, error=None)
                update_status_and_write(paths, file_path, i, "Success")
                print_with_time(
                    f'  [SELL WOOFI] Продал ${to_token_} за {format(amount_, ".8f")} $BTCb в {from_chain} | {explorer}tx/{tx_hash}')
                print(f'          {wallet}')
                return True
            else:
                return False
    except Exception as error:
        print(f"Woofi swap error: {error}")
        return False

