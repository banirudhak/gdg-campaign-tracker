import csv
import time
import argparse
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

# Configuration
REQUIRED_BADGES = 10
RATE_LIMIT_DELAY = 1.5  # Seconds between requests to prevent IP blocking
TIMEOUT = 10  # Seconds before a request times out

def is_valid_url(url):
    """Validate that the input is a valid Google Skills Boost URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and "cloudskillsboost.google" in result.netloc
    except ValueError:
        return False

def fetch_badge_count(url):
    """Scrapes the public profile to count the number of badges."""
    if not is_valid_url(url):
        return 0, "Invalid URL"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()  # Check for 404s or 500s

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Note: Inspect the Google Skills Boost page to confirm the exact class name. 
        # Typically, badges are wrapped in 'profile-badge' or 'ql-badge' classes.
        badges = soup.find_all('div', class_='profile-badge')
        
        return len(badges), "Success"

    except requests.exceptions.HTTPError as e:
        return 0, f"HTTP Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return 0, "Connection Error"
    except Exception as e:
        return 0, str(e)

def process_students(csv_file):
    """Reads the CSV, processes profiles, and builds the TUI table."""
    results = []
    
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] The file '{csv_file}' was not found.")
        return

    console.print(f"\n[bold blue]Starting Learn With Communities Tracker...[/]")
    console.print(f"Loaded {len(rows)} students. Applying a {RATE_LIMIT_DELAY}s rate limit.\n")

    # Setup TUI Progress Bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Verifying profiles...", total=len(rows))

        for row in rows:
            name = row.get("Name", "Unknown")
            url = row.get("Profile URL", "").strip()
            
            badge_count, status = fetch_badge_count(url)
            completed = badge_count >= REQUIRED_BADGES
            
            results.append({
                "name": name,
                "badges": badge_count,
                "status": status,
                "completed": completed
            })
            
            # Rate Limiting
            time.sleep(RATE_LIMIT_DELAY)
            progress.advance(task)

    # Render Results in a TUI Table
    table = Table(title="Learn With Communities Campaign Status")
    table.add_column("Student Name", style="cyan", no_wrap=True)
    table.add_column("Badges Earned", justify="right", style="magenta")
    table.add_column("Campaign Status", justify="center")
    table.add_column("HTTP Status", style="dim")

    for res in results:
        status_marker = "[bold green]✅ Completed[/]" if res["completed"] else "[bold red]❌ Pending[/]"
        table.add_row(
            res["name"], 
            str(res["badges"]), 
            status_marker,
            res["status"]
        )

    console.print("\n")
    console.print(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Skills Campaign Tracker")
    parser.add_argument(
        "-f", "--file", 
        type=str, 
        default="students.csv", 
        help="Path to the CSV file containing student data"
    )
    args = parser.parse_args()
    
    process_students(args.file)