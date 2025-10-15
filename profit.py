from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  # Import the Options class
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time  # Import the time module

# Wallet address to analyze
wallet_address = "0xff82bf5238637b7e5e345888bab9cd99f5ebe331"
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

    # Wait for 10 seconds before proceeding to search for the Total PnL container
    #time.sleep(10)  # Wait for 10 seconds

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

    # Output both PnL values
    print(f"Total PnL from Container 1: {pnl_value_1}")
    print(f"Total PnL from Container 2: {pnl_value_2}")

finally:
    # Do not close the browser, leave it open
    pass
    # driver.quit()  # Make sure this line is commented or removed to keep the browser open
