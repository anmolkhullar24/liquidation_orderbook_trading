import requests
import time

# Etherscan API key (replace with your own API key from etherscan.io)
etherscan_api_key = "AEEPMEC3492AAH3ZZ11PSRYAQZNBTW6J9Q"

# Function to fetch ERC-20 token transactions for Tether (USDT)
def get_token_transactions():
    try:
        contract_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"  # Tether (USDT) contract address
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_address}&startblock=0&endblock=latest&sort=desc&apikey={etherscan_api_key}"
        response = requests.get(url)
        data = response.json()
        print(url)
        # Check if the data is valid
        if data['status'] == '1':  # Status 1 means success
            return data['result']
        else:
            print(f"Error: {data['message']}")
            return []
    except Exception as e:
        print(f"Exception occurred while fetching token transactions: {e}")
        return []

# Function to track large USDT transactions and print the relevant details
def track_large_usdt_transactions(threshold_usdt=20000):
    # Continuously track token transactions
    while True:
        print("Fetching recent ERC-20 token transactions...")
        transactions = get_token_transactions()

        if not transactions:
            print("No transactions found or failed to fetch transactions.")
            break

        for tx in transactions:
            from_address = tx['from']
            to_address = tx['to']
            value_in_usdt = int(tx['value']) / 10**6  # Convert value from Wei to USDT (6 decimals)

            # Check if the transaction value is large (in USDT)
            if value_in_usdt >= threshold_usdt:
                timestamp = int(tx['timeStamp'])
                print(f"Large USDT Transaction Detected:")
                print(f"From: {from_address} -> To: {to_address}")
                print(f"Amount: {value_in_usdt} USDT")
                print(f"Timestamp: {time.ctime(timestamp)}\n")

        # Wait for 60 seconds before checking again
        print("Waiting for 60 seconds before checking for new transactions...\n")
        time.sleep(60)

# Start tracking large USDT transactions (threshold of 20,000 USDT)
track_large_usdt_transactions(threshold_usdt=20000)
