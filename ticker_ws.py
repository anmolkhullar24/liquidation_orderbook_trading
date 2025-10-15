import websocket
import json
import pandas as pd
from datetime import datetime

# WebSocket URL for ticker stream
ticker_url = "wss://fstream.binance.com/ws/btcusdt@ticker"

# Global variables
current_price = None
price_history_file = "btc_price_history.csv"  # File to store price history
current_price_file = "btc_current_price.csv"  # File to store the latest price

# WebSocket ticker message handler
def on_ticker_message(ws, message):
    global current_price
    data = json.loads(message)
    current_price = data.get("c")  # Last price

    # Get current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print the current price and timestamp
    print(f"Current Price: {current_price} at {timestamp}")

    # Save data to CSV files
    save_to_history_csv(timestamp, current_price)
    save_current_price_csv(timestamp, current_price)

# Save data to the price history CSV
def save_to_history_csv(timestamp, price):
    # Prepare the data
    new_data = {'Datetime': [timestamp], 'Price': [price]}
    df_new = pd.DataFrame(new_data)

    # Check if the CSV file exists
    try:
        df_existing = pd.read_csv(price_history_file)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    except FileNotFoundError:
        df_updated = df_new  # If file does not exist, start fresh

    # Write the updated DataFrame to the history CSV file
    df_updated.to_csv(price_history_file, index=False)

# Save the current price to a separate CSV file
def save_current_price_csv(timestamp, price):
    # Prepare the data
    current_data = {'Datetime': [timestamp], 'Price': [price]}
    df_current = pd.DataFrame(current_data)

    # Overwrite the file with the latest price
    df_current.to_csv(current_price_file, index=False)

# Error and close handlers
def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

# Start WebSocket connection
def start_websockets():
    ticker_ws = websocket.WebSocketApp(ticker_url, 
                                       on_message=on_ticker_message, 
                                       on_error=on_error, 
                                       on_close=on_close)
    ticker_ws.run_forever()

# Start the WebSocket connection
start_websockets()
