"""
	Delete all comments from a subreddit that are older than a given period. You need to be a
	moderator of the given subreddit to run this bot. This bot has to be scheduled, so make sure to
	read the sticky at /r/RequestABot (https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/).
	
	Requested by /u/PokestarFan.
	https://www.reddit.com/r/RequestABot/comments/55m05l/bot_that_deletes_a_post_that_is_x_hours_days_weeks/
"""
import praw
import OAuth2Util
from datetime import datetime, timedelta
from time import time


#
# Configuration
#

SUBREDDIT = "BitwiseShiftTest"		# Subreddit name, without the /r/ part.
# After how long posts get deleted. The given example will delete posts that are 2 days old.
REMOVE_AFTER = timedelta(weeks=0, days=2, hours=0, minutes=0)


#
# Actual bot
#

print("Authenticating...")
r = praw.Reddit('Python:OldCommentRemover by /u/BitwiseShift')
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

# Compute the date before which comments need to be removed (in Reddit's weird timezone).
t_to = int((datetime.now() - REMOVE_AFTER).timestamp()) + 8*60*60

while True:
	print("Retrieving submissions...")
	search_string = "timestamp:0..{}".format(t_to)
	submissions = list(r.search(search_string, subreddit=SUBREDDIT, sort="new", limit=1000, syntax="cloudsearch"))
	
	if not submissions:
		break
	
	for submission in submissions:
		t_to = int(submission.created)
		print("Removing comment. ID={}".format(submission.id))
		submission.remove()

print("No more submission!\nDone!\n")
