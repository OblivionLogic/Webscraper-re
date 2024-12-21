import requests
from bs4 import BeautifulSoup
import re  # For regex
import json

# Dictionary to store the jobs data
job_data = {
    "jobs": []
}

def fetch_html(url):
    """Fetch HTML content from the given url"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise response for bad error
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

def extract_jobs_with_regex(html_content, search_pattern):
    """
    Extract job titles matching the given regex pattern from the HTML content.
        
    Arguments:
        html_content (str): HTML coontent of the webpage
        search_pattern (str): The regex pattern to match job titles
            
    Returns:
        list: returns a list of job titles matching the pattern
            
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all text nodes that match the regex pattern
    job_titles = soup.find_all(string=re.compile(search_pattern, re.IGNORECASE))

    # Extract and clean job titles
    return [job.strip() for job in job_titles]

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

    # This block is to ensure parts of this code is executed only when the script is run directly , not when its imported as a module in another script
if __name__ == "__main__":
    url = "https://www.myjobmag.com/jobs-by-title/software-developer"  # Replace with the actual website
    html_content = fetch_html(url)

    if html_content:
        # Define regex pattern for  job titles
        job_search_pattern = r'\b(Software | Engineer | Data | Remote)\b'

        # Extract jobs using the regex function
        scraped_jobs = extract_jobs_with_regex(html_content, job_search_pattern)

        print("Available jobs:")
        for index, job in enumerate(scraped_jobs, start=1):
            print(f"{index}. {job}")

        # Save to JSON
        save_jobs_to_json(scraped_jobs)
        print("Jobs have been saved to 'jobs.json'.")