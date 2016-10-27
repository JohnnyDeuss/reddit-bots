import re

import praw
import OAuth2Util


#
# Configuration
#

SUBREDDIT = "BitwiseShiftTest"

#
# Actual bot
#

print("Authenticating...")
r = praw.Reddit("Python:CSSCountdown by /u/BitwiseShift")
r.config.api_request_delay = 1.0
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

def f(m):
	print(m.group())
	return str(int(m.group())-1)

print("Retrieving stylesheet...")
stylesheet = r.get_stylesheet(SUBREDDIT)["stylesheet"]
print("Replacing countdown template strings...")
stylesheet = re.sub(r"(?<=%%)\d+(?=%%)", f, stylesheet)
print("Uploading updated stylesheet...")
r.set_stylesheet(SUBREDDIT, stylesheet)
print("done!")
