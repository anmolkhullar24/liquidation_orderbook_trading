import requests
import time
import csv
import os  # Import os module for file existence check
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def get_pnl_from_wallet(wallet_address):
    url = f"https://gmgn.ai/eth/address/{wallet_address}"

    # Path to the ChromeDriver (update with your correct path)
    driver_path = r"C:/Users/anmolkh/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

    # Set up the Service for ChromeDriver
    service = Service(driver_path)

    # Initialize Chrome Options to open in normal mode
    chrome_options = Options()
    # Ensure the browser runs in normal mode (not headless) and without automation flags
    chrome_options.add_argument("--start-maximized")  # Open the browser maximized
    chrome_options.add_argument("disable-infobars")   # Prevent the 'Chrome is being controlled by automated test software' message
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (in some environments it may be necessary)

    # Initialize WebDriver with Service and Options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open the URL
        driver.get(url)

        # Wait for the "Got it" button to be clickable and click it
        got_it_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "css-147wlxj"))
        )
        got_it_button.click()

        # Wait for the Total PnL container 1 to load after closing the modal using the provided XPath
        pnl_container_1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/main/div[2]/div[1]/div[2]/div[3]/div[1]/div[2]"))
        )

        # Wait for the Total PnL container 2 to load using its XPath
        pnl_container_2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/main/div[2]/div[1]/div[2]/div[3]/div[2]/div[2]"))
        )

        # Extract PnL values from both containers
        pnl_value_1 = pnl_container_1.text
        pnl_value_2 = pnl_container_2.text

        # Handle PnL percentage extraction and check if it's greater than 1%
        if pnl_value_2 and "%" in pnl_value_2:
            # Extract the percentage part and clean up the string
            pnl_percentage_str = pnl_value_2.split('(')[-1].split(')')[0].strip()  # Get the value inside the parentheses
            pnl_percentage_str = pnl_percentage_str.replace('%', '').replace('$', '').replace('+', '').strip()

            try:
                pnl_percentage = float(pnl_percentage_str)
                # Check if the PnL value from Container 2 is greater than 1%
                if pnl_percentage > 1:
                    print(f"Wallet Address {wallet_address} has PnL greater than 1%")

                    # Append wallet address and PnL data to CSV immediately if condition is met
                    with open('wallet_pnl_data.csv', mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([wallet_address, pnl_percentage])

            except ValueError:
                print(f"Error converting PnL percentage: {pnl_percentage_str}")

    finally:
        try:
            driver.quit()  # Ensure this is called to terminate the WebDriver
        except Exception as e:
            print(f"Error terminating the WebDriver: {e}")

def main():
    # Fetch the latest block from Etherscan API
    latest_block = get_latest_block(API_KEY)
    if latest_block:
        # Get block transactions
        transactions = get_block_transactions(latest_block, API_KEY)

        # Set to store unique wallet addresses (both from and to)
        wallet_addresses = set()

        # Loop through the transactions and collect wallet addresses
        for tx in transactions:
            from_wallet = tx['from']
            to_wallet = tx.get('to', 'None')  # Handle cases where 'to' might be None
            wallet_addresses.add(from_wallet)
            wallet_addresses.add(to_wallet)

        # For each unique wallet address found, check the PnL
        for wallet_address in wallet_addresses:
            get_pnl_from_wallet(wallet_address)

if __name__ == "__main__":
    # Check if the file exists before writing the header
    file_exists = os.path.exists('wallet_pnl_data.csv')
    if not file_exists:
        # If the file does not exist, write the header
        with open('wallet_pnl_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Wallet Address', 'PnL Percentage'])

    main()
