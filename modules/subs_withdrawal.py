import time
from datetime import datetime
from modules.get_requests import print_with_time
import requests
import hmac
import json
import base64
import hashlib
import config

base_url = "https://www.okx.com"


def get_request_proxies():
    if config.use_okx_proxy:
        return {"http": config.okx_proxy, "https": config.okx_proxy}
    return {}


def get_sub_accounts():
    method = "GET"
    endpoint = "/api/v5/users/subaccount/list"
    url = base_url + endpoint
    headers = get_request_headers(method, endpoint, "")

    try:
        response = requests.get(url, headers=headers, proxies=get_request_proxies())
        json_response = response.json()
        if 'data' in json_response:
            return json_response["data"]
        else:
            print_with_time(f"  Ошибка при получении списка суб-аккаунтов: {json_response}")
            return []
    except Exception as e:
        print_with_time(f"  Ошибка при получении списка суб-аккаунтов: {e}")
        return []


def get_sub_account_funding_balance(sub_account_id, ccy=None):
    method = "GET"
    endpoint = "/api/v5/asset/subaccount/balances"
    params = f"?subAcct={sub_account_id}"

    if ccy is not None:
        params += f"&ccy={ccy}"

    url = base_url + endpoint + params
    headers = get_request_headers(method, endpoint, params)

    try:
        response = requests.get(url, headers=headers, proxies=get_request_proxies())
        return response.json()["data"]
    except Exception as e:
        print_with_time(f"  Ошибка при получении баланса суб-аккаунта {sub_account_id}: {e}")
        return []


def get_request_headers(method, endpoint, request_params, body='', sub_account_id=None):
    timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    message = timestamp + method + endpoint + request_params + body
    mac = hmac.new(config.okx_apisecret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
    sign = base64.b64encode(mac.digest()).decode("utf-8")

    headers = {
        "OK-ACCESS-KEY": config.okx_apikey,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-passphrase": config.okx_passphrase,
        "Content-Type": "application/json"
    }

    if sub_account_id is not None:
        headers["OK-ACCESS-SUBACCOUNT"] = sub_account_id

    return headers


def transfer_to_master_account(from_sub_account, ccy, amount):
    method = "POST"
    endpoint = "/api/v5/asset/transfer"
    url = base_url + endpoint
    payload = {
        "ccy": ccy,
        "amt": amount,
        "from": "6",
        "to": "6",
        "subAcct": from_sub_account,
        "type": "2"
    }
    json_payload = json.dumps(payload)
    headers = get_request_headers(method, endpoint, "", json_payload)
    try:
        response = requests.post(url, headers=headers, json=payload, proxies=get_request_proxies())
        response_data = response.json()
        if "data" in response_data and len(response_data["data"]) > 0:
            transfer_id = response_data["data"][0]["transId"]
            print_with_time(f"  Переведено {amount} {ccy} с суб-аккаунта {from_sub_account} на мастер-аккаунт (ID транзакции: {transfer_id})")
        elif "code" in response_data and "msg" in response_data:
            print_with_time(f"  Ошибка при переводе {amount} {ccy} с суб-аккаунта {from_sub_account} на мастер-аккаунт: {response_data['msg']} (Код ошибки: {response_data['code']})")
        else:
            print_with_time(f"  Ошибка при переводе {amount} {ccy} с суб-аккаунта {from_sub_account} на мастер-аккаунт: Неизвестная ошибка")
    except Exception as e:
        print_with_time(f"  Ошибка при переводе {amount} {ccy} с суб-аккаунта {from_sub_account} на мастер-аккаунт: {e}")


def okx_withdrawal_subs():
    sub_account_list = get_sub_accounts()

    for sub_account in sub_account_list:
        sub_account_id = sub_account["subAcct"]
        balances = get_sub_account_funding_balance(sub_account_id)
        for balance in balances:
            currency = balance["ccy"]
            available = balance["availBal"]
            transfer_to_master_account(sub_account_id, currency, available)


def get_trading_account_balance(ccy=None):
    method = "GET"
    endpoint = "/api/v5/account/balance"
    params = ""

    if ccy is not None:
        params += f"?ccy={ccy}"

    url = base_url + endpoint + params
    headers = get_request_headers(method, endpoint, params)
    proxies = get_request_proxies()

    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        data = response.json()["data"]
        balances = []
        for item in data:
            for balance in item["details"]:
                balances.append(balance)
        return balances
    except Exception as e:
        print_with_time(f"  Ошибка при получении баланса торгового аккаунта: {e}")
        return []


def transfer_spot_to_funding(ccy, amount):
    method = "POST"
    endpoint = "/api/v5/asset/transfer"
    url = base_url + endpoint
    payload = {
        "ccy": ccy,
        "amt": amount,
        "from": "18",
        "to": "6",
    }

    json_payload = json.dumps(payload)
    headers = get_request_headers(method, endpoint, "", json_payload)
    proxies = get_request_proxies()

    try:
        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        response_data = response.json()
        if "data" in response_data and len(response_data["data"]) > 0:
            transfer_id = response_data["data"][0]["transId"]
            print_with_time(f"  Переведено {amount} {ccy} с trading-счета на funding-счет (ID транзакции: {transfer_id})")
        elif "code" in response_data and "msg" in response_data:
            print_with_time(f"  Ошибка при переводе {amount} {ccy} с trading-счета на funding-счет: {response_data['msg']} (Код ошибки: {response_data['code']})")
        else:
            print_with_time(f"  Ошибка при переводе {amount} {ccy} с trading-счета на funding-счет: Неизвестная ошибка")
    except Exception as e:
        print_with_time(f"  Ошибка при переводе {amount} {ccy} с trading-счета на funding-счет: {e}")


def okx_transfer():
    if any('okx' in exchange_list for exchange_list in config.list_withdrawal_rules.values()):
        print_with_time(f"  [OKX] Начинаем перевод токенов из торгового аккаунта в основной...")
        okx_withdrawal_subs()
        trading_account_balances = get_trading_account_balance()
        for balance in trading_account_balances:
            currency = balance["ccy"]
            available = balance["availBal"]
            transfer_spot_to_funding(currency, available)
            time.sleep(3)
        print_with_time(f"  [OKX] Закончили перевод токенов из торгового аккаунта в основной, начинаем основную работу...")
    else:
        print_with_time(f"  Вы не используйте биржу OKX, пропускаем сбор токенов с суб-аккаунтов и трансфер на спот-баланс...")


if __name__ == '__main__':
    okx_transfer()
