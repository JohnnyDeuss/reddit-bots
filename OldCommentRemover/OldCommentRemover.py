from sys import argv, exit
import praw
import OAuth2Util
from datetime import datetime, timedelta
from time import time


#
# Configuration
#

# Inline configuration, this is what you'll have to fill in to get the bot
# to work. If you want to make a config file, you'll have to copy this section
# into a new file.

# Subreddit name, without the /r/ part. Setting this to None will have the
# script go through your submissions instead. This automatically sets the
# USE_DELETE option to True.
SUBREDDIT = "PokemonCreate"
# After how long posts get deleted. The given example will delete posts that are
# 2 days old. To delete any posts, regardless of age, simply set all values to 0.
REMOVE_AFTER = timedelta(weeks=0, days=0, hours=12, minutes=0)
REMOVE_MODERATOR_POSTS = False		# Whether to delete moderator posts.
# The following list, along with IGNORE_FILTERS will determine which submissions
# get deleted. Notice how None means that the property is ignored, while an
# empty string means that it matches submissions that don't have it set. Be sure
# you understand the difference.
DELETE_FILTER = [
	# Deletes posts that have both the given flair class and text.
	{"class": "SOME_CSS_CLASS", "text": "SOME_FLAIR_CLASS"},
	# Deletes posts that have the given flair class, regardless of text.
	{"class": "SOME_CSS_CLASS", "text": None},
	# Deletes posts that have the given flair class that have no flair text.
	{"class": "SOME_CSS_CLASS", "text": ""},
	# Deletes posts that have the given flair text, regarless of class.
	{"class": None, "text": "SOME_FLAIR_CLASS"},
	# Delete posts that don't have neither a flair class nor text.
	{"class": "", "text": ""},
	# Delete all posts, regardless of flairs.
	{"class": None, "text": None}
]
# Ignores certain flairs even if they are matched by the ONLY_DELETE lists before.
IGNORE_FILTER = [
	# Deletes posts that have both the given flair class and text.
	{"class": "SOME_CSS_CLASS", "text": "SOME_FLAIR_CLASS"},
]
# There are two ways of removing a comments. If this option is False, it will
# act as a moderator removing comments from their subreddit. If this is true,
# it will act as a user deleting his own comments. This will however not delete
# comments that have already been removed by a moderator.
USE_DELETE = False


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


def matches_filter(submission, filter):
	css_class = submission.link_flair_css_class if submission.link_flair_css_class != None else ""
	text = submission.link_flair_text if submission.link_flair_text != None else ""
	flair_signature = {"class": submission.link_flair_css_class, "text": submission.link_flair_text}
	# Check catch-all rule.
	if {"class": None, "text": None} in filter:
		return True
	# Rules containing both a flair class and text.
	if flair_signature in filter:
		return True
	# Flairs containing only a flair class.
	if css_class in [rule["class"]  for rule in filter if rule["text"] == None]:
		return True
	# Flairs containing only a flair text.
	if text in [rule["text"] for rule in filter if rule["class"] == None]:
		return True
	return False


def matches_filters(submission):
	if not REMOVE_MODERATOR_POSTS and submission.author.name in moderators:
		return False
	return not matches_filter(submission, IGNORE_FILTER) and matches_filter(submission, DELETE_FILTER)


# Enforce config limits.
if SUBREDDIT == None:
	USE_DELETE = True

# Compute the date before which comments need to be removed (in Reddit's weird timezone).
t_to = int((datetime.now() - REMOVE_AFTER).timestamp()) + 8*60*60

print("Authenticating...")
r = praw.Reddit("Python:OldCommentRemover by /u/BitwiseShift")
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

if not REMOVE_MODERATOR_POSTS:
	print("Getting moderator list...")
	moderators = [user.name for user in r.get_subreddit(SUBREDDIT).get_moderators()]

while True:
	print("Retrieving submissions...")
	search_string = "timestamp:0..{}".format(t_to)
	# If we're using delete, search only own submissions instead.
	if USE_DELETE:
		search_string = "(and {} author:'{}')".format(search_string, r.user.name)
	submissions = list(r.search(search_string, subreddit=SUBREDDIT, sort="new", limit=1000, syntax="cloudsearch"))

	if not submissions:		# No submissions, we're done.
		break

	for submission in submissions:
		t_to = int(submission.created) - 1

		if matches_filters(submission):
			print("Submission matches delete requirements. ID={}".format(submission.id))
			if USE_DELETE:
				submission.delete()
			else:
				submission.remove()
		else:
			print("Submission does not match delete requirements. ID={}".format(submission.id))

print("No more submission!\nDone!\n")
