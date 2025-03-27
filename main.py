import os
import csv
from datetime import datetime
import tweepy
import time

# Create media folder if it doesn't exist
if not os.path.exists('media'):
    os.makedirs('media')


def setup_twitter_api():
    """Set up Twitter API credentials"""
    # Replace these with your own Twitter API credentials
    consumer_key = 'YOUR_CONSUMER_KEY'
    consumer_secret = 'YOUR_CONSUMER_SECRET'
    access_token = 'YOUR_ACCESS_TOKEN'
    access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        return api
    except Exception as e:
        print(f"Error setting up Twitter API: {e}")
        return None


def validate_username(api, username):
    """Check if a Twitter username exists and is available"""
    try:
        user = api.get_user(screen_name=username)
        return True, user
    except tweepy.TweepError as e:
        if e.response.status_code == 404:
            return False, "User not found. Please check the username."
        elif e.response.status_code == 403:
            return False, "Account is suspended or private."
        else:
            return False, f"Error: {e}"


def get_followings(api, username):
    """Get all followings for a given username"""
    followings = []
    try:
        for user in tweepy.Cursor(api.get_friends, screen_name=username).items():
            followings.append(f"@{user.screen_name}")
        return True, followings
    except tweepy.TweepError as e:
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


def twitter_option(api):
    """Handle the Twitter option"""
    username = input("Enter Twitter username (without @): ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    print(f"Checking username @{username}...")
    valid, result = validate_username(api, username)

    if not valid:
        print(result)
        return

    print(f"Found valid user @{username}. Fetching followings...")
    success, followings = get_followings(api, username)

    if not success:
        print(followings)
        return

    if not followings:
        print("This user isn't following anyone.")
        return

    print(f"Found {len(followings)} followings. Saving to file...")
    success, filename = save_to_csv(username, followings)

    if success:
        print(f"Successfully saved followings to {filename}")
    else:
        print(filename)


def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 40)
    print("TWITTER FOLLOWING EXPORTER".center(40))
    print("=" * 40)
    print("0: Exit")
    print("1: Twitter")
    print("=" * 40)


def main():
    api = setup_twitter_api()
    if not api:
        print("Failed to initialize Twitter API. Please check your credentials.")
        return

    while True:
        display_menu()
        choice = input("Enter your choice (0-1): ").strip()

        if choice == "0":
            print("Exiting program. Goodbye!")
            break
        elif choice == "1":
            twitter_option(api)
        else:
            print("Invalid choice. Please try again.")

        # Small delay for better user experience
        time.sleep(1)


if __name__ == "__main__":
    main()
