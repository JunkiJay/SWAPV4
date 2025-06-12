from web3 import Web3
import json

# --- 🔧 Конфигурация ---
BASE_RPC_URL = "https://mainnet.base.org"  # или другой Base RPC
PRIVATE_KEY = "0xf2de49d0103d940dd2a6c01f4575089ee6f4640e0e51bd5cc1245236b2839cbe"  # ВАЖНО: Никогда не делись приватным ключом публично
WALLET_ADDRESS = "0x16441A65805eb1cf888dfB21b465DB517fB0570b"

SUPER_DCA_SWAP_ADDRESS = Web3.to_checksum_address("0xaf296044020b9e97326c2e7a4a2223313384900a")
USDC_ADDRESS = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")  # Base USDC (Bridged)

# Загрузите ABI контракта SuperDCASwap
with open("SuperDCASwap.json", "r") as f:
    CONTRACT_ABI = json.load(f)

# --- 📦 Web3 Setup ---
w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
nonce = w3.eth.get_transaction_count(account.address)

swap_contract = w3.eth.contract(address=SUPER_DCA_SWAP_ADDRESS, abi=CONTRACT_ABI)

# --- 🧩 PoolKey: ETH → USDC ---
POOL_KEY = (
    Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),  # ETH (currency0)
    USDC_ADDRESS,  # USDC (currency1)
    3000,          # fee
    60,            # tickSpacing
    "0x" + "00" * 20  # hooks: address(0)
)

# --- 💰 Параметры ---
amount_in_wei = w3.to_wei(0.01, "ether")  # 0.1 ETH
min_amount_out = 0
zero_for_one = True

# --- 🧾 Построение транзакции ---
tx = swap_contract.functions.swapExactInputSingle(
    POOL_KEY,
    zero_for_one,
    amount_in_wei,
    min_amount_out
).build_transaction({
    "from": account.address,
    "value": amount_in_wei,
    "nonce": nonce,
    "gas": 600_000,
    "gasPrice": w3.eth.gas_price,
    "chainId": 8453  # Base Mainnet chainId
})

# --- ✍️ Подпись и отправка ---
signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

print(f"📤 Транзакция отправлена: {tx_hash.hex()}")
print("⏳ Ожидание подтверждения...")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ Swap завершён. Status: {receipt.status}")
print(f"🔗 BaseScan: https://basescan.org/tx/{tx_hash.hex()}")

