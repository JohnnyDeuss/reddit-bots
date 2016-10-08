"""
	Rename user flair CSS class names on mass.

	INSTALL INSTRUCTIONS:
	Follow the instructions at https://github.com/JohnnyDeuss/reddit-bots#reddit-bots.

	Requested by /u/CatAttackPEOW.
	https://www.reddit.com/r/RequestABot/comments/53vz7g/updating_thousands_of_css_class_flairs/
"""
from sys import argv, exit
import praw
import OAuth2Util


#
# Configuration.
#

# Inline configuration, this is what you'll have to fill in to get the bot
# to work. If you want to make a config file, you'll have to copy this section
# into a new file.
SUBREDDIT = "BitwiseShiftTest"		# Subreddit name, without the /r/ part.
# Flair mapping, before the colon is the flair CSS name you want to change. After the colon is the
# flair CSS name you want to change it into.
FLAIR_MAPPING = {
	None: "",		# This line is for people without flairs, leave it.
	"OldFlair1": "NewFlair1",
	"OldFlair2": "NewFlair2",
	# ...
}


#
# Actual bot code
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

r = praw.Reddit("Python:MassFlairRename by /u/BitwiseShift")
o = OAuth2Util.OAuth2Util(r)
o.refresh()

after = None

print("Getting users...")
while True:
	flairs = list(r.get_flair_list(SUBREDDIT, sort="new", limit=100, params={"after": after}))
	if not flairs:
		break
	lastUser = r.get_redditor(flairs[-1]["user"])	# Already set the after, for pagination.
	after = "t2_"+lastUser.id

	l = len(flairs)
	unknowns = []
	unknown_count = 0
	# Map flairs to new values.
	for i in range(l-1,-1,-1):
		# The empty flair texts (None) need to be converted to empty strings.
		if flairs[i]["flair_text"] == None:
			flairs[i]["flair_text"] = ""
		try:
			flairs[i]["flair_css_class"] = FLAIR_MAPPING[flairs[i]["flair_css_class"]]
		except KeyError as e:
			unknown_count += 1
			# Only give a warning the first time an unknown class is encountered.
			if flairs[i]["flair_css_class"] not in unknowns:
				unknowns.append(flairs[i]["flair_css_class"])
				print('Warning: encountered unknown CSS flair class "{}", ignoring.'.format(flairs[i]["flair_css_class"]))
			del flairs[i]
	# Only try to update flairs if there are any changes.
	if unknown_count != l:
		r.set_flair_csv(SUBREDDIT, flairs)
	print("Succesfully changed  {}/{} user flairs!".format(l-unknown_count, l))
	print("Checking for more flaired users")

print("No more users found!\nDone!")
