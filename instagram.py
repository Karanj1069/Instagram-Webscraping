#!/usr/bin/env python
# coding: utf-8

# In[6]:


import time
import os
import re
import csv
import yaml
import logging
import datetime as dt
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

log_path = "instagram_scraper.log"
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log_event(event):
    logging.info(event)
    
def save_credentials(username, password):
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")

def load_credentials():
    if not os.path.exists('credentials.txt'):
        return None
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()
    return None

def read_config():
    try:
        with open('config.yml', 'r') as file:
            config = yaml.safe_load(file)
            username = config.get('username')
            password = config.get('password')
            subject_to_search = config.get('subject_to_search')
            max_executions_per_day = config.get('MAX_EXECUTIONS_PER_DAY', 5)
            return username, password, subject_to_search, max_executions_per_day
    except (FileNotFoundError, yaml.YAMLError):
        print("Error reading 'config.yml'. Make sure the file exists and has valid YAML syntax.")
        return None, None, None, 5  # Use 5 as the default value for MAX_EXECUTIONS_PER_DAY

def read_xpath_config():
    try:
        with open('xpath_config.yml', 'r') as file:
            config = yaml.safe_load(file)
            return config
    except (FileNotFoundError, yaml.YAMLError):
        print("Error reading 'xpath_config.yml'. Make sure the file exists and has valid YAML syntax.")
        return None
    
def read_warning():
    if os.path.exists('warning.txt'):
        with open('warning.txt', 'r') as file:
            date_str, counter_str = file.read().strip().split(',')
            return dt.datetime.strptime(date_str, '%Y-%m-%d').date(), int(counter_str)
    else:
        return dt.date.today(), 0

def write_warning(date, counter):
    with open('warning.txt', 'w') as file:
        file.write(f"{date.strftime('%Y-%m-%d')},{counter}")
        
def check_execution_limit(max_executions_per_day):
    current_date = dt.date.today()
    last_date, counter = read_warning()

    if current_date != last_date:
        # Reset the counter and update the date if it's a new day
        counter = 0
        last_date = current_date

    if counter >= max_executions_per_day:
        print("WARNING: Executing the code multiple times might lead to detection of the crawler and activation of two-factor authentication.")
        return False

    # Increment the counter after a successful execution
    counter += 1
    write_warning(last_date, counter)
    return True
    
def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password

def login(bot, username, password):
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(1)

    try:
        element = bot.find_element(By.XPATH, "//button[text()='Accept']")
        element.click()
    except NoSuchElementException:
        print("[Info] - Instagram did not require accepting cookies this time.")
   
    print("[Info] - Logging in...")
    username_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)
    login_button = WebDriverWait(bot, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    log_event("logged in using credentials")
    time.sleep(10)

def search_for_subject(bot, subject):
    search_element = bot.find_element(By.XPATH, XPATHS['search_input'])
    search_element.click()
    try:
        search_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, XPATHS['search_input_box'])))
        search_input.clear()
        search_input.send_keys(subject)
        log_event(f"crawled the website for {subject}")
        time.sleep(5)
    except TimeoutException:
        print("Element not found. Please map the element in the XPath config file.")
        bot.refresh()
        raise
        
def scrape_instagram(bot, subject):
    try:
        accounts = bot.find_elements(By.XPATH, XPATHS['account_elements'])
        usernames = []
        for i, account in enumerate(accounts):
            try:
                username = account.find_element(By.XPATH,f'/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div/div[2]/div[2]/div/div[{i+1}]/a/div/div/div/div[2]/div/div/div/span')                          
                usernames.append(username.text)
                print(username.text)
                log_event(f"Crawled account: {username.text}")
            
            except NoSuchElementException:
                pass
                
        return usernames
    
    except TimeoutException:
        print("Page content not loaded properly. Refreshing the page...")
        bot.refresh()
        raise
        
def append_bios_to_csv(csv_file_path):
    csv_file_name = "mental health.csv"
    csv_path = os.path.join(current_dir, csv_file_name)
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        header.append("Bio")  # Add a new "Bio" column to the header row
        rows = list(reader)  # Store the contents of the CSV file as a list

    bios_list = []
    for row in rows:
        username = row[0].strip()  # Assuming the username is in the first column
        log_event(f'extracted bio for {username}')
        profile_url = f"https://www.instagram.com/{username}/"
        bot.get(profile_url)
        time.sleep(2)

        bio_elements = []
        bio_div1 = ""
        bio_div2 = ""
        bio_div3 = ""
        bio_div4 = ""
        try:
            bio_div1 = bot.find_element(By.XPATH,XPATHS['bio_div1']).text
            print(bio_div1)
        except Exception as e:
            pass
        try:
            bio_div2 = bot.find_element(By.XPATH,XPATHS['bio_div2']).text
            print(bio_div2)
        except Exception as e:
            pass
        try:
            bio_div3 = bot.find_element(By.XPATH,XPATHS['bio_div3']).text
            print(bio_div3)
        except Exception as e:
            pass
        try:
            bio_div4 = bot.find_element(By.XPATH,XPATHS['bio_div14']).text
            print(bio_div4)
        except Exception as e:
            pass
        print(" ")
        bio_div = bio_div1 + bio_div2 + bio_div3 + bio_div4
        bio_elements.append(bio_div)
        bio_text = ' '.join(bio_elements)
        bios_list.append(bio_text)

    # Update the CSV file with bios in the new "Bio" column
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the updated header row with the "Bio" column
        for i, row in enumerate(rows):
            row.append(bios_list[i])  # Append the bio to the row
            writer.writerow(row)  # Write the updated row to the CSV file
    log_event("username and bio csv saved")
    
def extract_linktr_ee(input_csv, output_csv):
    linktr_ee_list = []
    pattern = r'linktr\.ee\/\w+'

    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Read the header row to get the column index of the bio
        bio_column_index = None
        if 'Bio' in header:
            bio_column_index = header.index('Bio')
        if bio_column_index is None:
            print("Error: Bio column not found in the CSV.")
            return
        for row in reader:
            bio = row[bio_column_index].strip()

            # Find all linktree links in the bio using regex
            links = re.findall(pattern, bio)
            linktr_ee_list.extend(links)

    # Write the extracted linktree links to the output CSV file with the "Links" header
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Links', 'Email'])  # Write the header row
        for linktr_ee_username in linktr_ee_list:
            writer.writerow([linktr_ee_username, ''])
    
def email_extraction():
    input_csv = "linkree.csv"
    rows_to_write = []

    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  
        options = webdriver.ChromeOptions()

        bot = webdriver.Chrome(options=options)
        bot.maximize_window()

        for row in reader:
            link = row[0].strip()
            profile_url = f"https://{link}/"
            print(f"Visiting: {link}")
            try:
                bot.get(profile_url)
                time.sleep(5) 
                html = bot.page_source
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                emails = re.findall(email_pattern, html)

                if emails:
                    unique_emails = set(emails)  # Remove duplicates using set
                    print("Found email IDs:")
                    for email in unique_emails:
                        print(email)
                    row[1] = ", ".join(unique_emails)  # Update the email column in the current row
                else:
                    print("No email IDs found on this page.")

            except InvalidArgumentException as e:
                print(f"Invalid link: {link}")
                continue  # Skip to the next link if there's an error with this one

            print(" ")
            rows_to_write.append(row)  # Append the updated row to the list

    # Write the updated rows back to the CSV file
    with open(input_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the header row
        for row in rows_to_write:
            writer.writerow(row)

    
if __name__ == '__main__':
    # Load configurations and credentials
    username, password, subject_to_search, max_executions_per_day = read_config()
    if not check_execution_limit(max_executions_per_day):
        exit(1)
    xpath_config = read_xpath_config()
    XPATHS = xpath_config

    credentials = load_credentials()
    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    # Set up Chrome options and create the WebDriver instance
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    mobile_emulation = {"userAgent": "Chrome"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(options=options)
    bot.maximize_window()

    # Log in to Instagram
    login(bot, username, password)

    # Search for the subject
    search_for_subject(bot, subject_to_search)

    # Scrape Instagram usernames
    scraped_usernames = scrape_instagram(bot, subject_to_search)

    # Save scraped usernames to CSV
    current_dir = os.getcwd()
    csv_path = os.path.join(current_dir, f"{subject_to_search}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Username'])  # Added 'Bio' column
        for username in zip(scraped_usernames):
            writer.writerow(username)  # Write the username, bio, and links to the CSV file

    log_event(f"saved scraped data in csv")
    append_bios_to_csv(csv_path)
    print(f"Scraped data saved to {csv_path}")

    # Extract linktree links
    extract_linktr_ee("mental health.csv", "linkree.csv")

    # Extract emails from linktree profiles
    email_extraction()

    bot.quit()


# In[12]:


import csv
import re
import time
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException

def extract_linktr_ee(input_csv, output_csv):
    linktr_ee_list = []
    pattern = r'linktr\.ee\/\w+'

    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Read the header row to get the column index of the bio
        bio_column_index = None
        if 'Bio' in header:
            bio_column_index = header.index('Bio')
        if bio_column_index is None:
            print("Error: Bio column not found in the CSV.")
            return
        for row in reader:
            bio = row[bio_column_index].strip()

            # Find all linktree links in the bio using regex
            links = re.findall(pattern, bio)
            linktr_ee_list.extend(links)

    # Write the extracted linktree links to the output CSV file with the "Links" header
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Links', 'Email'])  # Write the header row
        for linktr_ee_username in linktr_ee_list:
            writer.writerow([linktr_ee_username, ''])

def email_extraction():
    input_csv = "linkree.csv"
    rows_to_write = []

    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  
        options = webdriver.ChromeOptions()

        bot = webdriver.Chrome(options=options)
        bot.maximize_window()

        for row in reader:
            link = row[0].strip()
            profile_url = f"https://{link}/"
            print(f"Visiting: {link}")
            try:
                bot.get(profile_url)
                time.sleep(5) 
                html = bot.page_source
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                emails = re.findall(email_pattern, html)

                if emails:
                    unique_emails = set(emails)  # Remove duplicates using set
                    print("Found email IDs:")
                    for email in unique_emails:
                        print(email)
                    row[1] = ", ".join(unique_emails)  # Update the email column in the current row
                else:
                    print("No email IDs found on this page.")

            except InvalidArgumentException as e:
                print(f"Invalid link: {link}")
                continue  # Skip to the next link if there's an error with this one

            print(" ")
            rows_to_write.append(row)  # Append the updated row to the list

    # Write the updated rows back to the CSV file
    with open(input_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the header row
        for row in rows_to_write:
            writer.writerow(row)

