from sys import argv, exit
from time import sleep
import os.path
import praw
import re
import OAuth2Util
import json
import atexit
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse


#
# Configuration
#

# Your username, without the /u/ part, NOT the bot's username.
USERNAME = "USERNAME"
# List of subreddits to operate in. Subreddits do not have the /r/ part.
ALLOWED_SUBREDDITS = [
	"BitwiseShiftTest",
	"BitwiseShift",
]
# To know which submissions have been handled before between bot runs, the last
# submission parsed is stored in a file.
PERSISTENCE_FILE = "before.json"
# Text to prefix and suffix to the bot's comment.
COMMENT_PREFIX = "***Twitter transcript***\n*****\n"
COMMENT_SUFFIX = ("\n*****\n^^I'm ^^a ^^bot. ^^For ^^questions ^^or ^^comments, ^^contact ^^/u/{}!\n"
		"^^[Source](https://github.com/JohnnyDeuss/reddit-bots/tree/master/TwitterTranscriber).").format(USERNAME)


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
	r = {sr: None for sr in ALLOWED_SUBREDDITS}
	if os.path.isfile(PERSISTENCE_FILE):
		with open(PERSISTENCE_FILE, "r") as f:
			r.update(json.load(f))
			pass
	return r


def save_persistence_data():
	if befores:
		with open(PERSISTENCE_FILE, "w") as f:
			json.dump(befores, f)


def commented_before_top_level(submission):
	comments = list(submission.comments)
	oldLen = 0
	newLen = len(comments)
	while newLen != oldLen:
		oldLen = newLen
		submission.replace_more_comments()
		comments = list(submission.comments)
		newLen = len(comments)
	is_mine = [comment.author.name == r.user.name for comment in comments if comment.author]
	return any(is_mine)


def tweet_html_to_markdown(el):
	if el.name == "[document]":
		return " ".join(tweet_html_to_markdown(childEl) for childEl in el.contents)
	if not el.name:
		return el.string
	if el.name == "a":
		return "[{}]({})".format(" ".join(tweet_html_to_markdown(childEl) for childEl in el.contents), el["href"])
	elif el.name == "blockquote":
		content = " ".join(tweet_html_to_markdown(childEl) for childEl in el.contents)
		return " ".join("> "+line for line in content.splitlines(True)).rstrip("\n")
	elif el.name == "p":
		return " ".join(tweet_html_to_markdown(childEl) for childEl in el.contents)+"\n\n"
	else:
		return ""


def run_bot():
	global befores
	for subreddit, before in befores.items():
		print("[/r/{}] Retrieving new submissions...".format(subreddit))
		submissions = r.get_subreddit(subreddit).get_new(sort="New", limit=100, syntax="cloudsearch", params={"before": before})
		first = True
		for submission in submissions:
			# Update the 'before'.
			if first:
				first = False
				befores[subreddit] = submission.name
			print("+ New submission: ID={}".format(submission.id))
			if submission.is_self:
				twitter_links = TWITTER_LINK_REGEX.findall(submission.selftext)
				if twitter_links:
					if not commented_before_top_level(submission):
						tweet_markdowns = []
						for link in twitter_links:
							print("... Twitter link found: {}.".format(link[1]))
							params = {"url": link[1], "hide_media": 1, "hide_thread": 1, "omit_script": 1}
							tweet_oembed_url = TWITTER_OEMBED_URL+"?"+urllib.parse.urlencode(params)
							try:
								print("... Retrieving tweet from Twitter API.")
								f = urllib.request.urlopen(tweet_oembed_url)
								tweet_json = f.read().decode(f.info().get_content_charset(), "ignore")
							except:
								print("... Could not get tweet, it may not exist.")
								continue
							tweet_data = json.loads(tweet_json)
							soup = BeautifulSoup(tweet_data["html"], "html.parser")
							tweet_markdowns.append("[{}]({})\n\n".format(link[0], link[1])
									+ tweet_html_to_markdown(soup))
						if tweet_markdowns:
							reply_body = COMMENT_PREFIX+"\n*****\n".join(tweet_markdowns)+COMMENT_SUFFIX
							try:
								print("... Posting comment.")
								submission.add_comment(reply_body)
							except praw.errors.APIException:
								print("... Thread too old to comment in. Skipping following submissions.")
								break
					else:
						print("... Commented before! Ignoring.")
				else:
					print("... Does not contain Twitter links.")
			else:
				print("... Not a self-post.")


TWITTER_LINK_REGEX = re.compile(
		r"\[(?P<label>.*?)\]\((?P<url>https?:\/\/(?:mobile\.)?twitter\.com\/(?:#!\/)?[\w]+\/status(?:es)?\/[\d]+)\)",
		re.IGNORECASE)
TWITTER_OEMBED_URL = "https://publish.twitter.com/oembed"
befores = load_persistence_data()
atexit.register(save_persistence_data)

print("Authenticating...")
r = praw.Reddit("Python:TwitterTranscriber by /u/BitwiseShift")
r.config.api_request_delay = 1.0
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

print("Starting bot.")
while True:
	run_bot()
	print("Waiting 35 seconds to recheck submissions.")
	sleep(35)
