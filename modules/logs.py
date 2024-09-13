from bs4 import BeautifulSoup
from threading import Lock
from collections import defaultdict
from modules.get_requests import *
from jinja2 import Environment, FileSystemLoader

import shutil
import os
import json

log_lock = Lock()
current_day = datetime.datetime.now().day


def log_transactions(private_key, wallet_address, transaction_type, status, from_network=None,
                     to_network=None, token=None, amount=None):
    global current_day

    entry = {
        "datetime": datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        "private_key": private_key,
        "wallet_address": wallet_address,
        "transaction_type": transaction_type,
        "status": status,
        "from_network": from_network,
        "to_network": to_network,
        "token": token,
        "amount": amount
    }

    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    if not os.path.exists("./logs/json"):
        os.makedirs("./logs/json")

    filename = "./logs/all_transactions.html"

    if not os.path.exists("./logs/history"):
        os.makedirs("./logs/history")

    if datetime.datetime.now().day != current_day:
        current_day = datetime.datetime.now().day

        if os.path.exists(filename):
            filename_copy = f"./logs/history/all_transactions_{datetime.datetime.now().strftime('%Y_%m_%d')}.html"
            shutil.copy2(filename, filename_copy)
            with open(filename, 'w') as file:
                file.write('')  # Это очистит файл

    with open("./logs/json/transactions.json", "a+") as transactions_file:
        transactions_file.seek(0)
        try:
            entries = json.load(transactions_file)
        except json.JSONDecodeError:
            entries = []

        matching_entries = [e for e in entries if e["private_key"] == private_key]

        if not matching_entries:
            entries.append(entry)
        else:
            matching_entries = sorted(matching_entries,
                                      key=lambda x: datetime.datetime.strptime(x["datetime"], '%d.%m.%Y %H:%M:%S'),
                                      reverse=True)
            last_entry = matching_entries[0]
            last_entry_index = entries.index(last_entry)
            entries.insert(last_entry_index + 1, entry)

        entries = sorted(entries, key=lambda x: (
        x['private_key'], datetime.datetime.strptime(x["datetime"], '%d.%m.%Y %H:%M:%S')))

        transactions_file.truncate(0)
        json.dump(entries, transactions_file, indent=2)

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template/all_template.html")

    with open(filename, "w") as transactions_file:
        transactions_file.write(template.render(entries=entries))


def log_failed_account(private_key, wallet_address, transaction_type, from_network=None, to_network=None,
                       token=None, amount=None, error=None):
    global current_day

    entry = {
        "datetime": datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        "private_key": private_key,
        "wallet_address": wallet_address,
        "transaction_type": transaction_type,
        "from_network": from_network,
        "to_network": to_network,
        "token": token,
        "amount": amount,
        "error": str(error)
    }

    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    if not os.path.exists("./logs/json"):
        os.makedirs("./logs/json")

    if not os.path.exists("./logs/history"):
        os.makedirs("./logs/history")

    filename = "./logs/failed_transactions.html"
    filename_copy = f"./logs/history/failed_{datetime.datetime.now().strftime('%Y_%m_%d')}.html"

    with open("./logs/json/failed_wallets.json", "a+") as failed_file:
        failed_file.seek(0)
        try:
            entries = json.load(failed_file)
        except json.JSONDecodeError:
            entries = []

        if entry not in entries:
            entries.append(entry)
            failed_file.truncate(0)
            json.dump(entries, failed_file, indent=2)

    if datetime.datetime.now().day != current_day:
        current_day = datetime.datetime.now().day

        if os.path.exists(filename):
            shutil.copy2(filename, filename_copy)
            with open(filename, 'w') as file:
                file.write('')

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/failed_template.html')

    with open(filename, 'w') as f:
        f.write(template.render(transactions=entries))


def process_log(private_key, wallet_address, transaction_type, status, from_network,
                to_network, token, amount, error):
    with log_lock:
        try:
            if error is not None:
                log_failed_account(private_key, wallet_address, transaction_type, from_network,
                                   to_network, token, amount, error)
                log_transactions(private_key, wallet_address, transaction_type, status, from_network,
                                 to_network, token, amount)
            else:
                log_transactions(private_key, wallet_address, transaction_type, status, from_network,
                                 to_network, token, amount)
        except Exception as e:
            error_message = f"\n>>> Произошла при записи логов: {str(e)}\n{type(e)}"
            print(error_message)


def paths_spreadsheet(wallets_list):
    paths_folder = "logs/paths"

    if not os.path.exists(paths_folder):
        os.makedirs(paths_folder)

    transactions = []

    for wallet in wallets_list:
        file_path = os.path.join(paths_folder, f"{wallet}.json")
        with open(file_path, "r") as f:
            wallet_transactions = json.load(f)
            for trx in wallet_transactions:
                if trx.get("type") == "WITHDRAWAL":
                    trx["wallet_address"] = wallet
                    transactions.append(trx)

    html_file = "paths.html"
    try:
        with open(os.path.join("logs", html_file), "w") as f:
            soup = BeautifulSoup("<html><body></body></html>", "lxml")

            css = '''
            <style>
                body {
                    font-family: 'Roboto Mono', monospace;
                    background-color: #222;
                    color: #f0f0f0;
                    font-size: 16px;
                }
                td {
                    padding-left: 10px;
                    padding-right: 10px;
                }
                table {
                    border-collapse: collapse;
                    margin-bottom: 10px;
                    font-size: 12px;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #444;
                }
                .exchange_summary {
                    font-weight: bold;
                    background-color: #333;
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 8px;
                    display: inline-block;
                }
            </style>
            '''

            head = soup.new_tag("head")
            soup.html.insert(0, head)
            head.append(BeautifulSoup(css, "lxml"))

            body = soup.find("body")

            exchange_token_totals = defaultdict(lambda: defaultdict(int))

            for trx in transactions:
                exchange = trx.get("exchange", "")
                token = trx.get("to_token", "")[-1]
                amount = trx.get("amount", 0)

                if exchange not in exchange_token_totals:
                    exchange_token_totals[exchange] = {}

                if token not in exchange_token_totals[exchange]:
                    exchange_token_totals[exchange][token] = 0

                exchange_token_totals[exchange][token] += amount

            def token_priority(token):
                if token == "USDC":
                    return 1
                elif token == "USDT":
                    return 2
                else:
                    return 3

            wallet_transactions_grouped = defaultdict(list)
            for trx in transactions:
                wallet_address = trx["wallet_address"]
                wallet_transactions_grouped[wallet_address].append(trx)

            for exchange, token_dict in exchange_token_totals.items():
                if not exchange:
                    continue

                exchange_name = soup.new_tag("strong")
                exchange_name.string = f"{exchange}:"
                body.append(exchange_name)

                row = soup.new_tag("pre")
                row['class'] = "exchange_summary"
                body.append(row)

                tokens = []
                for token, amount in token_dict.items():
                    tokens.append((amount, token))

                sorted_tokens = sorted(tokens, key=lambda x: (token_priority(x[1]), x[1]))
                formatted_tokens = [f"{round(amount, 4)}  {token}" for amount, token in sorted_tokens]

                row.string = "  ".join(formatted_tokens)

                br = soup.new_tag("br")
                body.append(br)

            table = soup.new_tag("table")
            body.append(table)

            tbody = soup.new_tag("tbody")
            table.append(tbody)

            for wallet_address, wallet_transactions in wallet_transactions_grouped.items():
                num_bridge, amount, native = process_wallet_data(wallet_address)
                print(native)
                withdrawal_address = get_withdrawal_address(wallet_address)
                wallet_row = soup.new_tag("tr")
                tbody.append(wallet_row)

                value = amount

                wallet_address_cell = soup.new_tag("td", rowspan=len(wallet_transactions))
                wallet_address_cell.append(f"wallet: {wallet_address}")
                wallet_address_cell.append(soup.new_tag("br"))
                wallet_address_cell.append(f"num bridge: {num_bridge} | value: {value:.2f}")
                wallet_address_cell.append(soup.new_tag("br"))
                wallet_address_cell.append(f"WithAds: {withdrawal_address}")
                wallet_row.append(wallet_address_cell)

                for i, trx in enumerate(wallet_transactions):
                    if i != 0:
                        trx_row = soup.new_tag("tr")
                        tbody.append(trx_row)
                    else:
                        trx_row = wallet_row

                    amount_cell = soup.new_tag("td")
                    amount_cell.string = str(trx.get("amount", ""))
                    trx_row.append(amount_cell)

                    token_cell = soup.new_tag("td")
                    token_cell.string = "/".join(trx.get("to_token", ""))
                    trx_row.append(token_cell)

                    network_cell = soup.new_tag("td")
                    network_cell.string = trx.get("to", "")
                    trx_row.append(network_cell)

                    exchange_cell = soup.new_tag("td")
                    exchange_cell.string = trx.get("exchange", "")
                    trx_row.append(exchange_cell)

                    if i == len(wallet_transactions) - 1:
                        separator_row = soup.new_tag("tr")
                        separator_cell = soup.new_tag("td", colspan=4)
                        separator_cell.string = " "
                        separator_row.append(separator_cell)
                        tbody.append(separator_row)

            f.write(str(soup.prettify()))
    finally:
        save_to_history(os.path.join("logs", html_file))


def save_to_history(src):
    history_folder = "logs/history"
    if not os.path.exists(history_folder):
        os.makedirs(history_folder)

    i = 1
    while True:
        file_name = f"paths{i}.html"
        dest = os.path.join(history_folder, file_name)
        if not os.path.exists(dest):
            shutil.copy2(src, dest)
            break
        i += 1
