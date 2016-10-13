from sys import argv, exit
from collections import OrderedDict
from functools import reduce
import re
import httplib2

# Reddit API
import praw
import OAuth2Util


#
# Configuration.
#

# How many years to jump (keep in mind that the transition from BCE to CE should
# be on the border of a timespan).
YEARS_TO_JUMP = 25
# This is a regular expression used to find the date inside the sidebar.
# It describes what the date string looks like. The example regex will look
# for "Year:", followed by a date, followed by a hyphen, followed by another
# date, followed by CE or BCE, with whitespace allowed anywhere in between those
# parts.
YEAR_DETECTION_REGEX = r"(Year:\s*)(?P<from>[0-9]+)(\s*\-\s*)(?P<to>[0-9]+)(\s*)(?P<ce>B?CE)"
# Subreddit to work on, without the /r/ part.
SUBREDDIT = "DawnPowers"


#
# Actual bot code
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


print("Authenticating with Reddit...")
r = praw.Reddit("Python:PowersDateUpdater by /u/BitwiseShift")
o = OAuth2Util.OAuth2Util(r)
o.refresh()

print("Getting sidebar info...")
sr = r.get_subreddit(SUBREDDIT)
m = re.search(YEAR_DETECTION_REGEX, sr.description, re.IGNORECASE)
print("Finding date string...")
if not m:
	print("Could not find the date string!")
else:
	print("Recalculating date...")
	date = m.groupdict()
	if date["ce"] == "BCE":
		# Deal with BCE to CE.
		if date["to"] == "0":
			# To not make years seemingly shify when crossing over into CE,
			# consider year 0 to be year 1.
			date["from"] = "1"
			date["to"] = str(YEARS_TO_JUMP)
			date["ce"] = "CE"
		else:
			date["from"] = date["to"]
			date["to"] = str(int(date["to"])-YEARS_TO_JUMP)
	else:
		date["from"] = date["to"]
		date["to"] = str(int(date["to"])+YEARS_TO_JUMP)

	new_description = re.sub(YEAR_DETECTION_REGEX, r"\g<1>"+date["from"]+r"\g<3>"+date["to"]+r"\5"+date["ce"], sr.description)

	print("Submitting new sidebar...")
	sr.update_settings(description=new_description)
print("Done!")
