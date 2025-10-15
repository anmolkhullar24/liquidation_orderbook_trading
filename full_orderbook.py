import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# API URL for depth data
depth_url = "https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=1000"

# Function to fetch the full order book snapshot
def fetch_full_order_book():
    try:
        # Fetch data from the Binance API
        response = requests.get(depth_url)
        print(f"API Response Status: {response.status_code}")  # Debug: Check HTTP status
        
        if response.status_code != 200:
            print("Error fetching data from API.")
            return
        
        data = response.json()
        #print(f"Response Data: {data}")  # Debug: Inspect the raw response
        
        # Ensure the response contains bid and ask data
        if "bids" not in data or "asks" not in data:
            print("No bid or ask data found in the response.")
            return

        # Capture the event time
        event_time = datetime.utcnow()
        event_time_ist = event_time + timedelta(hours=5, minutes=30)
        event_time_ist_str = event_time_ist.strftime("%Y-%m-%d %H:%M:%S")

        # Extract bids and asks
        bids = data.get("bids", [])
        asks = data.get("asks", [])

        if not bids and not asks:
            print("Both bids and asks are empty.")
            return

        # Prepare data for saving
        full_order_book_data = []

        for bid in bids:
            price, quantity = bid
            full_order_book_data.append({
                "Datetime": event_time_ist_str,
                "Type": "Bid",
                "Price": price,
                "Quantity": quantity
            })

        for ask in asks:
            price, quantity = ask
            full_order_book_data.append({
                "Datetime": event_time_ist_str,
                "Type": "Ask",
                "Price": price,
                "Quantity": quantity
            })

        # Save to CSV
        save_data_to_csv(full_order_book_data)

    except Exception as e:
        print(f"Error fetching order book: {e}")

# Function to save data to a CSV file
def save_data_to_csv(order_book_data):
    try:
        if order_book_data:
            df = pd.DataFrame(order_book_data)

            # If the CSV file doesn't exist, write the header; otherwise, append without the header
            df.to_csv(
                "order_book_data.csv",
                mode="a",
                header=not os.path.exists("order_book_data.csv"),
                index=False
            )
            print(f"Saved {len(order_book_data)} records to CSV.")
        else:
            print("No data to save.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

# Main loop to fetch and save order book data every second
def main():
    print("Starting order book data fetcher...")
    while True:
        fetch_full_order_book()
        time.sleep(1)  # Fetch data every second

if __name__ == "__main__":
    main()
