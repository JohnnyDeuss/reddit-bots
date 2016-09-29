"""
	This will aggregate flair statistics over the newest submissions returned by a search. The
	generated statistics are total/avg upvotes, estimated total/avg downvotes, estimated total/avg
	votes and average upvote percentage. The bot can be altered to look for other kind of post by
	changing the search request.

	This bot is extremely slow because it has to make a lot of requests. Getting downvote count is
	very difficult, intentionally so. Even after the slow process of gathering them, the result is
	still an estimate, as it is derived from the upvote_ratio. An upvote_ratio of 71% may be given
	but may also give only 1 upvote. It is impossible to get 71% upvote_ratio with 1 upvote. So the
	upvote count is likely behind, because 71% can be reached with 5 upvotes and 2 downvotes. Don't
	run this bot perpetually, as it makes way too many requests for little amounts of data.

	Requested by /u/Ace_InTheSleeve.
	https://www.reddit.com/r/RequestABot/comments/54t6f3/bot_that_aggregates_upvote_percentage_of_threads/
"""
import praw
import OAuth2Util
import time
from datetime import datetime, timedelta
# Needed to deal with the clusterfuck that is timezones, since Reddit doesn't use epoch timezone, but SF timezone instead.
# I don't even want to know what they are doing when dst is applied.
import pytz


#
# Configuration
#
USERNAME = "BitwiseShift"
SUBREDDIT = "BuildAPC"
FLAIR = "Build upgrade"
LIMIT = 1000			# The amount of submissions to load. Using None automatically loads as many as allowed.
DAYS_TO_GO_BACK = 7		# The end date will likely not be reached for active subs due to the request limit.

#
# Actual bot
#
print("Authenticating...")
r = praw.Reddit('Python:StatisticsAggregate by /u/BitwiseShift, run by {}'.format(USERNAME))
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

# Handle Reddit's awful timestamps, using local instead of epoch timestamps. I'm also assuming they
# are following the sf dst as well *sigh*.
reddit_tz = pytz.timezone("America/Los_Angeles")						# The local timezone reddit insists on working in.
t_to = datetime.now(tz=pytz.utc).replace(tzinfo=reddit_tz)				# Get Reddit's local timestamp.
t_from = reddit_tz.normalize(t_to - timedelta(days=DAYS_TO_GO_BACK))	# Go back x days and deal with dst transitions.

print("Retrieving submissions...")
search_string = "(and timestamp:{}..{} flair:'{}')".format(int((t_from).timestamp()), int((t_to).timestamp()), FLAIR)
submissions = r.search(search_string, subreddit=SUBREDDIT, sort="new", limit=LIMIT, syntax="cloudsearch")

print("Gathering additional submission statistics:")
i = 0
stats = {"ups": 0, "downs": 0, "total": 0, "up_percent": 0, "oldest": None}
for submission in submissions:
	i += 1
	submission.refresh()
	stats["ups"] += submission.ups
	# If there are 0 upvotes, the upvote_ratio is useless, so use 1 instead.
	alt_ups = submission.ups if submission.ups else 1
	downs = round(alt_ups/submission.upvote_ratio - alt_ups)
	stats["downs"] += downs
	stats["total"] += submission.ups + downs
	stats["up_percent"] += submission.upvote_ratio
	# Thankfully, they do have a epoch timestamp on submission creation dates.
	t = datetime.fromtimestamp(submission.created_utc, tz=pytz.utc).astimezone(tz=None).strftime("%x %X")
	print("... {:4}  date: {} | up%: {:3d}% | ups: {:4} | downs: {:4} | total: {:4} | id: {}".format(
	i, t, int(submission.upvote_ratio*100), submission.ups, downs, submission.ups + downs, submission.id))
print("Done!\n")

# Average out percentages.
stats["up_percent"] = int((stats["up_percent"] / i) * 100 if i > 0 else 0)

# Ouput statistics.
if i:
	print("Generated statistics over {} latest '{}' submissions:".format(i, FLAIR))
	print("{:25} {:4d}%".format("Average upvote %", stats["up_percent"]))
	print("{:25} {:7.2f}".format("Average upvotes", stats["ups"]/i))
	print("{:25} {:7.2f}".format("Average downvotes*", stats["downs"]/i))
	print("{:25} {:7.2f}".format("Average votes*", stats["total"]/i))
	print("{:25} {:4d}".format("Total upvotes", stats["ups"]))
	print("{:25} {:4d}".format("Total downvotes*", stats["downs"]))
	print("{:25} {:4d}".format("Total votes*", stats["total"]))
	print("* Total votes and downvotes are estimated")
else:
	print("No submissions found matching your search!")
