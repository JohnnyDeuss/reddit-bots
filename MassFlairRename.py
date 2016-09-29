"""
	Rename user flair CSS class names on mass.
	
	Requested by /u/CatAttackPEOW.
	https://www.reddit.com/r/RequestABot/comments/53vz7g/updating_thousands_of_css_class_flairs/
"""
import praw
import OAuth2Util

#
# Configuration.
#

USERNAME = "BitwiseShift"	# Fill in your username.
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

r = praw.Reddit('Python:MassFlairRename by /u/BitwiseShift, run by {}'.format(USERNAME))
o = OAuth2Util.OAuth2Util(r)
o.refresh()

flairs = list(r.get_flair_list(SUBREDDIT, limit=None))
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
print('Succesfully changed  {}/{} user flairs!'.format(l-unknown_count, l))
