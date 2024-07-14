from config import *
from modules.natives_parser import parse_exchange_summary
from modules.get_requests import print_with_time
import ccxt
import time


def handle_ccxt_error(e):
    error_type = type(e).__name__
    print_with_time(f"  [OKX][NATIVE] Возникла ошибка {error_type}.")
    # print_with_time(f"  [OKX] Детали ошибки {e}")


def get_okx_balances(exchange):
    try:
        funding_balance = exchange.fetch_balance({'type': 'funding'})
        trading_balance = exchange.fetch_balance()

        total_balance = {}
        for currency, balance in funding_balance['total'].items():
            if currency in trading_balance['total']:
                total_balance[currency] = balance + trading_balance['total'][currency]
            else:
                total_balance[currency] = balance

        for currency, balance in trading_balance['total'].items():
            if currency not in total_balance:
                total_balance[currency] = balance
    except (ccxt.PermissionDenied, ccxt.AccountSuspended, ccxt.AuthenticationError, ccxt.BadResponse,
            ccxt.ExchangeError, ccxt.RateLimitExceeded, ccxt.DDoSProtection, ccxt.ExchangeNotAvailable,
            ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError) as e:
        handle_ccxt_error(e)

    return funding_balance, trading_balance, total_balance


def transfer_funding_to_trading(exchange):
    funding_balance, _, _ = get_okx_balances(exchange)

    usdt_balance = funding_balance['total'].get('USDT', 0)
    usdt_balance = float(exchange.decimal_to_precision(usdt_balance, rounding_mode=0, precision=5, counting_mode=2,
                                                       padding_mode=5))

    time.sleep(2)

    try:
        if usdt_balance > 0:
            print_with_time(f"  [OKX][NATIVE] Перевожу {usdt_balance} USDT из основного аккаунта на торговый.")
            transfer = exchange.transfer('USDT', usdt_balance, '6', '18')
            transfer_id = transfer['id']

            while True:
                time.sleep(2)
                transfer_info = exchange.fetch_transfer(transfer_id, 'USDT')
                if transfer_info['status'] == 'success':
                    print_with_time(f"  [OKX][NATIVE] Перевод USDT из основного аккаунта на торговый прошел успешно.")
                    break

        else:
            print_with_time(f"  [OKX][NATIVE] На основном аккаунте нет USDT для перевода на торговый.")

    except (ccxt.InsufficientFunds, ccxt.PermissionDenied, ccxt.AccountSuspended, ccxt.AuthenticationError,
            ccxt.BadResponse, ccxt.ExchangeError, ccxt.RateLimitExceeded, ccxt.DDoSProtection,
            ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError) as e:
        handle_ccxt_error(e)


def transfer_trading_to_funding(exchange):
    _, trading_balance, _ = get_okx_balances(exchange)

    for currency, balance in trading_balance['total'].items():
        balance = float(exchange.decimal_to_precision(balance, rounding_mode=0, precision=4, counting_mode=2,
                                                      padding_mode=5))

        time.sleep(2)

        try:
            if balance > 0:
                print_with_time(f"  [OKX][NATIVE] Перевожу {balance} {currency} из торгового аккаунта на основной.")
                transfer = exchange.transfer(currency, balance, '18', '6')
                transfer_id = transfer['id']

                while True:
                    time.sleep(2)
                    transfer_info = exchange.fetch_transfer(transfer_id, currency)
                    if transfer_info['status'] == 'success':
                        print_with_time(f"  [OKX][NATIVE] Перевод {currency} из торгового аккаунта на основной прошел успешно.")
                        break

            else:
                print_with_time(f"  [OKX][NATIVE] На торговом аккаунте нет {currency} для перевода на основной.")

        except (ccxt.InsufficientFunds, ccxt.PermissionDenied, ccxt.AccountSuspended, ccxt.AuthenticationError,
                ccxt.BadResponse, ccxt.ExchangeError, ccxt.RateLimitExceeded, ccxt.DDoSProtection,
                ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError) as e:
            handle_ccxt_error(e)


def process_natives(exchange, min_amount):
    natives = parse_exchange_summary()
    wd_fee = {
        'AVAX': 0.0128,
        'MATIC': 0.96,
        'USDC': 1.6,
        'CORE': 0.002,
        'ETH': 0.0002,
        'BNB': 0.004
    }
    amounts = {}

    for currency, value in natives.items():

        try:
            pair = currency
            if pair == 'USDT':
                continue
            else:
                pair += "/USDT"

            if currency in natives:
                amount = natives[currency]
                if pair in min_amount and amount < min_amount[pair]:
                    amount = min_amount[pair]

                taker_fee_info = exchange.fetch_trading_fee(pair)
                taker_fee = float(taker_fee_info['taker'])

                fee = wd_fee.get(currency, 0)
                amount_to_buy = (amount + fee) / (1 - taker_fee)

                amounts[pair] = (amount_to_buy, currency)
            else:
                amounts[pair] = (0, currency)

        except (ccxt.PermissionDenied, ccxt.AccountSuspended, ccxt.AuthenticationError, ccxt.BadResponse,
                ccxt.ExchangeError, ccxt.RateLimitExceeded, ccxt.DDoSProtection, ccxt.ExchangeNotAvailable,
                ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError, Exception, ValueError, KeyError) as e:
            handle_ccxt_error(e)

    return amounts


def okx_buy(exchange, min_amount):
    pairs_and_amounts = process_natives(exchange, min_amount)
    _, _, total_balance = get_okx_balances(exchange)
    # print_with_time(f"Total Balance: {total_balance}")

    for pair, amount_and_currency in pairs_and_amounts.items():
        amount, currency = amount_and_currency
        current_balance = total_balance.get(currency, 0)

        time.sleep(2)

        try:
            if pair == 'USDT':
                continue
            elif current_balance > amount:
                print_with_time(f"  [OKX][NATIVE] На аккаунте уже достаточно {currency} для оплаты газа. Пропускаю покупку...")
            else:
                print_with_time(f"  [OKX][NATIVE] Закупаю {amount} {currency}.")
                order = exchange.create_order(pair, 'market', 'buy', amount)
                print_with_time(f"  [OKX][NATIVE] Ордер на покупку {amount} {currency} создан.")
                order_id = order["id"]

                while True:
                    time.sleep(2)
                    order_info = exchange.fetch_order(order_id, pair)
                    size = order_info["filled"]
                    if order_info['status'] == 'closed':
                        print_with_time(f"  [OKX][NATIVE] Купил {size} {currency}.")
                        break

        except (ccxt.InsufficientFunds, ccxt.PermissionDenied, ccxt.AccountSuspended, ccxt.AuthenticationError,
                ccxt.BadResponse, ccxt.ExchangeError, ccxt.RateLimitExceeded, ccxt.DDoSProtection,
                ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError) as e:
            handle_ccxt_error(e)


def okx_main():
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

    min_amount = {
        'USDC/USDT': 1,
        'AVAX/USDT': 0.01,
        'BNB/USDT': 0.01,
        'CORE/USDT': 1,
        'ETH/USDT': 0.0001,
        'MATIC/USDT': 1,
    }

    print_with_time("  [OKX][NATIVE] Начинаю закупать нативные токены на okx.")
    exchange = ccxt.okx(exchange_options)
    transfer_funding_to_trading(exchange)
    okx_buy(exchange, min_amount)
    transfer_trading_to_funding(exchange)
    print_with_time("  [OKX][NATIVE] Покупка нативных токенов на okx завершена, переходим к основной работе.")
