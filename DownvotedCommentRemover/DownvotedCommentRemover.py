from sys import argv, exit
import praw
import OAuth2Util
from time import sleep


#
# Configuration
#

SUBREDDIT = "BitwiseShiftTest"		# Subreddit name, without the /r/ part.
# Reply given to deleted comments. Set to None to not reply at all.
# REMOVE_MESSAGE = None
REMOVE_MESSAGE = "Wow, your score is low!"
# All comments below the threshold get deleted.
THRESHOLD = -2
# Set this to None to have it run only once
# TIME_BETWEEN_RUNS = None
TIME_BETWEEN_RUNS = 30		# In number of seconds, the minimum is 30 seconds.


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

r = praw.Reddit("Python:DownvotedCommentRemover")
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

print("Grabbing subreddit...")
subreddit = r.get_subreddit(SUBREDDIT)

def run_bot():
	print("Start bot run")
	print("Grabbing comments...")
	comments = list(subreddit.get_comments(limit=100))
	for comment in comments:
		if comment.score < THRESHOLD and comment.banned_by == None:
			print("Match found! Comment ID: " + comment.id)
			if REMOVE_MESSAGE:
				comment.reply(REMOVE_MESSAGE)
			print("Reply to deleted comment succesful!")
			comment.remove()
			print("Comment has been deleted")
	print("End bot run")

run_bot()
if TIME_BETWEEN_RUNS:
	while True:
		sleep(max(30, TIME_BETWEEN_RUNS))
		run_bot()
