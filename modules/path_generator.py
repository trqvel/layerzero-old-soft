import os
import sys

# Получение абсолютного пути к файлу config.py
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, '..', 'config.py')
config_path = os.path.normpath(config_path)

# Добавление директории файла config.py в путь поиска модулей Python
sys.path.append(os.path.dirname(config_path))

# Импорт переменных из файла config.py
from config import *
from modules.get_requests import *


def stargate_paths(num_paths):
    token_mapping = {
        "BSC": ["USDT"],
        "Polygon": ["USDC", "USDT"],
        "Avalanche": ["USDC", "USDT"],
        "Fantom": ["USDC"],
        "Arbitrum": ["USDC"],
        "Optimism": ["USDC", "USDT"]
    }

    path = []
    current_required_networks = required_networks.copy()
    for i in range(num_paths):
        start, end = None, None
        while True:
            start = random.choice(available_networks)
            end = random.choice(available_networks)
            if start == end:
                continue
            if i == 0:
                if start not in not_first and end not in not_last:
                    break
            elif i == num_paths - 1:
                if start == path[-1]["to"] and end not in not_last:
                    break
            else:
                if start == path[-1]["to"]:
                    break

        if current_required_networks:
            end = current_required_networks.pop(0)
            if start == end:
                if current_required_networks:
                    end = current_required_networks.pop(0)
                else:
                    while start == end:
                        end = random.choice(available_networks)

        if i == 0:
            from_token = random.choice(token_mapping[start])
        else:
            from_token = path[-1]["to_token"][0]

        to_token = random.choice(token_mapping[end])

        if from_token == to_token:
            to_token = random.choice(token_mapping[end])

        path.append({
            "from": start,
            "token": [from_token],
            "to": end,
            "to_token": [to_token],
            "type": "Bridge",
            "project": "Stargate"
        })

    return path


def insert_core(paths):
    bsc_indices = [(i, 'from') for i, path in enumerate(paths) if path['from'] == 'BSC']
    bsc_indices += [(i, 'to') for i, path in enumerate(paths) if path['to'] == 'BSC']
    random.shuffle(bsc_indices)

    if len(bsc_indices) >= 1:
        index, key = bsc_indices[0]
        bsc_token = None
        if key == 'from':
            bsc_token = paths[index]['token'][0]
        elif key == 'to':
            bsc_token = paths[index]['to_token'][0]

        if use_core:
            num_core_bridges = random.randint(num_core_txn[0], num_core_txn[1])
            for _ in range(num_core_bridges):
                core_bridge = {'from': 'BSC', 'token': [bsc_token], 'to': 'Core', 'to_token': ['USDT'],
                               'type': 'Bridge', 'project': 'Core'}
                core_return_bridge = {'from': 'Core', 'token': ['USDT'], 'to': 'BSC', 'to_token': [bsc_token],
                                      'type': 'Bridge', 'project': 'Core'}

                if key == 'from':
                    paths.insert(index, core_bridge)
                    paths.insert(index + 1, core_return_bridge)
                elif key == 'to':
                    paths.insert(index + 1, core_bridge)
                    paths.insert(index + 2, core_return_bridge)

                index += 2
    return paths


def insert_harmony(paths):
    bsc_indices = [i for i, path in enumerate(paths) if path['from'] == 'BSC']
    random.shuffle(bsc_indices)

    if len(bsc_indices) >= 1:
        index = bsc_indices[0]
        bsc_token = paths[index]['token'][0]

        if use_harmony:
            harmony_bridge = {'from': 'BSC',
                              'token': [bsc_token],
                              'to': 'Harmony',
                              'to_token': ['USDT'],
                              'type': 'Bridge',
                              'project': 'Harmony',
                              'amount': round(random.uniform(amount_to_harmony[0], amount_to_harmony[1]), 3)
                              }
            paths.insert(index, harmony_bridge)

    return paths


def insert_btcb_transactions(paths, txns_count):
    txns_count += 1
    enable_networks = required_networks_btcb.copy()

    if not use_btcb or txns_count < 2:
        return paths

    # Check for any existing Avalanche path to insert BTCb paths around it
    avalanche_indices = [(i, 'from') for i, path in enumerate(paths) if path['from'] == 'Avalanche']
    avalanche_indices += [(i, 'to') for i, path in enumerate(paths) if path['to'] == 'Avalanche']

    if not avalanche_indices:
        return paths

    index, key = avalanche_indices[0]
    from_network = None
    token_buy = None
    if key == 'from':
        from_network = paths[index]['from']
    elif key == 'to':
        from_network = paths[index]['to']
    if key == 'from':
        token_buy = paths[index]['token'][0]
    elif key == 'to':
        token_buy = paths[index]['to_token'][0]

    token_bridge = 'BTCb'

    # Buy BTCb
    buy_btcb = {'from': from_network,
                'token': [token_buy],
                'to': '',
                'to_token': [token_bridge],
                'type': 'Buy',
                'project': 'BTCb',
                'amount': round(random.uniform(buy_btcb_amount[0], buy_btcb_amount[1]), 3)}

    paths.insert(index, buy_btcb)

    for i in range(txns_count - 2):
        to_network = from_network
        while to_network == from_network:  # Ensure we don't select the same network twice in a row
            to_network = random.choice(enable_networks)

        # Add a bridge from the current network to the next one
        btcb_bridge = {'from': from_network,
                       'token': [token_bridge],
                       'to': to_network,
                       'to_token': [token_bridge],
                       'type': 'Bridge',
                       'project': 'BTCb'}

        paths.insert(index + i + 1, btcb_bridge)
        from_network = to_network

    # Add a bridge from the last network to Avalanche
    avalanche_bridge = {'from': from_network,
                        'token': [token_bridge],
                        'to': 'Avalanche',
                        'to_token': [token_bridge],
                        'type': 'Bridge',
                        'project': 'BTCb'}

    paths.insert(index + txns_count - 1, avalanche_bridge)

    # Sell BTCb
    sell_btcb = {'from': 'Avalanche',
                 'token': [token_bridge],
                 'to': '',
                 'to_token': [token_buy],
                 'type': 'Sell',
                 'project': 'BTCb',
                 'amount': round(random.uniform(buy_btcb_amount[0], buy_btcb_amount[1]), 3)}

    paths.insert(index + txns_count, sell_btcb)

    return paths


def insert_staking(paths):
    from_networks = ["Avalanche"]

    if not stake_STG:
        return paths

    available_from_networks = [network for network in from_networks if network in available_networks]

    if not available_from_networks:
        return paths

    selected_network = random.choice(available_from_networks)

    # Выбираем только пути с заданным типом и проектом
    network_indices = [(i, 'from') for i, path in enumerate(paths) if
                       path['from'] == selected_network and path['type'] == 'Bridge' and path['project'] == 'Stargate']
    network_indices += [(i, 'to') for i, path in enumerate(paths) if
                        path['to'] == selected_network and path['type'] == 'Bridge' and path['project'] == 'Stargate']

    if not network_indices:
        return paths

    index, key = random.choice(network_indices)
    token = None
    if key == 'from':
        token = paths[index]['token'][0]
    elif key == 'to':
        token = paths[index]['to_token'][0]

    buy_stg = {'from': selected_network,
               'token': [token],
               'to': '',
               'to_token': ['STG'],
               'type': 'Buy',
               'project': 'Stg_stake',
               'amount': round(random.uniform(buy_stg_amount[0], buy_stg_amount[1]), 3)}

    staking_bridge = {'from': selected_network,
                      'token': ['STG'],
                      'to': '',
                      'to_token': ['STG'],
                      'type': 'Staking',
                      'project': 'Stg_stake'}

    if key == 'from':
        paths.insert(index, buy_stg)
        paths.insert(index + 1, staking_bridge)
    elif key == 'to':
        paths.insert(index + 1, buy_stg)
        paths.insert(index + 2, staking_bridge)

    return paths


def insert_testnet(paths):
    from_networks = ["Arbitrum"]
    acceptable_tokens = ["USDC", "USDT"]

    if not use_testnet:
        return paths

    available_from_networks = [network for network in from_networks if network in available_networks]

    if not available_from_networks:
        return paths

    selected_network = "Arbitrum"
    network_indices = [(i, 'from') for i, path in enumerate(paths) if
                       path['from'] == selected_network and path['token'][0] in acceptable_tokens]
    network_indices += [(i, 'to') for i, path in enumerate(paths) if
                        path['to'] == selected_network and path['to_token'][0] in acceptable_tokens]

    if not network_indices:
        return paths

    index, key = random.choice(network_indices)
    token = None
    if key == 'from':
        token = paths[index]['token'][0]
    elif key == 'to':
        token = paths[index]['to_token'][0]

    bridge_arbitrum = {'from': selected_network,
                       'token': [token],
                       'to': '',
                       'to_token': ['ETH'],
                       'type': 'Bridge',
                       'project': 'Testnet',
                       'amount': round(random.uniform(amount_to_testnet[0], amount_to_testnet[1]), 5)}

    if key == 'from':
        paths.insert(index, bridge_arbitrum)
    elif key == 'to':
        paths.insert(index + 1, bridge_arbitrum)

    return paths


def insert_aptos(paths):
    from_networks = ["Polygon", "BSC"]
    acceptable_tokens = ["USDC", "USDT"]

    if not use_aptos:
        return paths

    available_from_networks = [network for network in from_networks if network in available_networks]

    if not available_from_networks:
        return paths

    selected_network = random.choice(available_from_networks)
    network_indices = [(i, 'from') for i, path in enumerate(paths) if
                       path['from'] == selected_network and path['token'][0] in acceptable_tokens]
    network_indices += [(i, 'to') for i, path in enumerate(paths) if
                        path['to'] == selected_network and path['to_token'][0] in acceptable_tokens]

    if not network_indices:
        return paths

    index, key = random.choice(network_indices)
    token = None
    if key == 'from':
        token = paths[index]['token'][0]
    elif key == 'to':
        token = paths[index]['to_token'][0]

    send_aptos = {'from': selected_network,
                  'token': [token],
                  'to': '',
                  'to_token': [token],
                  'type': 'Bridge',
                  'project': 'Aptos',
                  'amount': round(random.uniform(amount_to_aptos[0], amount_to_aptos[1]), 3)}

    if key == 'from':
        paths.insert(index, send_aptos)
    elif key == 'to':
        paths.insert(index + 1, send_aptos)

    return paths


def process_data(data):
    total_costs = {}
    for record in data:
        if record['type'] in ['Bridge', 'Staking']:
            from_chain = record['from']
            to_chain = record['to']
            project = record['project']
            cost = 0

            if from_chain not in total_costs:
                total_costs[from_chain] = 0

            cost += get_value_approve(from_chain)
            cost += get_current_gas_price(from_chain)

            if project == 'Stargate':
                cost += get_value_stg(from_chain, to_chain)
            elif from_chain == 'Core' and project == 'Core':
                cost += get_value_out_core(from_chain)
            elif from_chain == 'BSC' and project == 'Core':
                cost += get_value_in_core(from_chain)
            elif project == 'Harmony':
                cost += get_value_harmony(from_chain)
            elif project == 'Staking':
                cost += get_value_approve(from_chain)
            elif project == 'Aptos':
                cost += get_value_aptos(from_chain)
            elif project == 'Testnet':
                cost += get_value_testnet(from_chain)

            cost += chains_fee[from_chain]
            total_costs[from_chain] += cost

    total_costs = {k: v / (10 ** 18) for k, v in total_costs.items()}

    return total_costs


def insert_withdrawal(paths):
    withdrawal_networks = []
    gas_costs = process_data(paths)
    for network in data_blockchains.keys():
        project_count = {}
        for i, path in enumerate(paths):
            if path['from'] == network:
                project = path['project']
                if project in project_count:
                    project_count[project] += 1
                else:
                    project_count[project] = 1

        for i, path in enumerate(paths):
            if path['from'] == network:
                booster_range = boosters.get(network, [1.1, 1.2])
                booster = random.uniform(booster_range[0], booster_range[1])
                withdrawal_bridge = {
                    'from': '',
                    'token': [''],
                    'to': network,
                    'to_token': [data_blockchains[network]['native']],
                    'type': 'WITHDRAWAL',
                    'project': 'native',
                    'count': project_count,
                    'exchange': random.choice(list_withdrawal_rules.get((network, data_blockchains[network]['native']),
                                                                        ['default_exchange'])),
                    'amount': float(smart_round(Decimal(gas_costs[network]) * Decimal(booster)))
                }
                paths.insert(i, withdrawal_bridge)
                withdrawal_networks.append(network)
                break

    last_bridge = next((path for path in reversed(paths) if path['type'] == 'Bridge' and path['project'] == 'Stargate'),
                       None)
    if last_bridge and last_bridge['to'] not in withdrawal_networks:
        amount_list = {
            "BSC": 0.0042,
            "Fantom": 0.9,
            "Avalanche": 0.075,
            "Arbitrum": 0.00053,
            "Polygon": 1.5
        }
        network = last_bridge['to']
        booster_range = boosters.get(network, [1.1, 1.2])
        booster = random.uniform(booster_range[0], booster_range[1])
        withdrawal_bridge = {
            'from': '',
            'token': [''],
            'to': network,
            'to_token': [data_blockchains[network]['native']],
            'type': 'WITHDRAWAL',
            'project': 'native',
            'count': 1,
            'exchange': random.choice(
                list_withdrawal_rules.get((network, data_blockchains[network]['native']), ['default_exchange'])),
            'amount': float(smart_round(Decimal(amount_list[network]) * Decimal(booster)))
        }
        paths.append(withdrawal_bridge)  # добавляем вывод в конец списка

    return paths


def insert_start_end(paths):
    start_project = 'Stargate'
    start_index = None
    end_index = None

    for i, path in enumerate(paths):
        if path['project'] == start_project:
            if start_index is None:
                start_index = i
            end_index = i

    start_path = paths[start_index]
    end_path = paths[end_index]

    if start_path['from'] in not_first:
        raise ValueError(
            "\n >>> Не удалось вставить правильный путь - неподходящий начальный элемент. Проверьте правильность настройки путей")
    if end_path['to'] in not_last:
        raise ValueError(
            "\n >>> Не удалось вставить правильный путь - неподходящий конечный элемент. Проверьте правильность настройки путей")

    start_bridge = {
        'from': '',
        'token': [''],
        'to': start_path['from'],
        'to_token': start_path['token'],
        'type': 'WITHDRAWAL',
        'project': 'amount in',
        'exchange': random.choice(list_withdrawal_rules.get((start_path['from'], start_path['token'][0]), None)),
        'amount': round(random.uniform(main_amount[0], main_amount[1]), 2)
    }

    end_bridge = {
        'from': '',
        'token': [''],
        'to': end_path['to'],
        'to_token': end_path['to_token'],
        'type': 'WITHDRAWAL',
        'project': 'amount out',
        'amount': 0
    }

    paths.insert(0, start_bridge)
    paths.append(end_bridge)

    return paths


def format_output(paths):
    output = []
    for path in paths:
        print(path)
        if path['type'] == 'WITHDRAWAL':
            if path['project'] == 'amount in' or path['project'] == 'amount out':
                output.append(
                    f"[{path['type']}][{path['project']}] {path['amount']} {path['to_token'][0]} {path['to']}")
            elif path['project'] == 'native':
                output.append(
                    f"[{path['type']}][{path['project']}] {path['to']} {path['amount']} {path['to_token'][0]}")
            else:
                output.append(
                    f"[{path['type']}][{path['project']} {path['count'][path['project']]}] {path['to']} {path['to_token'][0]} ({path['project']}: {path['count'][path['project']]})")
        elif path['type'] == 'Staking':
            output.append(f"[{path['type']}] {path['from']} {path['token'][0]}")
        elif path['type'] == 'Buy':
            output.append(
                f"[{path['type']}] {path['from']} {path['amount']} {path['to_token'][0]} for {path['token'][0]}")
        elif path['type'] == 'Sell':
            output.append(
                f"[{path['type']}] {path['from']} {path['amount']} {path['to_token'][0]} for {path['token'][0]}")
        else:
            output.append(
                f"[{path['project']}] {path['from']} {path['token'][0]} -> {path['to']} {path['to_token'][0]}")

    return output

def insert_defi():

    path = []
    path.append({
            "from": "",
            "token": [""],
            "to": "Polygon",
            "to_token": ["USDC"],
            "type": "WITHDRAWAL",
            "project": "amount in",
            "exchange": "okx",
            "amount": round(random.uniform(amount_to_defi_usdc[0],amount_to_defi_usdc[1]),3)
        })
     
    
    path.append({
            "from": "",
            "token": [""],
            "to": "Polygon",
            "to_token": ["MATIC"],
            "type": "WITHDRAWAL",
            "project": "native",
            "count": 1, 
            "exchange": "okx", 
            "amount": round(random.uniform(amount_to_defi_matic[0],amount_to_defi_matic[1]),3)
        })
    
    return path

def generate():
    if (use_defi):
        paths = insert_defi()
    else:
        num_txn = random.randint(num_stargate_txns[0], num_stargate_txns[1])
        num_txn_btcb = random.randint(num_btcb_txns[0], num_btcb_txns[1])
        paths = stargate_paths(num_txn)
        paths = insert_core(paths)
        paths = insert_harmony(paths)
        paths = insert_btcb_transactions(paths, num_txn_btcb)
        paths = insert_staking(paths)
        paths = insert_testnet(paths)
        paths = insert_aptos(paths)
        paths = insert_withdrawal(paths)
        paths = insert_start_end(paths)
    
    return paths


if __name__ == '__main__':
    for i in range(1):  # создаем цикл для 10 итераций
        print("--------- {} путь ------".format(i + 1))  # печатаем номер пути
        for path in format_output(generate()):  # для каждого пути, сгенерированного функцией generate()
            print(path)  # печатаем путь
