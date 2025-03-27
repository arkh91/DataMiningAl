import os
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re

# Create media folder if it doesn't exist
if not os.path.exists('media'):
    os.makedirs('media')

def validate_username(username):
    """Check if a Twitter username exists by trying to access their profile"""
    url = f"https://twitter.com/{username}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check for suspended account
        if "account suspended" in response.text.lower():
            return False, "Account is suspended"
        
        # Check for non-existent account
        if response.status_code == 404 or "doesn't exist" in response.text.lower():
            return False, "User not found. Please check the username."
        
        # Check for private account
        if "These Tweets are protected" in response.text:
            return False, "Account is private"
            
        return True, "User exists and is available"
    
    except requests.RequestException as e:
        return False, f"Error checking username: {e}"

def get_followings(username):
    """Get followings by scraping Twitter's following page"""
    url = f"https://twitter.com/{username}/following"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Twitter's structure changes frequently - this selector might need updating
        following_tags = soup.find_all('a', href=re.compile(r'^/[\w]+$'))
        
        followings = []
        for tag in following_tags:
            href = tag.get('href', '')
            if href and href != f'/{username}' and href != '/home':
                followings.append(f"@{href[1:]}")
        
        # Remove duplicates while preserving order
        seen = set()
        followings = [x for x in followings if not (x in seen or seen.add(x))]
        
        return True, followings
    
    except requests.RequestException as e:
        return False, f"Error fetching followings: {e}"

def save_to_csv(username, followings):
    """Save followings to a CSV file in media folder"""
    timestamp = datetime.now().strftime("%m%d%Y-%H%M%S")
    filename = f"media/{timestamp}-{username}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Following Usernames"])
            for following in followings:
                writer.writerow([following])
        return True, filename
    except Exception as e:
        return False, f"Error saving to CSV: {e}"

def twitter_option():
    """Handle the Twitter option"""
    username = input("Enter Twitter username (without @): ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    
    print(f"Checking username @{username}...")
    valid, result = validate_username(username)
    
    if not valid:
        print(result)
        return
    
    print(f"Found valid user @{username}. Attempting to fetch followings...")
    print("Note: Web scraping may not get all followings and might be unreliable.")
    
    success, followings = get_followings(username)
    
    if not success:
        print(followings)
        return
    
    if not followings:
        print("Couldn't fetch any followings. Twitter's structure may have changed.")
        return
    
    print(f"Found {len(followings)} followings. Saving to file...")
    success, filename = save_to_csv(username, followings)
    
    if success:
        print(f"Successfully saved followings to {filename}")
    else:
        print(filename)

def display_menu():
    """Display the main menu"""
    print("\n" + "="*40)
    print("TWITTER FOLLOWING EXPORTER (NO API)".center(40))
    print("="*40)
    print("0: Exit")
    print("1: Twitter")
    print("="*40)
    print("Note: This uses web scraping which may be unreliable")
    print("="*40)

def main():
    while True:
        display_menu()
        choice = input("Enter your choice (0-1): ").strip()
        
        if choice == "0":
            print("Exiting program. Goodbye!")
            break
        elif choice == "1":
            twitter_option()
        else:
            print("Invalid choice. Please try again.")
        
        # Small delay to be polite to Twitter's servers
        time.sleep(2)

if __name__ == "__main__":
    main()
