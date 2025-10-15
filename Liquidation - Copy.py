import websocket
import json
import pandas as pd
from datetime import datetime
import os
import pytz
from playsound import playsound

# WebSocket URL for liquidation order stream
liquidation_url = "wss://fstream.binance.com/stream?streams=solusdt@forceOrder"

# Liquidation order data storage
liquidation_orders = []

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

# Path to the audio file
audio_file = "coin-257878.mp3"  # Change this to your audio file's path

# WebSocket message handler for liquidation orders
def on_liquidation_order_message(ws, message):
    try:
        # Parse incoming message
        data = json.loads(message)["data"]
        
        # Extract event data
        event_time_utc = datetime.utcfromtimestamp(data["E"] / 1000)  # Event time in UTC (milliseconds)
        order = data["o"]
        
        # Convert to IST
        event_time_ist = event_time_utc.replace(tzinfo=pytz.utc).astimezone(IST)

        # Order details
        symbol = order["s"]
        side = order["S"]
        quantity = float(order["q"])
        price = float(order["ap"])
        last_filled_quantity = float(order["l"])  # Limit executed
        filled_quantity = float(order["z"])       # Total filled (market + limit)
        
        # Determine if it was a short or long liquidation
        liquidation_type = "Short Trade" if side == "BUY" else "Long Trade"

        # Calculate market-executed quantity
        market_executed_quantity = filled_quantity - last_filled_quantity

        # Store the liquidation order details
        liquidation_order = {
            "Event Time (IST)": event_time_ist,
            "Liquidation Type": liquidation_type,
            "Price": price,
            "Quantity": quantity,
            "Limit Executed Quantity": last_filled_quantity,
            "Market Executed Quantity": market_executed_quantity
        }

        # Add to the list
        liquidation_orders.append(liquidation_order)

        # Save the current liquidation order
        save_current_liquidation_order(liquidation_order)

        # Print to console
        print(f"{liquidation_type} liquidated at {event_time_ist}.")
        print(f"Price: {price}, Total Quantity: {quantity}")
        print(f"Limit Executed: {last_filled_quantity}, Market Executed: {market_executed_quantity}\n")

        # Play sound notification
        playsound(audio_file)

        # Save data to historical CSV
        save_data_to_history_csv()

    except Exception as e:
        print(f"Error processing liquidation order: {e}")

# Save the current liquidation order to a separate CSV
def save_current_liquidation_order(order):
    df = pd.DataFrame([order])
    df.to_csv("current_liquidation_order.csv", index=False)
    print("Saved current liquidation order to CSV.")

# Save data to the historical CSV
def save_data_to_history_csv():
    global liquidation_orders
    if liquidation_orders:
        df = pd.DataFrame(liquidation_orders)
        df.to_csv("liquidation_orders_history.csv", mode='a', header=not os.path.exists("liquidation_orders_history.csv"), index=False)
        print(f"Saved {len(liquidation_orders)} liquidation orders to history CSV.")
        
        # Clear the list after saving
        liquidation_orders.clear()

# Error and close handlers for WebSocket
def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

# Start the WebSocket connection
def start_websocket():
    ws = websocket.WebSocketApp(liquidation_url,
                                on_message=on_liquidation_order_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    # Start the WebSocket connection
    start_websocket()
