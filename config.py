# config

# ====== Общие настройки ======
number_of_threads = 10 # кол-во потоков, приватных ключей с которыми бот будет работать одновременно
main_amount = [7, 8]  # кол-во объема для каждого аккаунта (который будем крутить), в $
buy_btcb_amount = [1, 2]  # сумма покупки $BTC.b, указывается в $
min_boost = [1, 6]  # если выводим с биржи минималку, к ней добавляем рандомный %, в %
delay_threads = [1, 1]  # задержка старта потока, действует только в начале, в секундах
delay_txn = [10, 25]  # задержка между транзакциями, в секундах
delay_approve = [1, 10]
delay_wallets = [1,5]  # задержка между кошельками, в секундах

# ====== Настройки пути ====== 
# available_networks - сети которые мы будем использовать при генерации пути 
available_networks = ["Polygon", "Arbitrum"] 
# required_networks - обязательные сети, через которые мы будем проходить в каждом пути 
required_networks = [] 
 
# not_first - сети, с которых не будут начинаться пути 
not_first = ["Polygon"] 
# not_last - сети, которыми не будут оканчиваться пути 
not_last = []

num_stargate_txns = [3, 4]  # кол-во транзакций для старгейт
# бустеры к выводу нативок в разных сетях
boosters = {
    "BSC": [1.20, 1.30],
    "Fantom": [1.25, 1.30],
    "Avalanche": [1.30, 1.40],
    "Arbitrum": [1.20, 1],
    "Polygon": [1.25, 1.30]
}
# ====== Defi Kingdoms ======
use_defi = False
amount_to_defi_usdc = [1, 2]
amount_to_defi_matic = [3, 4]

# ====== Core Bridge ======
use_core = False  # True - использовать Core, False - отключить
num_core_txn = [3, 4]  # кол-во раз, которое нужно отправить В и ИЗ Core

# ====== Harmony Bridge ======
use_harmony = False  # True - использовать Harmony, False - отключить
amount_to_harmony = [1, 2]  # сумма для отправки в Harmony, указывается в $

# ====== Btc.b Bridge ======
use_btcb = False  # True - купить и отправить BTC.b, False - отключить

required_networks_btcb = ["BSC", "Arbitrum"]
num_btcb_txns = [1, 1]  # кол-во транзакций для BTC.b

# ====== Stake $STG ======
stake_STG = True  # True - купить и застейкать $STG, False - отключить
buy_stg_amount = [1, 1]  # сумма покупки $STG, указывается в $
months_to_lock = [36, 36]  # время лока $STG, указывается в месяцах

# ====== Testnet Bridge ======
use_testnet = False  # True - купить и застейкать $STG, False - отключить
amount_to_testnet = [0.0001, 0.0002]  # сумма бриджа ETH в Goerli, указывается в ETH

# ====== Aptos Bridge ======
use_aptos = False  # True - купить и застейкать $STG, False - отключить
amount_to_aptos = [0.1, 0.3]  # сумма для бриджа в aptos, указывается в $

# ====== DEX settings ====== # choose_dex = ["woofi", "sushi", "inch"]
choose_dex = ["woofi"]

# ====== Вывод обратно на биржу ======
withdrawal_out = True  # нужно ли выводить из конечной сети объем
reserve_balance = [0, 0]  # сумма, которую вы хотите оставить перед выводом на биржу, в $
delay_withdrawal = [10, 10]  # отдельная задержка на вывод с последней сети, в секундах

# ====== БИРЖИ ======
# ====== Схема вывода токенов ======
# укажите с какой биржи какой токен выводить
list_withdrawal_rules = {
    ('Fantom', 'FTM'): ['okx'],
    ('Avalanche', 'AVAX'): ['okx'],
    ('Polygon', 'MATIC'): ['okx'],
    ('Arbitrum', 'ETH'): ['okx'],
    ('BSC', 'BNB'): ['okx'],
    ('Avalanche', 'USDC'): ['okx'],
    ('Avalanche', 'USDT'): ['okx'],
    ('Polygon', 'USDC'): ['okx'],
    ('Polygon', 'USDT'): ['okx'],
    ('Arbitrum', 'USDC'): ['okx'],
    ('Arbitrum', 'USDT'): ['okx'],
    ('BSC', 'USDC'): ['okx'],
    ('BSC', 'USDT'): ['okx'],
    ('Core', 'CORE'): ['okx']
}

# ====== Настройка доступа к биржам ======
# BINANCE
use_binance_proxy = False  # если не используете прокси, переведите в False
binance_proxy = "http://login:password@ip:port"
binance_apikey = "__binance__api_key__"
binance_apisecret = "__binance__api_secret__"

# OKX
use_okx_proxy = True  # если не используете прокси, переведите в False
okx_proxy = ""
okx_apikey = ""
okx_apisecret = ""
okx_passphrase = ""


# MEXC
use_mexc_proxy = False  # если не используете прокси, переведите в False
mexc_proxy = "http://login:password@ip:port"
mexc_apikey = "__mexc__api_key__"
mexc_apisecret = "__mexc__api_secret__"
