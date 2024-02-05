## Instagram Scraper

### Overview
This Python script is designed to scrape Instagram data, including usernames and bios, based on a specified search subject. The script utilizes the Selenium library to automate interactions with the Instagram website.

### Prerequisites
- Python (3.x recommended)
- Selenium library (`pip install selenium`)
- Chrome browser
- ChromeDriver (Ensure it's in your system PATH or specify the path in the script)

### Usage

1. **Configuration**
    - Create a `config.yml` file with your Instagram username, password, subject to search, and maximum executions per day.
    ```yaml
    username: your_instagram_username
    password: your_instagram_password
    subject_to_search: your_subject_here
    MAX_EXECUTIONS_PER_DAY: 5
    ```

2. **XPath Configuration**
    - Create an `xpath_config.yml` file with the XPaths for search input, search input box, and account elements.
    ```yaml
    search_input: "//your/search/input/xpath"
    search_input_box: "//your/search/input/box/xpath"
    account_elements: "//your/account/elements/xpath"
    bio_div1: "//your/bio/div1/xpath"
    bio_div2: "//your/bio/div2/xpath"
    bio_div3: "//your/bio/div3/xpath"
    bio_div4: "//your/bio/div4/xpath"
    ```

3. **Execution**
    - Run the script using `python script_name.py`.

### Notes
- The script logs events in the `instagram_scraper.log` file.
- Ensure you comply with Instagram's terms of service and use the script responsibly to avoid any issues.

### Warning
Executing the script multiple times in a day might lead to the detection of the crawler and activation of two-factor authentication. Exercise caution and adhere to execution limits.

## Linktree Email Extractor

### Overview
This Python script extracts Linktree links from Instagram bios saved in a CSV file (`mental health.csv`). It then visits each Linktree profile and extracts email addresses.

### Usage

1. **Execution**
    - Run the script using `python script_name.py`.

### Notes
- The script uses Selenium for web scraping, so ensure you have the necessary dependencies installed.
- Email addresses extracted are saved in a new CSV file (`linkree.csv`) along with the corresponding Linktree links.

### Warning
Executing the script on a large scale may lead to IP blocking or other restrictions. Use responsibly and consider rate limiting to avoid issues.

**Disclaimer**: Use these scripts responsibly and in compliance with the terms of service of the respective platforms. The authors are not responsible for any misuse or violation of terms.
