import json
import random
import time
from eth_account import Account
from web3 import Web3
from colorama import init, Fore
import logging

init(autoreset=True)  # Инициализация colorama

# Функция для выбора случайного цвета из списка цветов colorama
def random_color():
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
    return random.choice(colors)

# Вывод с использованием рандомных цветов и символов Unicode
print(random_color() + ' ╔═══╗╔═══╗╔══╗╔╗─╔╗╔════╗╔══╗   ╔══╗ ╔══╗╔══╗')
print(random_color() + ' ║╔══╝║╔═╗║║╔╗║║╚═╝║╚═╗╔═╝║╔╗║   ║╔╗╚╗║╔╗║║╔╗║ ')
print(random_color() + ' ║║╔═╗║╚═╝║║╚╝║║╔╗ ║  ║║  ║╚╝║   ║║╚╗║║╚╝║║║║║')
print(random_color() + ' ║║╚╗║║╔╗╔╝║╔╗║║║╚╗║  ║║  ║╔╗║   ║║ ║║║╔╗║║║║║')
print(random_color() + ' ║╚═╝║║║║║ ║║║║║║ ║║  ║║  ║║║║   ║╚═╝║║║║║║╚╝║')
print(random_color() + ' ╚═══╝╚╝╚╝ ╚╝╚╝╚╝ ╚╝  ╚╝  ╚╝╚╝   ╚═══╝╚╝╚╝╚══╝', '\n')

# Настройка логгирования
logging.basicConfig(filename='transaction_errors.log', level=logging.ERROR)

# Чтение ABI контрактов из файла abi.json
with open('abi.json', 'r') as f:
    abi_data = json.load(f)

mail_contract_abi = abi_data['mail']
blur_contract_abi = abi_data['blur']
rainbow_contract_abi = abi_data['rainbow']

# Получение приватных ключей из файла keys.txt
with open('keys.txt', 'r') as f:
    private_keys = [line.strip() for line in f]

rpc_endpoints = {
    "1": "https://rpc.ankr.com/eth",
    "2": "https://rpc.ankr.com/gnosis",
    "3": "https://rpc.ankr.com/eth"
}

# Выбор сети
network_choice = input("""
Выберите сеть:
- Eth sendMail (1) 
- Gnosis sendMail (2)
- Eth Pro Mode (3)
: """).lower()

# Проверка корректности выбора сети
if network_choice not in rpc_endpoints:
    print("Напиши нормально ебик. Иди подумай над своим поведением")
    exit()

# Используемый RPC
rpc_endpoint = rpc_endpoints[network_choice]
web3 = Web3(Web3.HTTPProvider(rpc_endpoint))



# Адрес контракта
mail_contract_address = "0xa3b31028893c20bEAA882d1508Fe423acA4A70e5"
blur_contract_address = "0x0000000000A39bb272e79075ade125fd351887Ac"
rainbow_contract_address = "0x6BFaD42cFC4EfC96f529D786D643Ff4A8B89FA52"
mail_contract = web3.eth.contract(address=web3.to_checksum_address(mail_contract_address), abi=mail_contract_abi)
blur_contract = web3.eth.contract(address=web3.to_checksum_address(blur_contract_address), abi=blur_contract_abi)
rainbow_contract = web3.eth.contract(address=web3.to_checksum_address(rainbow_contract_address), abi=rainbow_contract_abi)

# Вспомогательные функции

def check_gwei(web3, threshold_gwei):
    current_gwei = web3.eth.gas_price / 10**9  # Приведение к нормальному виду
    if current_gwei > threshold_gwei:
        print(f"{current_gwei:.2f} gwei > {threshold_gwei} gwei.")
        while current_gwei > threshold_gwei:
            time.sleep(10)  # Проверка каждые 10 секунд
            current_gwei = web3.eth.gas_price / 10**9  # Приведение к нормальному виду
            print(f"{current_gwei:.2f} gwei > {threshold_gwei} gwei")
        print(f"{threshold_gwei} gwei. Start working")

# Отправка транзакции с кошелька сети Ethereum
def send_mail(wallet_address, private_key, web3, i):
    destination_mailbox = '0xF8f0929809fe4c73248C27DA0827C98bbE243FCc'
    message = '0x457468657265756de280997320696e7465726f7065726162696c697479206a75737420676f7420736e61726b7920f09faa84'
    destination_chain_id = random.choice(list(chain_ids.keys()))
    
    nonce = web3.eth.get_transaction_count(wallet_address)
    balance = web3.eth.get_balance(wallet_address)
    if balance <= 0:
        logging.error(f"Insufficient balance in wallet {wallet_address}")
        return None

    current_gas_price = web3.eth.gas_price
    gas_price = int(current_gas_price * 1.1)
    payable_amount = web3.to_wei(random.uniform(0, 0), 'ether')
    gas_limit = web3.eth.estimate_gas({
        'from': wallet_address,
        'to': mail_contract_address,
        'value': payable_amount,
        'data': mail_contract.encodeABI(fn_name='sendMail', args=[destination_chain_id, destination_mailbox, message]),
    })

    print(f'Start with wallet [{i}/{len(wallets)}]: {wallet_address}')
    print(f"Send Mail to {chain_ids[destination_chain_id]}")
    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': mail_contract_address,
            'value': payable_amount,
            'data': mail_contract.encodeABI(fn_name='sendMail', args=[destination_chain_id, destination_mailbox, message]),
            'chainId': 1,  # ID сети ETH
        }

        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f'Transaction sent: {tx_hash.hex()}')

        # Ожидание подтверждения транзакции
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print(Fore.GREEN + f'Transaction {tx_hash.hex()} successfully confirmed')
        else:
            print(Fore.RED + f'Transaction {tx_hash.hex()} failed')
        
        return tx_hash.hex()
    
    except Exception as e:
        logging.error(f'Error occurred for wallet {wallet_address}: {e}')
        logging.exception("Exception occurred", exc_info=True)
        return None
        
# Отправка транзакции с кошелька сети Gnosis
def send_gnosis(wallet_address, private_key, web3, i):
    destination_mailbox = '0xF8f0929809fe4c73248C27DA0827C98bbE243FCc'
    message = '0x457468657265756de280997320696e7465726f7065726162696c697479206a75737420676f7420736e61726b7920f09faa84'
    destination_chain_id = 5
    
    nonce = web3.eth.get_transaction_count(wallet_address)
    balance = web3.eth.get_balance(wallet_address)
    if balance <= 0:
        logging.error(f"Insufficient balance in wallet {wallet_address}")
        return None

    current_gas_price = web3.eth.gas_price
    gas_price = int(current_gas_price * 1.8)
    payable_amount = web3.to_wei(random.uniform(0, 0), 'ether')
    gas_limit = web3.eth.estimate_gas({
        'from': wallet_address,
        'to': mail_contract_address,
        'value': payable_amount,
        'data': mail_contract.encodeABI(fn_name='sendMail', args=[destination_chain_id, destination_mailbox, message]),
    })

    print(f'Start with wallet [{i}/{len(wallets)}]: {wallet_address}')
    print(f"Send Mail to {chain_ids[destination_chain_id]}")
    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': mail_contract_address,
            'value': payable_amount,
            'data': mail_contract.encodeABI(fn_name='sendMail', args=[destination_chain_id, destination_mailbox, message]),
            'chainId': 100,  # ID сети ETH
        }

        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f'Transaction sent: {tx_hash.hex()}')

        # Ожидание подтверждения транзакции
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
                    print(Fore.GREEN + f'Transaction {tx_hash.hex()} successfully confirmed')
        else:
            print(Fore.RED + f'Transaction {tx_hash.hex()} failed')
        
        return tx_hash.hex()
    
    except Exception as e:
        logging.error(f'Error occurred for wallet {wallet_address}: {e}')
        logging.exception("Exception occurred", exc_info=True)
        return None

# Blur Deposit
def blur_deposit(wallet_address, private_key, web3, i):
    nonce = web3.eth.get_transaction_count(wallet_address)
    balance = web3.eth.get_balance(wallet_address)
    if balance <= 0:
        logging.error(f"Insufficient balance in wallet {wallet_address}")
        return None

    current_gas_price = web3.eth.gas_price
    gas_price = int(current_gas_price * 1.1)
    payable_amount = web3.to_wei(random.uniform(0.000001, 0.00002), 'ether') # меняй сумму
    gas_limit = web3.eth.estimate_gas({
        'from': wallet_address,
        'to': blur_contract_address,
        'value': payable_amount,
        'data': blur_contract.encodeABI(fn_name='deposit'),
    })

    print(f'Start with wallet [{i}/{len(wallets)}]: {wallet_address}')
    print(f'Blur deposit {web3.from_wei(payable_amount, "ether")} eth')
    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': blur_contract_address,
            'value': payable_amount,
            'data': blur_contract.encodeABI(fn_name='deposit'),
            'chainId': 1,  # ID сети ETH
        }

        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f'Transaction sent: {tx_hash.hex()}')

        # Ожидание подтверждения транзакции
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print(Fore.GREEN + f'Transaction {tx_hash.hex()} successfully confirmed')
        else:
            print(Fore.RED + f'Transaction {tx_hash.hex()} failed')
        
        return tx_hash.hex()
    
    except Exception as e:
        logging.error(f'Error occurred for wallet {wallet_address}: {e}')
        logging.exception("Exception occurred", exc_info=True)
        return None

# RainbowBrdige
def rainbow_bridge(wallet_address, private_key, web3, i):
    # Удаление префикса "0x" из адреса кошелька
    wallet_address_clean = wallet_address.lower().lstrip("0x")
    nearRecipientAccountId = "aurora:" + wallet_address_clean
    fee = 0
    
    nonce = web3.eth.get_transaction_count(wallet_address)
    balance = web3.eth.get_balance(wallet_address)
    if balance <= 0:
        logging.error(f"Insufficient balance in wallet {wallet_address}")
        return None

    current_gas_price = web3.eth.gas_price
    gas_price = int(current_gas_price * 1.1)
    payable_amount = web3.to_wei(random.uniform(0.000001, 0.00002), 'ether') # меняй сумму
    gas_limit = web3.eth.estimate_gas({
        'from': wallet_address,
        'to': rainbow_contract_address,
        'value': payable_amount,
        'data': rainbow_contract.encodeABI(fn_name='depositToNear', args=[nearRecipientAccountId, fee]),
    })

    print(f'Start with wallet [{i}/{len(wallets)}]: {wallet_address}')
    print(f'Bridge to Aurora {web3.from_wei(payable_amount, "ether")} eth')
    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': rainbow_contract_address,
            'value': payable_amount,
            'data': rainbow_contract.encodeABI(fn_name='depositToNear', args=[nearRecipientAccountId, fee]),
            'chainId': 1,  # ID сети ETH
        }

        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f'Transaction sent: {tx_hash.hex()}')

        # Ожидание подтверждения транзакции
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print(Fore.GREEN + f'Transaction {tx_hash.hex()} successfully confirmed')
        else:
            print(Fore.RED + f'Transaction {tx_hash.hex()} failed')
        
        return tx_hash.hex()
    
    except Exception as e:
        logging.error(f'Error occurred for wallet {wallet_address}: {e}')
        logging.exception("Exception occurred", exc_info=True)
        return None



# Список доступных destination_chain_id и их соответствующие имена
chain_ids = {
    5: "Goerli",
    10: "Optimism",
    42161: "Arbitrum",
    56: "BNB",
    100: "Gnosis",
    137: "Polygon",
    43114: "Avalanche"
}

# Генерация кошельков из приватных ключей
wallets = [Account.from_key(private_key).address for private_key in private_keys]


web3 = Web3(Web3.HTTPProvider(rpc_endpoint))

# Отправка транзакции с каждого кошелька
for i, (wallet_address, private_key) in enumerate(zip(wallets, private_keys), 1):
    # Проверка цены газа перед каждой транзакцией
    if network_choice == "1" or network_choice == "3":
        check_gwei(web3, 24) # gwei настройка

    if network_choice == "1":
        threshold_gwei = 24  # gwei настройка
        check_gwei(web3, threshold_gwei)
        try:
            tx_hash = send_mail(wallet_address, private_key, web3, i)
        except Exception as e:
            print(f"Error: {e}. Skipping to the next action.")
            continue
    elif network_choice == "2":
        try:
            tx_hash = send_gnosis(wallet_address, private_key, web3, i)
        except Exception as e:
            print(f"Error: {e}. Skipping to the next action.")
            continue
    elif network_choice == "3":
        threshold_gwei = 24  # gwei настройка
        modules = ["rainbow_bridge", "blur_deposit"]
        # Случайный выбор модулей из списка
        selected_modules = random.sample(modules, random.randint(1, len(modules)))
        # send_mail в случайное место в списке
        send_mail_index = random.randint(0, len(selected_modules))
        selected_modules.insert(send_mail_index, "send_mail")
        for module_type in selected_modules:
            try:
                if module_type == "send_mail":
                    tx_hash = send_mail(wallet_address, private_key, web3, i)
                elif module_type == "rainbow_bridge":
                    tx_hash = rainbow_bridge(wallet_address, private_key, web3, i)
                elif module_type == "blur_deposit":
                    tx_hash = blur_deposit(wallet_address, private_key, web3, i)
                    random_sleep_duration = random.randint(100, 200) # меняй время
                    print(f'Waiting for {random_sleep_duration} seconds before processing next action...')
                time.sleep(random_sleep_duration)
            except Exception as e:
                print(f"Error: {e}. Skipping to the next action.")
                continue
    else:
        print("Invalid network choice")
        break

    if tx_hash:
        print('')
    else:
        print(f'Skipping wallet {wallet_address} due to error.')

    # Рандомное время задежки между кошельками
    delay_before_next_wallet = random.randint(200, 400) # меняй время
    print(f'Waiting for {delay_before_next_wallet} seconds before processing next wallet...')
    time.sleep(delay_before_next_wallet)

print("Transaction processing completed for all wallets.")
