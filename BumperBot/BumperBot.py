from sys import argv, exit
import json
import traceback

import praw
import OAuth2Util


#
# Configuration
#

# Where the bot will store the URLs of the submissions it is bumping.
PERSISTENCE_FILE = "persistence.json"
# A list of thread URLs to bump the first time this bot is run. After the first
# run, the newly posted threads will be stored in the persistence file and they
# will be used for subsequent runs.
INITIAL_THREADS = [
	"https://www.reddit.com/r/YOUR_SUBREDDIT/comments/ID1",
	"https://www.reddit.com/r/YOUR_SUBREDDIT/comments/ID2",
]


#
# Actual bot
#

print("Authenticating...")
r = praw.Reddit("Python:BumperScript by /u/BitwiseShift")
r.config.api_request_delay = 1.0
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

try:
	with open(PERSISTENCE_FILE) as f:
		urls = json.load(f)
except:
	print("Couldn't read persistence file, using INITIAL_THREADS instead.")
	urls = INITIAL_THREADS
try:
	for url in urls[:]:
		oldSubmission = r.get_submission(url=url)
		print("Old submission: "+oldSubmission.permalink)
		print("... Posting new submission.")
		newSubmission = r.submit(oldSubmission.subreddit.display_name, oldSubmission.title, oldSubmission.selftext)
		print("... Marking old submission as closed.")
		oldSubmission.mark_as_nsfw()
		print("... Replacing URL.")
		urls.remove(url)
		urls.append(newSubmission.permalink)
		print("... Flairing new submission.")
		newSubmission.select_flair(oldSubmission.link_flair_css_class, oldSubmission.link_flair_text)
except Exception as e:
	print("An error occurred! Quitting.")
finally:
	print("Saving updated files.")
	with open(PERSISTENCE_FILE, "w") as f:
		json.dump(urls, f)
