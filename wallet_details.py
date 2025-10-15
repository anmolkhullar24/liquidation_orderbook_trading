import requests
import time

# Etherscan API key (replace with your own API key from etherscan.io)
etherscan_api_key = "AEEPMEC3492AAH3ZZ11PSRYAQZNBTW6J9Q"

# Predefined token names for specific contract addresses
predefined_token_names = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "Tether USDT",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USD Coin USDC",
    "0x514910771af9ca656af840dff83e8264ecf986ca": "LINK"
    # Add more predefined token addresses and names here as needed
}

# Function to fetch ERC-20 token transactions for a given wallet address
def get_token_transactions(wallet_address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=latest&sort=desc&apikey={etherscan_api_key}"
        response = requests.get(url)
        data = response.json()

        # Check if the data is valid
        if data['status'] == '1':  # Status 1 means success
            return data['result']
        else:
            print(f"Error: {data['message']}")
            return []
    except Exception as e:
        print(f"Exception occurred while fetching token transactions: {e}")
        return []

# Function to get token name using predefined names
def get_token_name(contract_address):
    # Check if the token is in the predefined list
    if contract_address in predefined_token_names:
        return predefined_token_names[contract_address]
    else:
        # Fallback to the contract address if not found
        return contract_address

# Function to calculate the profit/loss for the wallet based on its trades
def calculate_profit_and_loss(wallet_address):
    transactions = get_token_transactions(wallet_address)
    token_balances = {}  # A dictionary to track the balance of each token
    token_costs = {}  # A dictionary to track the cost of each token
    total_profit_loss = {}  # To track profit and loss for each token

    # Loop through all the transactions and calculate profit/loss
    for tx in transactions:
        from_address = tx['from']
        to_address = tx['to']
        contract_address = tx['contractAddress']  # The contract address of the token
        value_in_token = int(tx['value']) / 10**6  # Assuming 6 decimals for USDT
        timestamp = int(tx['timeStamp'])

        # Fetch the token name using predefined list
        token_name = get_token_name(contract_address)

        # If the wallet receives tokens (buy event)
        if to_address.lower() == wallet_address.lower():
            if contract_address not in token_balances:
                token_balances[contract_address] = 0
            if contract_address not in token_costs:
                token_costs[contract_address] = 0  # Initialize the token cost if not present
            token_balances[contract_address] += value_in_token
            token_costs[contract_address] += value_in_token  # Track the cost of received tokens
            print(f"Received {value_in_token} {token_name} from {contract_address} at {time.ctime(timestamp)}")

        # If the wallet sends tokens (sell event)
        elif from_address.lower() == wallet_address.lower():
            if contract_address not in token_balances:
                token_balances[contract_address] = 0
            if contract_address not in token_costs:
                token_costs[contract_address] = 0
            token_balances[contract_address] -= value_in_token
            # Calculate profit/loss by considering the received tokens' cost
            profit_loss = value_in_token - token_costs[contract_address]
            if contract_address not in total_profit_loss:
                total_profit_loss[contract_address] = 0
            total_profit_loss[contract_address] += profit_loss
            print(f"Sold {value_in_token} {token_name} to {contract_address} at {time.ctime(timestamp)}")

    # Final balances and profitability
    print("\nFinal Token Balances:")
    for token, balance in token_balances.items():
        print(f"{token}: {balance} tokens")

    print("\nProfit/Loss for each token (in tokens):")
    for token, profit_loss in total_profit_loss.items():
        print(f"{token}: {profit_loss} tokens")

# Example wallet address to track
wallet_address = '0x3131f201bc68c615e289fcfdd6ead12e8a94c768'

# Start calculating profit and loss
calculate_profit_and_loss(wallet_address)
