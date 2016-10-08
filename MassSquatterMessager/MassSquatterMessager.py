"""
	This script will investigate a mass squater's subreddits and figure out which of them are
	username subreddits. Every username subreddit will be verified to make sure that the user it is
	named after isn't also a moderator of it. Every user who's username subreddit is being squated
	will be messaged. This scrapes the squatter's user page to find the subreddits he moderated, as
	Reddit doesn't have an API call for this.

	For some users, sending messages requires the solving of a captcha, this is
	not supported by the script at the moment.

	INSTALL INSTRUCTIONS:
	Follow the instructions at https://github.com/JohnnyDeuss/reddit-bots#reddit-bots.
	For the scraping of HTML, you'll need to install BeautifulSoup. This can be
	installed by running the command `pip install beautifulsoup4`.

	Requested by /u/Stuart98.
	https://www.reddit.com/r/RequestABot/comments/55dlxk/need_a_bot_to_send_mass_pms_to_users_matching_a/

	DISCLAIMER:
	This script was purposefully made to message only people whose username subreddit is being
	squatted by a mass squatter. This bot could be altered to mass message anyone. Don't do this
	unless you have a damn good reason. Don't be a dick. Mass messaging is spam if there isn't a
	good reason and spamming gets you banned. Don't be a dick.
"""
from sys import argv, exit
import urllib.request
import urllib.error
import praw
import OAuth2Util
from time import sleep
from bs4 import BeautifulSoup


#
# Configuration
#

# Inline configuration, this is what you'll have to fill in to get the bot
# to work. If you want to make a config file, you'll have to copy this section
# into a new file.
SQUATTER_USERNAME = "ragwort"		# Without the /u/ part
EXCLUDE_LIST = ["fagwort"]			# List of users to exclude from the mass messaging.
TITLE = "Subreddit squatter"		# Message title
# The message you want to send to people. The message can automatically be filled in with names.
# You can use {YOU} to use the person you're sending a message to's username. {ME} will turn into
# your username and {SQUATTER} will turn into the squatter's username. See the example message
# below.
MESSAGE = """
Hi /u/{YOU}, I just want to let you know that a user called /u/{SQUATTER} is squatting a
subreddit that has the same name as your username. He has been squatting a lot of subreddits like
this and I'm trying to get the subreddits to be released, but I need your help to do this!
Please PM me if you would be so kind as to help me out!

Sincerely, /u/{ME}.
"""


#
# Actual bot
#

# Read configuration file if one is given.
if len(argv) == 2:
	try:
		exec(open(argv[2], "r").read())
	except FileNotFoundError as e:
		print("[ERROR] The config file could not be found.")
		raise e
	except:
		print("[ERROR] The config file contains error.")
		raise e
elif len(argv) > 2:
	print("[Error] Correct syntax: {} [config_file]".format(argv[0]))
	exit()


def get_moderated_subreddits(username):
	""" Get the subreddit someone moderates. The Reddit API doesn't have an entrypoint for this,
		so we'll scrape it from the user page.
	"""
	url = USER_PAGE.format(username)
	print("... "+url)
	attempt = 0
	while attempt < MAX_ATTEMPTS:
		try:
			req = urllib.request.Request(url, headers={'User-agent': UA})
			f = urllib.request.urlopen(req)
			break
		except urllib.error.HTTPError as e:
			if e.code == 404 or e.code == 403:
				return None
			attempt += 1
			print("... Try {}/{}: Something went wrong while getting user page. Retrying in {} seconds.".format(attempt, MAX_ATTEMPTS, RETRY_DELAY))
			sleep(RETRY_DELAY)
	else:
		print("Unable to get the page, skipping.")
		return None

	html = f.read().decode(f.info().get_content_charset()).encode("ascii", errors="ignore")
	soup = BeautifulSoup(html, 'html.parser')
	side_mod = soup.find("ul", {"id": "side-mod-list"})
	return [] if side_mod == None else [tag.text for tag in side_mod.find_all("a")]


# Static bot constants.
UA = "Python:MassSquatterMessager by /u/BitwiseShift"
EXCLUDE_LIST = [user.lower() for user in EXCLUDE_LIST]
USER_PAGE = "https://www.reddit.com/user/{}/"
RETRY_DELAY = 2
MAX_ATTEMPTS = 5

print("Retrieving squatter's user page...")
subreddits = get_moderated_subreddits(SQUATTER_USERNAME)
if subreddits == None:
	print("Can't get the squatter's moderated subreddits. Check the username or try again later.")
	exit()
print("Found {} subreddits under squatter's control...".format(len(subreddits)))
print("Finding out which subreddits also have a user with the same name...")

user_also_mod_count = 0
banned_users = 0
users = []
l = len(subreddits)

for i, subreddit in enumerate(subreddits[:], start=1):
	print("({}/{}) Checking {}...".format(i, l, subreddit))
	user = subreddit[3:]
	subreddits = get_moderated_subreddits(user)
	if subreddits == None:
		banned_users += 1
		print("... Could not get the user's moderated subreddits. Maybe the user is banned?")
	else:
		print("... Making sure they aren't a moderator of the subreddit themselves.")
		if subreddit in subreddits:
			print("... This user is also a moderator of his subreddit. Ignoring.")
			user_also_mod_count += 1
		else:
			print("... User is not a moderator of the subreddit. Adding to message queue.")
			users.append(user)

if not users:
	print("No squatted subreddits found")
	exit()

print("Found {} subreddits that were not named after users or named after deleted users!".format(len(subreddits)-len(users)-user_also_mod_count-banned_users))
print("Found {} subreddits could not be checked! Either due to users being banned or network issues!".format(banned_users))
print("Found {} subreddits that were also modded by the users themselves!".format(user_also_mod_count))
print("Found {} squated subreddits!".format(len(users)))
print("Filtering usernames...")
users = [user for user in users if user.lower() not in EXCLUDE_LIST]

print("-"*80)
print("About to start sending messages. You will send your message to {} users.\n"
      "Are you sure you want to continue? This is your last chance to quit.".format(len(users)))
input("Press ENTER to continue...")
print("Authenticating...")
r = praw.Reddit(UA)
o = OAuth2Util.OAuth2Util(r)
o.refresh()

print("Messaging all {} users.".format(len(users)))
l = len(users)
for i, user in enumerate(users, start=1):
	print("({}/{}) Messaging /u/{}...".format(i, l, user))
	r.send_message(user, TITLE, MESSAGE.format(ME=r.user.name, YOU=user, SQUATTER=SQUATTER_USERNAME))
	break
print("Done!")
