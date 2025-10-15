import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Path to your local chromedriver
driver_path = r"C:/Users/anmolkh/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

# Create a Service object with the path to the ChromeDriver
service = Service(driver_path)

# Start a new browser session with the Service object
driver = webdriver.Chrome(service=service)

# Open the CoinGlass website
driver.get("https://www.coinglass.com/pro/futures/LiquidationHeatMapNew")

try:
    # Wait until the search input field is visible and clickable
    search_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[class*='MuiAutocomplete-input']"))
    )
    
    # Scroll to the search input (if it's out of view)
    driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
    
    # Type 'xrp' into the search input field
    search_input.send_keys("xrp")

    # Wait for the dropdown to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='listbox']"))
    )

    # Get the coordinates of the dropdown options (the list of options)
    dropdown = driver.find_element(By.CSS_SELECTOR, "ul[role='listbox']")
    location = dropdown.location
    size = dropdown.size

    # Print coordinates and size (optional)
    print(f"Dropdown location: {location}")
    print(f"Dropdown size: {size}")

    # Calculate the position to click a few pixels below the dropdown
    x_position = location['x'] + size['width'] // 2  # Middle of the dropdown
    y_position = location['y'] + size['height'] + 833  # 5 pixels below the dropdown

    # Scroll to the calculated position (optional, but it helps ensure the click happens in view)
    driver.execute_script("window.scrollTo(0, arguments[0]);", y_position)

    # Move the cursor to the calculated position and click
    actions = ActionChains(driver)
    actions.move_by_offset(x_position, y_position).click().perform()

    print("Clicked a few pixels below the dropdown.")

except Exception as e:
    print(f"An error occurred: {e}")

# Keep the browser open to inspect (optional)
input("Press Enter to close the browser...")

# Close the browser
driver.quit()
