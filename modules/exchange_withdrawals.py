from config import *
from modules.logs import *

import traceback
import ccxt
import re

min_withdrawal = {
    'BSC': 0.00001,
    'Avalanche': 0.1,
    'Core': 0.1,
    'Arbitrum': 0.001,
    'Polygon': 0.001,
}

def binance_withdraw(private_key, amount: float, symbolWithdraw, network, original_network, paths, file_path, i):
    address_wallet = get_address_wallet(private_key)

    exchange_options = {
        'apiKey': binance_apikey,
        'secret': binance_apisecret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    }

    if use_binance_proxy:
        exchange_options['proxies'] = {
            'http': binance_proxy,
            'https': binance_proxy,
        }

    exchange = ccxt.binance(exchange_options)
    currencies = exchange.fetch_currencies()
    currency = currencies[symbolWithdraw]
    networks = currency['info']['networkList']
    min_withdrawal_amount = None

    for net in networks:
        if net['network'] == network:
            min_withdrawal_amount = float(net['withdrawMin'])
            break

    if min_withdrawal_amount is None:
        print_with_time(
            f'  [WITHDRAWAL][Binance] Не удалось найти информацию о минимальной сумме вывода для {symbolWithdraw} в сети {network}')
        return True

    if amount < min_withdrawal_amount:
        boost = random.uniform(min_boost[0], min_boost[1]) / 100
        amount = min_withdrawal_amount * (1 + boost)
        print_with_time(
            f'  [WITHDRAWAL][Binance] Сгенерированная сумма меньше минимальной для вывода, минимальная: {min_withdrawal_amount} ${symbolWithdraw}')
        print(f'          {address_wallet}')
    fee = get_binance_withdrawal_fee(symbolWithdraw, network)
    amount_with_fee = smart_round(amount + fee)

    if symbolWithdraw == 'USDC':
        if not usdc_swap_binance(address_wallet, exchange, amount_with_fee):
            print_with_time(f"  [WITHDRAWAL][Binance] Не удалось свапнуть USDT на USDC, вывод прерван")
            return True
    try:
        withdrawal = exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_with_fee,
            address=address_wallet,
            tag=None,
            params={
                "network": network
            }
        )

        withdrawal_id = withdrawal['id']
        status = "pending"

        while status == "pending":
            time.sleep(random.uniform(42, 115))
            fetched_withdrawal = exchange.fetch_withdrawals()
            for fetched_withdrawal in fetched_withdrawal:
                if fetched_withdrawal['id'] == withdrawal_id:
                    status = fetched_withdrawal['status']
                    break

        if status == "ok":
            process_log(private_key, address_wallet, "WITHDRAWAL", "SUCCESS", "Binance", original_network,
                        symbolWithdraw, amount_with_fee,
                        error=None)
            print_with_time(f'  [WITHDRAWAL][Binance] Вывел {amount_with_fee} ${symbolWithdraw} в {original_network} ')
            print(f'          {address_wallet}')
            if paths != "Error":
                update_status_and_write(paths, file_path, i, "Success")
        else:
            process_log(private_key, address_wallet, "WITHDRAWAL", "ERROR", "Binance", original_network, symbolWithdraw,
                        amount_with_fee, status)
            print_with_time(
                f'  [WITHDRAWAL][Binance] Не удалось вывести {amount_with_fee} ${symbolWithdraw} в {original_network} : вывод был отменен или неудачен')
            print(f'          {address_wallet}')
            return True

    except Exception as error:
        process_log(private_key, address_wallet, "WITHDRAWAL", "ERROR", "Binance", original_network, symbolWithdraw,
                    amount_with_fee, error)
        print_with_time(
            f'  [WITHDRAWAL][Binance] Не удалось вывести {amount} ${symbolWithdraw} в {original_network} : {error} ')
        print(f'          {address_wallet}')
        return True


def get_binance_withdrawal_fee(symbolWithdraw, network):
    exchange_options = {
        'apiKey': binance_apikey,
        'secret': binance_apisecret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    }

    if use_binance_proxy:
        exchange_options['proxies'] = {
            'http': binance_proxy,
            'https': binance_proxy,
        }

    exchange = ccxt.binance(exchange_options)
    currencies = exchange.fetch_currencies()
    currency = currencies[symbolWithdraw]
    networks = currency['info']['networkList']

    for net in networks:
        if net['network'] == network:
            return float(net['withdrawFee'])

    raise ValueError(f"  [BINANCE] Не могу найти комиссию для токена ${symbolWithdraw} в сети {network}")


def usdc_swap_binance(address, exchange, amount_usdc):
    trading_pair = 'USDC/USDT'
    order_type = 'market'
    side = 'buy'

    increase_percentage = random.uniform(1, 2)
    amount_with_boost = smart_round(amount_usdc * (1 + (increase_percentage / 100)))
    try:
        balance = exchange.fetch_balance()
        available_usdc = balance['USDC']['free']
        available_usdt = balance['USDT']['free']
        if available_usdc >= amount_usdc:
            print_with_time(
                f"  [BINANCE-SWAP] Достаточно USDC на балансе: {smart_round(available_usdc)} USDC. Пропускаем обмен...")
            print(f'          {address}')
            return True
        elif available_usdt >= amount_with_boost:
            order = exchange.create_order(trading_pair, order_type, side, amount_with_boost)
            order_id = order['id']
            time.sleep(15)
            fetched_order = exchange.fetch_order(order_id, trading_pair)
            if fetched_order['status'] == 'closed' or fetched_order['status'] == 'filled':
                print_with_time(f"  [BINANCE-SWAP] Успешно обменяли {amount_with_boost} USDT на USDC")
                print(f'          {address}')
                time.sleep(random.uniform(55, 77))
                return True
            else:
                print_with_time(f"  [BINANCE-SWAP] Ошибка при обмене USDT на USDC: ордер не был выполнен")
                print(f'          {address}')
                return False
        else:
            print_with_time(
                f"  [BINANCE-SWAP] Недостаточно средств для обмена: доступно {smart_round(available_usdt)} USDT, требуется {amount_with_boost} USDT")
            print(f'          {address}')
            return False
    except Exception as error:
        print_with_time(f"  [BINANCE-SWAP] Ошибка при обмене USDT на USDC: {error}")
        print(f'          {address}')
        return False


def okx_withdraw(private_key, amount: float, symbolWithdraw, network, original_network, paths, file_path, i):
    address_wallet = get_address_wallet(private_key)
    exchange_options = {
        'apiKey': okx_apikey,
        'secret': okx_apisecret,
        'password': okx_passphrase,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    }

    if use_okx_proxy:
        exchange_options['proxies'] = {
            'http': okx_proxy,
            'https': okx_proxy,
        }

    exchange = ccxt.okx(exchange_options)

    chainName = symbolWithdraw + "-" + network

    currencies = exchange.fetch_currencies()
    currency = currencies.get(symbolWithdraw)
    if currency is None:
        print_with_time(f'  [WITHDRAWAL][OKX] Не удалось найти информацию о валюте {symbolWithdraw}')
        return True

    networks = currency['networks']
   
    min_withdrawal_amount = None
    for net_name, net in networks.items():
        if net['info']['chain'] == chainName:
            min_withdrawal_amount = float(net['limits']['withdraw']['min'])
            break
    min_withdrawal_amount = min_withdrawal[original_network]
    # if min_withdrawal_amount is None:
    #     print_with_time(
    #         f'  [WITHDRAWAL][OKX] Не удалось найти информацию о минимальной сумме вывода для {symbolWithdraw} в сети {network}')
    #     return True

    if amount < float(min_withdrawal_amount):
        boost = random.uniform(min_boost[0], min_boost[1]) / 100
        amount = min_withdrawal_amount * (1 + boost)
        print_with_time(
            f'  [WITHDRAWAL][OKX] Сгенерированная сумма меньше минимальной для вывода, минимальная: {min_withdrawal_amount} ${symbolWithdraw}')
        print(f'          {address_wallet}')

    fee = get_okx_withdrawal_fee(symbolWithdraw, chainName)
    amount_with_fee = smart_round(amount + fee)

    try:
        withdraw = exchange.withdraw(symbolWithdraw, amount_with_fee, address_wallet,
                                     params={
                                         "toAddress": address_wallet,
                                         "chainName": chainName,
                                         "dest": 4,
                                         "fee": fee,
                                         "pwd": '-',
                                         "amt": amount_with_fee,
                                         "network": network
                                     }
                                     )

        withdrawal_id = withdraw['id']
        status = "pending"
        while status == "pending":
            time.sleep(random.uniform(52, 117))
            fetched_withdrawal = exchange.fetch_withdrawals()
            for fetched_withdrawal in fetched_withdrawal:
                if fetched_withdrawal['id'] == withdrawal_id:
                    status = fetched_withdrawal['status']
                    break
        print_with_time(f'  [WITHDRAWAL][OKX] Ожидаем пополнение на  {round(amount, 4)} ${symbolWithdraw} в {original_network} ')
        print(f'          {address_wallet}')
        if status == "ok":
            process_log(private_key, address_wallet, "WITHDRAWAL", "SUCCESS", "OKX", original_network, symbolWithdraw,
                        amount, error=None)
            print_with_time(f'  [WITHDRAWAL][OKX] Вывел {round(amount, 10)} ${symbolWithdraw} в {original_network} ')
            print(f'          {address_wallet}')
            if paths != "Error":
                update_status_and_write(paths, file_path, i, "Success")
            return True
        else:
            process_log(private_key, address_wallet, "WITHDRAWAL", "ERROR", "OKX", original_network, symbolWithdraw,
                        amount, status)
            print_with_time(
                f'  [WITHDRAWAL][OKX] Не удалось вывести {round(amount, 4)} ${symbolWithdraw}  в {original_network}: вывод был отменен или неудачен')
            print(f'          {address_wallet}')
            return False
    except Exception as error:
        if re.search("Withdrawal address is not whitelisted", str(error), re.IGNORECASE):
            print_with_time(
                f'  [WITHDRAWAL][OKX] Адрес не в вайтлисте! Добавьте адрес как универсальный для {original_network}, и я продолжу работать... ')
            print(f'          {address_wallet}')
            print(error)
            return True
        else:
            process_log(private_key, address_wallet, "WITHDRAWAL", "ERROR", "OKX", original_network, symbolWithdraw,
                        round(amount, 3), error)
            print_with_time(
                f'  [WITHDRAWAL][OKX] Не удалось вывести {round(amount, 4)} ${symbolWithdraw}  в {original_network}: {error} ')
            print(f'          {address_wallet}')
            print(error)
            return True


def get_okx_withdrawal_fee(symbolWithdraw, chainName):
    try:
        exchange_options = {
            'apiKey': okx_apikey,
            'secret': okx_apisecret,
            'password': okx_passphrase,
            'enableRateLimit': True
        }

        if use_okx_proxy:
            exchange_options['proxies'] = {
                'http': okx_proxy,
                'https': okx_proxy,
            }

        exchange = ccxt.okx(exchange_options)
        # print('symbolWithdraw',symbolWithdraw)
        # print('chainName',chainName)
        currencies = exchange.fetch_currencies()
        for currency in currencies:
            #print('currency',currency)
            if currency == symbolWithdraw:
                #print('currency',currency)
                currency_info = currencies[currency]
                #print('currency_info',currency_info)
                network_info = currency_info.get('networks', None)
                if network_info:
                    #print('network_info',network_info)
                    for network in network_info:
                        network_data = network_info[network]
                        network_id = network_data['id']
                        if network_id == chainName:
                            withdrawal_fee = currency_info['networks'][network]['fee']
                            if withdrawal_fee == 0:
                                return 0
                            else:
                                #print('withdrawal_fee',withdrawal_fee)
                                return withdrawal_fee
    except Exception as e:
        print(e)
        return False
    #raise ValueError(f"  [OKX] Не могу найти комиссию для токена ${symbolWithdraw} в сети {chainName}")


def mexc_withdraw(private_key, amount: float, symbolWithdraw, network, original_network, paths, file_path, i):
    address_wallet = get_address_wallet(private_key)
    exchange_options = ({
        'apiKey': mexc_apikey,
        'secret': mexc_apisecret,
        'enableRateLimit': True,
        'options': {
            'createMarketBuyOrderRequiresPrice': False
        }
    })

    if use_mexc_proxy:
        exchange_options['proxies'] = {
            'http': mexc_proxy,
            'https': mexc_proxy,
        }

    exchange = ccxt.mexc(exchange_options)
    currencies = exchange.fetch_currencies()
    currency = currencies[symbolWithdraw]
    networks = currency['info']['networkList']

    min_withdrawal_amount = None
    for net in networks:
        if net['network'] == network:
            min_withdrawal_amount = float(net['withdrawMin'])
            break

    if min_withdrawal_amount is None:
        print_with_time(
            f'  [WITHDRAWAL][MEXC] Не удалось найти информацию о минимальной сумме вывода для {symbolWithdraw} в сети {network}')
        return True

    if amount < float(min_withdrawal_amount):
        boost = random.uniform(min_boost[0], min_boost[1]) / 100
        amount = min_withdrawal_amount * (1 + boost)
        print_with_time(
            f'  [WITHDRAWAL][MEXC] Сгенерированная сумма меньше минимальной для вывода, минимальная: {min_withdrawal_amount} ${symbolWithdraw}')
        print(f'          {address_wallet}')

    fee = get_mexc_withdrawal_fee(symbolWithdraw, network)
    amount_with_fee = smart_round(amount + fee)

    if symbolWithdraw == 'USDC':
        if not usdc_swap_mexc(address_wallet, exchange, amount_with_fee):
            print_with_time(f"  [WITHDRAWAL][MEXC] Не удалось свапать USDT на USDC, вывод прерван")
            print(f'          {address_wallet}')
            return True

    try:
        withdrawal = exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_with_fee,
            address=address_wallet,
            tag=None,
            params={
                "network": network
            }
        )

        withdrawal_id = withdrawal['id']
        status = "pending"

        while status == "pending":
            time.sleep(random.uniform(36, 117))
            fetched_withdrawal = exchange.fetch_withdrawals()
            for fetched_withdrawal in fetched_withdrawal:
                if fetched_withdrawal['id'] == withdrawal_id:
                    status = fetched_withdrawal['status']
                    break

        if status == "ok":
            process_log(private_key, address_wallet, "WITHDRAWAL", "SUCCESS", "MEXC", original_network, symbolWithdraw,
                        amount_with_fee, error=None)
            print_with_time(f'  [WITHDRAWAL][MEXC] Вывел {amount_with_fee} ${symbolWithdraw} в {original_network} ')
            print(f'          {address_wallet}')
            if paths != "Error":
                update_status_and_write(paths, file_path, i, "Success")
        else:
            process_log(private_key, address_wallet, "WITHDRAWAL", "ERROR", "MEXC", original_network, symbolWithdraw,
                        amount_with_fee, status)
            print_with_time(
                f'  [WITHDRAWAL][MEXC] Не удалось вывести {amount_with_fee} ${symbolWithdraw} в {original_network} : вывод был отменен или неудачен')
            print(f'          {address_wallet}')
            return True
    except Exception as error:
        process_log(private_key, address_wallet, "WITHDRAWAL", "ERROR", "MEXC", original_network, symbolWithdraw,
                    round(amount, 3), error)
        print_with_time(
            f'  [WITHDRAWAL][MEXC] Не удалось вывести {amount_with_fee} ${symbolWithdraw} в {original_network} : {error} ')
        print(f'          {address_wallet}')
        return True


def get_mexc_withdrawal_fee(symbolWithdraw, network):
    exchange_options = ({
        'apiKey': mexc_apikey,
        'secret': mexc_apisecret,
        'enableRateLimit': True,
        'options': {
            'createMarketBuyOrderRequiresPrice': False
        }
    })

    if use_mexc_proxy:
        exchange_options['proxies'] = {
            'http': mexc_proxy,
            'https': mexc_proxy,
        }

    exchange = ccxt.mexc(exchange_options)
    currencies = exchange.fetch_currencies()
    currency = currencies[symbolWithdraw]
    networks = currency['info']['networkList']

    for net in networks:
        if net['network'] == network:
            return float(net['withdrawFee'])

    raise ValueError(f"  [MEXC] Не могу найти комиссию для токена ${symbolWithdraw} в сети {network}")


def usdc_swap_mexc(address, exchange, amount_usdc):
    trading_pair = 'USDC/USDT'
    order_type = 'market'
    side = 'buy'

    increase_percentage = random.uniform(1, 2)
    amount_with_boost = smart_round(amount_usdc * (1 + (increase_percentage / 100)))

    try:
        balance = exchange.fetch_balance()
        available_usdc = balance['USDC']['free']
        available_usdt = balance['USDT']['free']

        if available_usdc >= amount_usdc:
            print_with_time(f"  [MEXC-SWAP] Достаточно USDC на балансе: {smart_round(available_usdc)} USDC")
            print(f'          {address}')
            return True
        elif available_usdt >= amount_with_boost:
            order = exchange.create_order(trading_pair, order_type, side, amount_with_boost, None,
                                          {'quoteOrderQty': amount_with_boost})
            order_id = order['id']
            time.sleep(15)
            fetched_order = exchange.fetch_order(order_id, trading_pair)
            if fetched_order['status'] == 'closed' or fetched_order['status'] == 'filled':
                print_with_time(f"  [MEXC-SWAP] Успешно обменяли {amount_with_boost} USDT на USDC")
                print(f'          {address}')
                time.sleep(random.uniform(57, 127))
                return True
            else:
                print_with_time(f"  [MEXC-SWAP] Ошибка при обмене USDT на USDC: ордер не был выполнен")
                print(f'          {address}')
                return False
        else:
            print_with_time(
                f"  [MEXC-SWAP] Недостаточно средств для обмена: доступно {available_usdt} USDT, требуется {amount_with_boost} USDT")
            print(f'          {address}')
            return False
    except Exception as error:
        print_with_time(f"  [MEXC-SWAP] Ошибка при обмене USDT на USDC: {error}")
        print(f'          {address}')
        return False


def choose_exchange(network, token):
    withdrawal_rules = list_withdrawal_rules
    exchange_list = withdrawal_rules.get((network, token))
    if exchange_list is None:
        raise ValueError(f"  Для сети '{network}' и токена'{token}' не указана биржа [function: choose_exchange]")

    return random.choice(exchange_list)


def exception_withdraw(private_key, from_chain, paths="Error", file_path="Error", i=0):
    from_token = data_blockchains[from_chain]["native"]
    currect_cex = choose_exchange(from_chain, from_token)
    currect_network = get_network_format(from_chain, currect_cex)

    function_name = f"{currect_cex}_withdraw"
    token_withdrawal = globals().get(function_name)
    token_withdrawal(private_key, 0, from_token, currect_network, from_chain, paths, file_path, i)


def call_exchange_withdraw(exchange_name, private_key, amount: float, symbolWithdraw, original_network, paths,
                           file_path, i):
    try:
        native_token_balance = get_native_token_balance(private_key, original_network)
        balance = float(Decimal(native_token_balance) * Decimal('1.05'))
        
        usdt_contract = data_blockchains[original_network]["usdt_contract"]
        
        usdc_contract = data_blockchains[original_network]["usdc_contract"]
        balance_usdt = get_token_balance(private_key, original_network, 'USDT')
        balance_usdc = get_token_balance(private_key, original_network, 'USDC')
        address_wallet = get_address_wallet(private_key)
        network = get_network_format(original_network, exchange_name)
        exchange_functions = {
            "binance": binance_withdraw,
            "okx": okx_withdraw,
            "mexc": mexc_withdraw,
        }

        if exchange_name not in exchange_functions:
            print_with_time(f"  Неизвестная биржа: {exchange_name}")
            return True

        if balance < amount:
            print_with_time(
                f'  [WITHDRAWAL][{exchange_name}] Начинаем выводить  {symbolWithdraw} на сумму {amount}')
            print(f'          {address_wallet}')
            withdraw_function = exchange_functions[exchange_name]
            withdraw_result = withdraw_function(private_key, amount, symbolWithdraw, network, original_network, paths,
                                                file_path, i)
            return withdraw_result
        elif symbolWithdraw == 'USDT' and (balance_usdt < amount):
            print_with_time(
                f'  [WITHDRAWAL][{exchange_name}] Начинаем выводить  {symbolWithdraw} на сумму {amount}')
            print(f'          {address_wallet}')
            withdraw_function = exchange_functions[exchange_name]
            withdraw_result = withdraw_function(private_key, amount, symbolWithdraw, network, original_network, paths,
                                                file_path, i)
            return withdraw_result
        elif symbolWithdraw == 'USDC' and (balance_usdc < amount):
            print_with_time(
                f'  [WITHDRAWAL][{exchange_name}] Начинаем выводить  {symbolWithdraw} на сумму {amount}')
            print(f'          {address_wallet}')
            withdraw_function = exchange_functions[exchange_name]
            withdraw_result = withdraw_function(private_key, amount, symbolWithdraw, network, original_network, paths,
                                                file_path, i)
            return withdraw_result
        else:
            print_with_time(
                f'  [WITHDRAWAL][{exchange_name}] Баланс токена {smart_round(balance)} {symbolWithdraw} достаточный, пропускаем вывод...')
            print(f'          {address_wallet}')
            update_status_and_write(paths, file_path, i, "Success")
            return True
 

    except Exception as e:
        print_with_time(f"  Ошибка при выполнении функции 'call_exchange_withdraw': {e}")
        traceback.print_exc()
