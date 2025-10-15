import requests
import json
import time
import pandas as pd
import os
from datetime import datetime, timedelta
from playsound import playsound  # Library for playing sound

# File paths
history_file = "open_interest_history.csv"
current_file = "open_interest_current.csv"

# Global variable to store the previous open interest
previous_open_interest = None

# Function to fetch the current open interest for a symbol
def fetch_open_interest(symbol="BTCUSDT"):
    url = "https://fapi.binance.com/fapi/v1/openInterest"
    
    # Prepare the request parameters
    params = {
        "symbol": symbol
    }

    try:
        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            open_interest = float(data.get("openInterest"))
            timestamp = int(data.get("time", time.time() * 1000))

            # Convert timestamp to UTC datetime
            open_interest_time_utc = datetime.utcfromtimestamp(timestamp / 1000)

            # Convert UTC time to IST (UTC + 5:30)
            open_interest_time_ist = open_interest_time_utc + timedelta(hours=5, minutes=30)

            # Format the IST time
            open_interest_time_str = open_interest_time_ist.strftime('%Y-%m-%d %H:%M:%S')

            # Return the open interest and time for storage
            return {
                "Datetime": open_interest_time_str,
                "Open Interest": open_interest
            }
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to play a sound for significant increase
def play_increase_sound():
    try:
        playsound("cashier-quotka-chingquot-sound-effect-129698.mp3")  # Path to your alert sound for increase
    except Exception as e:
        print(f"Error playing increase sound: {e}")

# Function to play a sound for significant decrease
def play_decrease_sound():
    try:
        playsound("money-bag-82960.mp3")  # Path to your alert sound for decrease
    except Exception as e:
        print(f"Error playing decrease sound: {e}")

# Function to save open interest data to CSV files
def save_to_csv(data):
    # Save historical data (with timestamp and open interest)
    try:
        # Load the history CSV file if it exists, otherwise create a new DataFrame
        if os.path.exists(history_file):
            history_df = pd.read_csv(history_file)
        else:
            history_df = pd.DataFrame(columns=["Datetime", "Open Interest"])

        # Convert data to DataFrame and concatenate
        data_df = pd.DataFrame([data])

        # Concatenate the new data with the existing DataFrame
        history_df = pd.concat([history_df, data_df], ignore_index=True)

        # Save the history data back to the CSV file
        history_df.to_csv(history_file, index=False)
        print(f"Saved to history file: {data}")
    except Exception as e:
        print(f"Error saving history data: {e}")

    # Save current data (only timestamp and open interest) - Overwrite the current file
    try:
        # Convert data to DataFrame
        current_df = pd.DataFrame([data])

        # Save only the latest data, overwriting the file
        current_df.to_csv(current_file, index=False)
        print(f"Saved to current file: {data}")
    except Exception as e:
        print(f"Error saving current data: {e}")

# Run the function continuously
def run_continuously(symbol="BTCUSDT", interval=10):
    global previous_open_interest

    try:
        while True:
            data = fetch_open_interest(symbol)
            if data:
                # Determine if OI changed significantly
                current_open_interest = data["Open Interest"]
                if previous_open_interest is not None:
                    difference = current_open_interest - previous_open_interest
                    if abs(difference) > 50:  # Check if the change is greater than 50
                        if difference > 0:
                            print(f"Significant OI Increase: {current_open_interest} (Previous: {previous_open_interest}, Change: {difference})")
                            play_increase_sound()
                        elif difference < 0:
                            print(f"Significant OI Decrease: {current_open_interest} (Previous: {previous_open_interest}, Change: {difference})")
                            play_decrease_sound()

                # Save the data to CSV
                save_to_csv(data)

                # Update previous open interest
                previous_open_interest = current_open_interest

            time.sleep(interval)  # Wait for 'interval' seconds before fetching again

    except KeyboardInterrupt:
        print("\nProcess interrupted. Stopping the script.")

# Start fetching data continuously
if __name__ == "__main__":
    symbol = "BTCUSDT"  # You can change this to any symbol (e.g., ETHUSDT, etc.)
    run_continuously(symbol)
