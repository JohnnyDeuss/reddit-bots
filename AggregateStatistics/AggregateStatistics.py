from sys import argv, exit
import praw
import OAuth2Util
from datetime import datetime, timedelta
from time import time


#
# Configuration
#

SUBREDDIT = "BuildAPC"		# Subreddit name, without the /r/ part.
FLAIR = "Build upgrade"
LIMIT = 10					# The amount of submissions to load. Using None automatically loads as many as allowed.
DAYS_TO_GO_BACK = 7			# The end date will likely not be reached for active subs due to the request limit.


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

print("Authenticating...")
r = praw.Reddit("Python:AggregateStatistics by /u/BitwiseShift")
r.config.api_request_delay = 1.0
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

t_to = int(time()) +8*60*60				# After trying to get timezones and dst to work, I give up, I've stopped caring.
t_from = t_to - 24*60*60*DAYS_TO_GO_BACK

print("Retrieving submissions...")
search_string = "(and timestamp:{}..{} flair:'{}')".format(t_from, t_to, FLAIR)
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
	t = datetime.utcfromtimestamp(submission.created_utc).strftime("%x %X")
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
