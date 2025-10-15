import websocket
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import requests

# WebSocket URL for depth stream
depth_url = "wss://fstream.binance.com/ws/btcusdt@depth"

# File paths
current_order_book_file = "current_order_book.csv"
order_book_history_file = "order_book_history.csv"

# Global variable to store the current order book
current_order_book = {"bids": {}, "asks": {}, "timestamp": ""}

# Function to convert UTC to IST
def convert_utc_to_ist(utc_time):
    # Convert UTC to IST (UTC + 5:30)
    return utc_time + timedelta(hours=5, minutes=30)

# Function to fetch the initial full order book snapshot
def fetch_initial_order_book():
    global current_order_book

    url = "https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=1000"
    response = requests.get(url)
    data = response.json()

    # Initialize the current order book with the fetched snapshot
    utc_time = datetime.utcnow()
    ist_time = convert_utc_to_ist(utc_time)
    
    current_order_book = {
        "bids": {float(price): float(quantity) for price, quantity in data.get("bids", [])},
        "asks": {float(price): float(quantity) for price, quantity in data.get("asks", [])},
        "timestamp": ist_time.strftime("%Y-%m-%d %H:%M:%S")  # Add IST timestamp to the initial order book
    }

    # Save the initial snapshot to both CSV files
    save_current_order_book()
    append_to_history_file()


# Function to update the current order book with WebSocket updates
def update_order_book(updates):
    global current_order_book

    # Process bids and asks from the updates
    bids = updates.get("b", [])
    asks = updates.get("a", [])

    # Update bids
    for price, quantity in bids:
        price = float(price)
        quantity = float(quantity)
        if quantity == 0:
            current_order_book["bids"].pop(price, None)  # Remove the price level if quantity is 0
        else:
            current_order_book["bids"][price] = quantity

    # Update asks
    for price, quantity in asks:
        price = float(price)
        quantity = float(quantity)
        if quantity == 0:
            current_order_book["asks"].pop(price, None)  # Remove the price level if quantity is 0
        else:
            current_order_book["asks"][price] = quantity

    # Update timestamp with the latest update time
    utc_time = datetime.utcnow()
    ist_time = convert_utc_to_ist(utc_time)
    current_order_book["timestamp"] = ist_time.strftime("%Y-%m-%d %H:%M:%S")


# Function to save the current order book to a CSV file
def save_current_order_book():
    global current_order_book

    # Capture the current timestamp
    event_time_str = current_order_book["timestamp"]

    # Convert the current order book to DataFrame for bids and asks
    bids_df = pd.DataFrame(
        [{"Price": price, "Quantity": quantity, "Datetime": event_time_str} for price, quantity in current_order_book["bids"].items()]
    ).sort_values(by="Price", ascending=False)

    asks_df = pd.DataFrame(
        [{"Price": price, "Quantity": quantity, "Datetime": event_time_str} for price, quantity in current_order_book["asks"].items()]
    ).sort_values(by="Price", ascending=True)

    # Add a column to distinguish bids and asks
    bids_df["Type"] = "Bid"
    asks_df["Type"] = "Ask"

    # Combine bids and asks
    combined_df = pd.concat([bids_df, asks_df], ignore_index=True)

    # Save to CSV
    combined_df.to_csv(current_order_book_file, index=False)
    print(f"Current order book saved with timestamp {event_time_str}")


# Function to append the entire current order book with timestamp to the history file
def append_to_history_file():
    global current_order_book

    # Get the current timestamp
    event_time_str = current_order_book["timestamp"]

    # Create a DataFrame for the full order book with timestamp
    history_data = []
    for price, quantity in current_order_book["bids"].items():
        history_data.append({"Datetime": event_time_str, "Type": "Bid", "Price": price, "Quantity": quantity})
    for price, quantity in current_order_book["asks"].items():
        history_data.append({"Datetime": event_time_str, "Type": "Ask", "Price": price, "Quantity": quantity})

    # Create a DataFrame for the history data
    history_df = pd.DataFrame(history_data)

    # Append to the history file
    history_df.to_csv(order_book_history_file, mode="a", header=not os.path.exists(order_book_history_file), index=False)
    print(f"Order book history appended with timestamp {event_time_str}")


# WebSocket message handler
def on_depth_message(ws, message):
    try:
        updates = json.loads(message)
        update_order_book(updates)  # Update the current order book with WebSocket updates
        save_current_order_book()  # Save the updated current order book
        append_to_history_file()  # Append the updated order book to the history file
    except Exception as e:
        print(f"Error processing message: {e}")


# WebSocket error and close handlers
def on_error(ws, error):
    print(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")


# Start the WebSocket
def start_websockets():
    # Fetch the initial order book before starting WebSocket
    fetch_initial_order_book()

    # Connect to WebSocket
    ws = websocket.WebSocketApp(
        depth_url,
        on_message=on_depth_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()


if __name__ == "__main__":
    start_websockets()
