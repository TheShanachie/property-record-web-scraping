import json, subprocess
      
def submit_scrape_job(api_url: str, kwargs: dict):
    result = subprocess.run(
        [
            'curl',
            '-s', # Silent mode e.g. no progress bar, no external data.
            '-X', 'POST', # Set method to post
            f'{api_url}/scrape', # URL
            "-H", "Content-Type: application/json", # Set content type to JSON data
            "-d", json.dumps(kwargs)
        ],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)


def scrape_job_status(api_url: str, job_id: str):
    result = subprocess.run(
        [
            'curl',
            '-s', # Silent mode e.g. no progress bar, no external data.
            '-X', 'GET', # Set method to post
            f"{api_url}/task/{job_id}/status", # URL
            "-H", "Content-Type: application/json", # Set content type to JSON data
        ],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)


def scrape_job_cancel(api_url: str, job_id: str):
    result = subprocess.run(
        [
            'curl',
            '-s', # Silent mode e.g. no progress bar, no external data.
            '-X', 'POST', # Set method to post
            f"{api_url}/task/{job_id}/cancel", # URL
            "-H", "Content-Type: application/json", # Set content type to JSON data
        ],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)


def get_tasks(api_url: str):
    result = subprocess.run(
        [
            'curl',
            '-s', # Silent mode e.g. no progress bar, no external data.
            '-X', 'GET', # Set method to post
            f"{api_url}/tasks", # URL
            "-H", "Content-Type: application/json", # Set content type to JSON data
        ],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)


def get_health(api_url: str):
    result = subprocess.run(
        [
            'curl',
            '-s', # Silent mode e.g. no progress bar, no external data.
            '-X', 'GET', # Set method to post
            f"{api_url}/health", # URL
            "-H", "Content-Type: application/json", # Set content type to JSON data
        ],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)
    