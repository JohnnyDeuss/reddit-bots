from sys import argv, exit
import praw


#
# Configuration.
#

SUBREDDIT = "YOUR_SUBREDDIT"		# Subreddit name, without the /r/ part.
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

reddit = praw.Reddit(client_id='YOUR_CLIENT_ID',
				client_secret='YOUR_CLIENT_SECRET',
				username='YOUR_USERNAME',
				password='YOUR_PASSWORD',
				user_agent='Python:MassFlairRename by /u/BitwiseShift')
subreddit = reddit.subreddit(SUBREDDIT)

unknowns = []
unknown_count = 0
flair_list = []
l = 0

print("Getting flairs...")
for flair in subreddit.flair():
	l += 1
	new_flair = flair
	# The empty flair texts (None) need to be converted to empty strings.
	if new_flair["flair_text"] is None:
		new_flair["flair_text"] = ""
	try:
		new_flair["flair_css_class"] = FLAIR_MAPPING[flair["flair_css_class"]]
	except KeyError as e:
		unknown_count += 1
		# Only give a warning the first time an unknown class is encountered.
		if flair["flair_css_class"] not in unknowns:
			unknowns.append(flair["flair_css_class"])
			print('Warning: encountered unknown CSS flair class "{}", ignoring.'.format(flair["flair_css_class"]))
	flair_list.append(new_flair)
# Only try to update flairs if there are any changes.
if flair_list:
	subreddit.flair.update(flair_list)
	print("Succesfully changed  {}/{} user flairs!".format(l-unknown_count, l))
else:
	print("No flairs found that can be changed.")
