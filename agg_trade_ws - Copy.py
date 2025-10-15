import websocket
import json
import pandas as pd
from datetime import datetime
import os
import pytz  # Library for timezone handling
from playsound import playsound  # Library for playing sound

# WebSocket URL for aggTrade stream
agg_trade_url = "wss://fstream.binance.com/ws/btcusdt@aggTrade"

# Global variable to store trade data
trade_data = []

# Paths to sound files
buy_sound_file = "money-bag-82960.mp3"  # Replace with your buy sound file path
sell_sound_file = "money-bag-82960.mp3"  # Replace with your sell sound file path

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

# WebSocket aggTrade message handler
def on_agg_trade_message(ws, message):
    try:
        # Parse the incoming WebSocket message
        data = json.loads(message)

        # Extract trade details
        trade_time_utc = datetime.utcfromtimestamp(data["T"] / 1000)  # Trade time in UTC
        trade_time_ist = trade_time_utc.replace(tzinfo=pytz.utc).astimezone(IST)  # Convert to IST

        trade_price = float(data["p"])  # Trade price
        trade_quantity = float(data["q"])  # Trade quantity
        buyer_is_maker = data["m"]  # Market maker flag

        # Determine the trade type (Buy or Sell)
        trade_type = "Market Sell" if buyer_is_maker else "Market Buy"

        # Only process trades with a quantity greater than 15 BTC
        if trade_quantity > 15:
            # Print filtered trade data to console
            print(f"Trade Type: {trade_type}, Trade Time: {trade_time_ist}, Quantity: {trade_quantity}, Price: {trade_price}")

            # Play sound based on trade type
            if trade_type == "Market Buy":
                playsound(buy_sound_file)
            elif trade_type == "Market Sell":
                playsound(sell_sound_file)

            # Append trade to the trade_data list
            trade_data.append({
                "Trade Type": trade_type,
                "Trade Time (IST)": trade_time_ist,
                "Quantity": trade_quantity,
                "Price": trade_price
            })

            # Save data to CSV
            save_data_to_csv()

    except Exception as e:
        print(f"Error: {e}")

# Save data to CSV file
def save_data_to_csv():
    global trade_data
    if trade_data:
        # Convert trade_data to a pandas DataFrame
        df = pd.DataFrame(trade_data)

        # Append to CSV file (create file if it doesn't exist)
        df.to_csv("agg_trade_data.csv", mode='a', header=not os.path.exists("agg_trade_data.csv"), index=False)
        print(f"Saved {len(trade_data)} records to CSV.")

        # Clear the trade_data list after saving
        trade_data.clear()

# WebSocket error handler
def on_error(ws, error):
    print(f"WebSocket Error: {error}")

# WebSocket close handler
def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

# Start WebSocket connection
def start_websockets():
    agg_trade_ws = websocket.WebSocketApp(
        agg_trade_url,
        on_message=on_agg_trade_message,
        on_error=on_error,
        on_close=on_close
    )
    agg_trade_ws.run_forever()

# Start the WebSocket connection
if __name__ == "__main__":
    print("Starting WebSocket connection...")
    start_websockets()
