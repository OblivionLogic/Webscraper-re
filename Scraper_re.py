from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re  # For regex
import json
import time

# Dictionary to store the jobs data
job_data = {
    "jobs": []
}


def fetch_html_with_selenium(url):
    """Fetch HTML content from the given URL using Selenium WebDriver"""
    try:
        # Set up the WebDriver
        driver = webdriver.Chrome()  # You can replace Chrome with other browser drivers
        driver.get(url)

        # Wait for the page to load fully before extracting content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))  # Wait for the body element to be present
        )

        # Optionally scroll to load more content (if it's a lazy-loaded site)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load after scrolling

        # Get the page source after interacting with the page
        html_content = driver.page_source

        # Close the browser after fetching the content
        driver.quit()

        return html_content
    except Exception as e:
        print(f"Error occurred while fetching HTML with Selenium: {e}")
        return None


def extract_jobs_with_regex(html_content, search_pattern):
    """
    Extract job titles matching the given regex pattern from the HTML content.

    Arguments:
        html_content (str): HTML content of the webpage
        search_pattern (str): The regex pattern to match job titles

    Returns:
        list: returns a list of job titles matching the pattern
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all text nodes that match the regex pattern
    job_titles = soup.find_all(string=re.compile(search_pattern, re.IGNORECASE))

    # Extract and clean job titles
    return [job.strip() for job in job_titles]


def click_and_scrape_jobs(driver, url):
    """Click on different job links and scrape job titles"""
    driver.get(url)
    time.sleep(3)  # Give the page some time to load

    # Wait for job links to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.job-link"))  # Adjust the selector based on the site
    )

    job_links = driver.find_elements(By.CSS_SELECTOR, "a.job-link")  # Replace with correct selector for job links

    # List to store all scraped job titles
    all_jobs = []

    for link in job_links:
        try:
            # Click on the job link
            link.click()

            # Wait for the job page to load (adjust the wait condition as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-title"))
                # Adjust the selector for the job title
            )

            # Get the page source after clicking the job link
            job_html = driver.page_source
            job_soup = BeautifulSoup(job_html, 'html.parser')

            # Extract the job title (you can adjust the selector based on the actual HTML structure of job pages)
            job_title = job_soup.find('h1', class_='job-title')  # Adjust class based on the actual site

            if job_title:
                all_jobs.append(job_title.get_text(strip=True))

            # Go back to the previous page (if necessary)
            driver.back()
            time.sleep(2)  # Wait for the page to load again after going back

        except Exception as e:
            print(f"Error occurred while clicking job link: {e}")

    return all_jobs


def save_jobs_to_json(job_list, output_file="jobs.json"):
    """
    Saves the job list to a JSON file

    Arguments:
        job_list (list): A list of job titles
        output_file (str): Name of the output JSON file
    """
    global job_data

    # Populate the dictionary
    job_data["jobs"] = [{"id": idx + 1, "title": job} for idx, job in enumerate(job_list)]

    # Write to JSON file
    with open(output_file, "w") as json_file:
        json.dump(job_data, json_file, indent=4)


if __name__ == "__main__":
    url = "https://www.myjobmag.com/jobs-by-title/software-developer"  # Replace with the actual website
    html_content = fetch_html_with_selenium(url)

    if html_content:
        # Define regex pattern for job titles
        job_search_pattern = r'\b(Software | Engineer | Data | Remote)\b'

        # Extract jobs using the regex function (for the initial page load)
        initial_scraped_jobs = extract_jobs_with_regex(html_content, job_search_pattern)

        # Print initial jobs found
        print("Available jobs from the main page:")
        for index, job in enumerate(initial_scraped_jobs, start=1):
            print(f"{index}. {job}")

        # Setup Selenium WebDriver to click and scrape additional jobs
        driver = webdriver.Chrome()  # Use ChromeDriver or any other WebDriver
        all_jobs = click_and_scrape_jobs(driver, url)

        # Combine both initial and clicked jobs
        total_jobs = initial_scraped_jobs + all_jobs
        print(f"\nTotal available jobs after scraping: {len(total_jobs)}")

        # Save all scraped jobs to JSON
        save_jobs_to_json(total_jobs)
        print("Jobs have been saved to 'jobs.json'.")
