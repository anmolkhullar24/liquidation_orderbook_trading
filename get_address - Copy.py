import requests
import time

API_KEY = "AEEPMEC3492AAH3ZZ11PSRYAQZNBTW6J9Q"

def get_latest_block(api_key):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "proxy",
        "action": "eth_blockNumber",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            return int(data["result"], 16)  # Convert hex to int
    print("Error fetching block number")
    return None

def get_block_transactions(block_number, api_key):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "proxy",
        "action": "eth_getBlockByNumber",
        "tag": hex(block_number),
        "boolean": "true",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "result" in data and data["result"]:
            return data["result"]["transactions"]
    print("Error fetching block transactions")
    return []

def main():
    latest_block = get_latest_block(API_KEY)
    if latest_block:
        print(f"Latest Block: {latest_block}")
        transactions = get_block_transactions(latest_block, API_KEY)
        print(f"Transactions in Block {latest_block}:")
        for tx in transactions:
            print(f"Hash: {tx['hash']}, From: {tx['from']}, To: {tx.get('to')}, Value: {int(tx['value'], 16)} Wei")

if __name__ == "__main__":
    main()
