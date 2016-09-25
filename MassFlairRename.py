import praw

# Fill in this configuration:
USR = "INSERT_USERNAME"
PWD = "INSERT_PASSWORD"
SUBREDDIT = "INSERT_SUBREDDIT"	# Subreddit name, without the /r/ part
# Fill in how you want to replace CSS flair names, in the example mapping, OldFlair1 will turn into
# NewFlair1 and OldFlair2 will turn into NewFlair2.
FLAIR_MAPPING = {
	None: "",					# This line is for people without flairs, leave it.
	"hello": "NewFlair1",
	"NewFlair1": "NewFlair2"
}

		
r = praw.Reddit('Python:MassFlairRename (by /u/BitwiseShift)')

try:
	r.login(USR, PWD, disable_warning=True)
except praw.errors.InvalidUserPass:
	print('Incorrect username or password')
else:
	errors_occured = 0
	flairs = list(r.get_flair_list(SUBREDDIT, limit=None))
	# Update flairs.
	for user in flairs:
		# The empty flair texts (None) need to be converted to empty strings.
		if user["flair_text"] == None:
			user["flair_text"] = ""
		try:
			user["flair_css_class"] = FLAIR_MAPPING[user["flair_css_class"]]
		except KeyError as e:
			errors_occured += 1
			print('Error: encountered CSS flair class "{}".'
					.format(user["flair_css_class"]))

	if errors_occured:
		print('{} errors occurred, no flairs were changed.'.format(str(errors_occured)))
	else:
		r.set_flair_csv(SUBREDDIT, flairs)
		print('Succesfully changed all flairs! ({} total)'.format(str(len(flairs))))
input('Press enter to exit')
