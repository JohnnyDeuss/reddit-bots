"""
	Delete all comments from a subreddit that are older than a given period. You need to be a
	moderator of the given subreddit to run this bot. This bot has to be scheduled, so make sure to
	read the sticky at /r/RequestABot (https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/).

	Requested by /u/PokestarFan.
	https://www.reddit.com/r/RequestABot/comments/55m05l/bot_that_deletes_a_post_that_is_x_hours_days_weeks/
	Updated request:
	https://www.reddit.com/r/RequestABot/comments/55p3sg/not_that_deletes_post_with_a_certain_flair/
"""
import praw
import OAuth2Util
from datetime import datetime, timedelta
from time import time


#
# Configuration
#

SUBREDDIT = "PokemonCreate"		# Subreddit name, without the /r/ part.
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


#
# Actual bot
#

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
	submissions = list(r.search(search_string, subreddit=SUBREDDIT, sort="new", limit=1000, syntax="cloudsearch"))

	if not submissions:		# No submissions, we're done.
		break

	for submission in submissions:
		t_to = int(submission.created) - 1

		if matches_filters(submission):
			print("Submission matches delete requirements. ID={}".format(submission.id))
			#submission.remove()
		else:
			print("Submission does not match delete requirements. ID={}".format(submission.id))

print("No more submission!\nDone!\n")
