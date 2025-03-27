import time
import random
import pickle
import pandas as pd
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  # For hovering and clicking

# Set ChromeDriver path
CHROMEDRIVER_PATH = "C:\\chromedriver-win64\\chromedriver.exe"
COOKIES_PATH = "naukri_cookies.pkl"

# User agents for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def setup_selenium():
    """Set up Selenium with undetected-chromedriver"""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    driver = uc.Chrome(options=options, driver_executable_path=CHROMEDRIVER_PATH)
    return driver

def save_cookies(driver):
    """Save session cookies"""
    pickle.dump(driver.get_cookies(), open(COOKIES_PATH, "wb"))
    print(" Cookies saved successfully.")

def load_cookies(driver):
    """Load saved cookies"""
    try:
        cookies = pickle.load(open(COOKIES_PATH, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        time.sleep(2)
        print(" Cookies loaded successfully.")
    except Exception as e:
        print(f"Could not load cookies: {e}")

def expand_search_bar(driver, wait):
    """Ensure the search bar is expanded before interacting"""
    try:
        search_bar_xpath = "//div[contains(@class, 'nI-gNb-search-bar')]"
        placeholder_xpath = "//input[contains(@class, 'suggestor-input') and @placeholder='Enter keyword / designation / companies']"

        search_bar = wait.until(EC.presence_of_element_located((By.XPATH, search_bar_xpath)))
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, placeholder_xpath)))

        # Ensure the search bar is in view before clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_bar)
        time.sleep(1)

        # Remove any overlay blockers
        driver.execute_script("arguments[0].style.display = 'block';", search_bar)
        driver.execute_script("arguments[0].removeAttribute('tabindex');", search_input)
        time.sleep(1)

        print("Clicking inside search box using JavaScript...")
        driver.execute_script("arguments[0].click();", search_input)
        time.sleep(2)

        # Verify that the search bar expanded
        expanded_xpath = "//div[contains(@class, 'nI-gNb-sb__main--expand')]"
        wait.until(EC.presence_of_element_located((By.XPATH, expanded_xpath)))
        print(" Search bar expanded successfully.")
    
    except Exception as e:
        print(f" Error expanding search bar: {e}")

def extract_job_details(driver):
    """Extract job listings from the results page"""
    jobs = []
    job_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'srp-jobtuple-wrapper')]")
    
    for job in job_elements:
        try:
            title = job.find_element(By.XPATH, ".//a[contains(@class, 'title')]").text
            company = job.find_element(By.XPATH, ".//a[contains(@class, 'comp-name')]").text
            location = job.find_element(By.XPATH, ".//span[contains(@class, 'locWdth')]").text
            experience = job.find_element(By.XPATH, ".//span[contains(@class, 'expwdth')]").text if job.find_elements(By.XPATH, ".//span[contains(@class, 'expwdth')]") else "Not Mentioned"
            salary = job.find_element(By.XPATH, ".//span[contains(@class, 'sal')]/span").text if job.find_elements(By.XPATH, ".//span[contains(@class, 'sal')]/span") else "Not Disclosed"
            job_desc = job.find_element(By.XPATH, ".//span[contains(@class, 'job-desc')]").text
            skills = ", ".join([skill.text for skill in job.find_elements(By.XPATH, ".//ul[@class='tags-gt']/li")])
            job_url = job.find_element(By.XPATH, ".//a[contains(@class, 'title')]").get_attribute("href")
            
            jobs.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Experience": experience,
                "Salary": salary,
                "Description": job_desc,
                "Skills": skills,
                "Job URL": job_url
            })
        except Exception as e:
            print(f"Error extracting job details: {e}")
    
    return jobs

def scrape_naukri_jobs(job_title, location, job_type="Job", max_pages=5):
    """Scrape job listings from Naukri"""
    driver = setup_selenium()
    driver.get("https://www.naukri.com/")
    wait = WebDriverWait(driver, 30)
    time.sleep(5)

    # Load cookies and refresh
    load_cookies(driver)
    driver.refresh()
    time.sleep(5)

    all_jobs = []
    OUTPUT_FILE = "naukri_jobs.csv"
    
    try:
        print("Ensuring search bar is expanded...")
        expand_search_bar(driver, wait)

        # Select Job Type (Job/Internship)
        print("Selecting job type...")
        job_type_dropdown_xpath = "//input[@id='jobType']"
        job_option_xpath = f"//li[@value='a{job_type.lower()}']"

        job_type_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, job_type_dropdown_xpath)))
        driver.execute_script("arguments[0].click();", job_type_dropdown)
        time.sleep(2)

        job_option = wait.until(EC.element_to_be_clickable((By.XPATH, job_option_xpath)))
        driver.execute_script("arguments[0].click();", job_option)
        print(f" Selected job type: {job_type}")

        # Enter job title
        print("Entering job title...")
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'suggestor-input')]")))
        search_box.clear()
        search_box.send_keys(job_title)
        time.sleep(2)
        search_box.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        print(f" Job title entered: {job_title}")

        # Enter Location (Fixed)
        print("Entering location...")
        location_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'suggestor-input') and @placeholder='Enter location']")))
        location_box.clear()
        location_box.send_keys(location)
        time.sleep(2)
        location_box.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        print(f"Location entered: {location}")

        # Click Search Button
        print("Clicking search button...")
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='nI-gNb-sb__icon-wrapper']")))
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(5)

        for page in range(1, max_pages+1):
            print(f"Scraping page {page}...")
            jobs = extract_job_details(driver)
            all_jobs.extend(jobs)
            
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn-secondary') and span[text()='Next']]")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)
            except:
                print("No more pages available.")
                break

        print("Saving data to CSV...")
        df = pd.DataFrame(all_jobs)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f" Data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()


# Get user input
job_title = input("Enter the job title: ")
location = input("Enter the job location: ")
job_type = input("Enter job type (Job/Internship): ")
max_pages = int(input("Enter the number of pages to scrape: "))

# Call the function with user input
scrape_naukri_jobs(job_title, location, job_type, max_pages)

