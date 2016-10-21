from sys import argv, exit
import os.path
import atexit
import json
from collections import deque

import praw
import OAuth2Util

import urllib.request
import urllib.parse


#
# Configuration
#

# The temp threshold to post at.
TEMP_THRESHOLD = 100
# The HUKD API key. Check README.md for information on how to get one.
HUKD_API_KEY = "INSERT_KEY_HERE"
# Your username, without the /u/ part, NOT the bot's username.
USERNAME = "epicmindwarp"
# Subreddit to post to.
SUBREDDIT = "hotukdeals"
# Submission footer.
SUBMISSION_FOOTER = "\n******\n^^I'm ^^a ^^bot. ^^For ^^questions ^^or ^^comments, ^^contact ^^/u/{}!\n".format(USERNAME)
# To know which submissions have been handled before between bot runs, the last
# submission parsed is stored in a file.
PERSISTENCE_FILE = "persistence.json"
# To prevent the persistence file from growing too large, limit how many items
# posted items it keeps track of.
PERSISTENCE_LIMIT = 10000
# Whether to post all found matches or just one each run, as to not spam.
QUIT_AFTER_FIRST_POST = True


#
# Actual bot
#

# Read configuration file if one is given.
if len(argv) == 2:
	try:
		with open(argv[1], "r") as f:
			exec(f.read())
	except FileNotFoundError as e:
		print("[ERROR] The config file could not be found.")
		raise e
	except Exception as e:
		print("[ERROR] The config file contains error.")
		raise e
elif len(argv) > 2:
	print("[Error] Correct syntax: {} [config_file]".format(argv[0]))
	exit()


def load_persistence_data():
	print("Loading persistence data...")
	if os.path.isfile(PERSISTENCE_FILE):
		with open(PERSISTENCE_FILE, "r") as f:
			return deque(json.load(f), PERSISTENCE_LIMIT)
	return deque(maxlen=PERSISTENCE_LIMIT)


def save_persistence_data():
	print("Saving persistence data...")
	if posted_before:
		with open(PERSISTENCE_FILE, "w") as f:
			json.dump(list(posted_before), f)


HUKD_API_URL = "http://api.hotukdeals.com/rest_api/v2/"
HUKD_API_PARAMS = {
	"key": HUKD_API_KEY,
	"output": "json",
	"order": "new",
	"page": 1,
	"results_per_page": 1000,
	"min_temp": TEMP_THRESHOLD,
	"exclude_expired": True
}
posted_before = load_persistence_data()
atexit.register(save_persistence_data)

print("Authenticating...")
r = praw.Reddit("Python:HUKDAutoSubmitter by /u/BitwiseShift")
r.config.api_request_delay = 1.0
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

try:
	print("Retrieving new hot deals from HUKD API...")
	f = urllib.request.urlopen(HUKD_API_URL+"?"+urllib.parse.urlencode(HUKD_API_PARAMS))
	hukd_json = f.read().decode("utf-8", errors="ignore")
except:
	print("Could not get data from HUKD API, exiting.")
	exit()

hukd_data = json.loads(hukd_json)
if not os.path.isfile(PERSISTENCE_FILE):
	print("No persistence file detected, assuming this is first run.")
	print("All hot deals found will be stored as to not be posted on the next run.")
	posted_before = [item["deal_link"] for item in hukd_data["deals"]["items"]]
else:
	for item in hukd_data["deals"]["items"]:
		if item["deal_link"] not in posted_before:
			print("New hot deal: "+item["deal_link"])
			posted_before.append(item["deal_link"])
			body = "{description}\n\nDeal URL: [Desktop]({desktop_url}), [Mobile]({mobile_url}){footer}".format(
					description=item["description"],
					desktop_url=item["deal_link"]+"&bot=true",
					mobile_url=item["mobile_deal_link"]+"&bot=true",
					footer=SUBMISSION_FOOTER
			)
			try:
				print("... Posting deal...")
				r.submit(SUBREDDIT, item["title"], body)
				print("... Successfully posted deal.")
			except Exception as e:
				print(e)
				print("... [Error] Failed to post deal!")
			if QUIT_AFTER_FIRST_POST:
				break
print("Done!")
