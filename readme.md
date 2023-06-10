Python script that scrape the public "/read" page of a Writefreely istance and post the new post titles on a Mastodon account.

## Setup
 - The script use python3
 - Install dependencies
   - `pip3 install Mastodon.py`
   - `pip3 install bs4`
 - Create a new app in you mastodon instance under preferences->development and copy the access token
   - In the scopes part you only need "write:statuses"
 - Change the "variables" in the top of the script with yours
 - Run