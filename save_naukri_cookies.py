from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pickle
import time

# ✅ Path to ChromeDriver
CHROMEDRIVER_PATH = "C:\\chromedriver-win64\\chromedriver.exe"

# ✅ Your Chrome Profile Path
CHROME_PROFILE_PATH = "C:\\Users\\shobh\\AppData\\Local\\Google\\Chrome\\User Data"

# ✅ Set Chrome options to use your actual profile
options = Options()
options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")  # Load your Chrome user data
options.add_argument("profile-directory=Default")  # Use the Default profile
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# ✅ Initialize Chrome driver
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# ✅ Open Naukri.com
driver.get("https://www.naukri.com/")

# ✅ Pause for manual login
input("🔹 Log in manually, then press ENTER to save session...")

# ✅ Save cookies for future use
pickle.dump(driver.get_cookies(), open("naukri_cookies.pkl", "wb"))
print("✅ Cookies saved successfully!")

driver.quit()