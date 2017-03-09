from sys import argv, exit
from collections import OrderedDict
from functools import reduce
import re
import httplib2

# Google API
from apiclient import discovery
from apiclient.errors import HttpError
from oauth2client import client, tools
from oauth2client.file import Storage

# Reddit API
import praw
import OAuth2Util


#
# Configuration.
#

# The ID of the spreadsheet, which can be found in the URL. This example is the
# ID for https://docs.google.com/spreadsheets/d/1v8SVnzrGaupBKm6CbtmPjMqOrkcl0_sfEW0eEcujkys/edit
SPREADSHEET_ID = "1v8SVnzrGaupBKm6CbtmPjMqOrkcl0_sfEW0eEcujkys"
# The flair sheet is the sheet where the username, mail, snail mail and flair
# assignment columns are. The bot assumes these columns are given in this order
# starting in column A and the actual values start in row 2.
FLAIR_SHEET = "Sheet1"
# This bot will store the timestamp of the last comment it handled. This way it
# will know which comments have already been handled. This reference will
# be stored in the cell indicated here. See
# https://developers.google.com/sheets/guides/concepts#a1_notation to know how
# to reference cells. You can always hide these in a hidden sheet if you prefer
# them not being visible on the main sheet.
PREV_COMMENT_TIME_CELL = FLAIR_SHEET+"!J2"
# The bot will also store a reference to the previous thread it processed, this
# way it can handle any new comments in the old sticky before going to the new
# one. It will also make it easy for the bot to know when the "prev comment"
# value is no longer relevant, as the sticky thread changed.
PREV_THREAD_ID_CELL = FLAIR_SHEET+"!I2"
# if a user tries to enter a high combined verification count for a single user,
# the bot will not automatically update the count, but send an email to the
# moderators instead. E.g. with a threshold of 30, "/u/user 20 20" will not
# automatically be added, but will cause a mail to be sent to the mods instead.
COUNT_THRESHOLD_USER = 10
# The same as before, except it will look if the total verification count of a
# comment is high, instead of just the verified count for a single user.
COUNT_THRESHOLD_COMMENT = 30
# A list of mods that will be mailed if the bot encounters something fishy. If
# the list is empty, no mods will be mailed. Usernames are always written
# without the /u/ part. To send to all moderators of a subreddit, write
# /r/subreddit_name
#MODS = ["wmeacham", ]
#MODS = ["/r/penpals", ]
MODS = ["/r/BitwiseShiftTest"]
# A definition of all ranks in descending order of prestige. The first value
# must be the flair CSS class, the second is a function determining whether
# a user has met the conditions for this flair. I guessed these, change them
# to their actual values! The requirements function gets passed a row from the
# datasheet, whose values are all strings.
RANKS = OrderedDict([
	("combogold", lambda row: int(row[1]) >= 300 and int(row[2]) >= 100),
	("goldsnail", lambda row: int(row[1]) >= 300 or int(row[2]) >= 100),
	("combosilver", lambda row: int(row[1]) >= 30 and int(row[2]) >= 10),
	("silversnail", lambda row: int(row[1]) >= 30 or int(row[2]) >= 10),
	("combobronze", lambda row: int(row[1]) >= 3 and int(row[2]) >= 1),
	("bronzeemail", lambda row: int(row[1]) >= 3 or int(row[2]) >= 1),
	("", lambda row: True),	# Catch-all, for people who have not met any requirements yet.
])
# Wether to allow users to verify themselves.
ALLOW_SELF_VERIFICATION = False


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


class colors:
	# Adapted from https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
	OK = "\033[92m\033[1m"
	WARNING = "\033[93m\033[1m"
	ERROR = "\033[91m\033[1m"
	INPUT = "\033[94m\033[1m"
	ENDC = "\033[0m"


def get_credentials():
	"""	Gets valid user credentials from storage.
		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
		Credentials, the obtained credential.
	"""
	store = Storage("sheets.googleapis.com-python-penpalsbot.json")
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		credentials = tools.run_flow(flow, store)
	return credentials


def get_verification_thread():
	print("Looking for new verification sticky...")
	print("Checking top sticky...", end="")
	sticky = r.get_sticky(SUBREDDIT, True)
	if "verification post" not in sticky.title.lower():
		print("\nChecking bottom sticky...", end="")
		sticky = r.get_sticky(SUBREDDIT, False)
		if "verification post" not in sticky.title.lower():
			sticky = None
	print(colors.OK+" DONE"+colors.ENDC)
	return sticky


def message_mods(subject, message):
	""" Lazy loaded send mods a message. """
	return
	global MODS
	for mod in MODS:
		try:
			r.send_message(mod, subject, message, from_sr=SUBREDDIT)
		except praw.errors.Forbidden:
			print(colors.WARNING+"[WARNING]"+colors.ENDC+" Unable to send a message to /u/{}".format(mod))


def expand_comments(thread):
	""" Expand top-level comments to the point where there are no more comments.
		Returned comments are sorted descendingly by time.
	"""
	comments = list(thread.comments)
	oldLen = 0
	newLen = len(comments)
	while newLen != oldLen:
		oldLen = newLen
		thread.replace_more_comments()
		comments = list(thread.comments)
		newLen = len(comments)
	comments.sort(key=lambda x: int(x.created_utc), reverse=True)
	return comments


def total_verification_count(verifications):
	return reduce(lambda a, x: a + int(x["mail_count"]) + int(x["letter_count"]), verifications, 0)


def process_comments(thread, prev_comment_time=0):
	""" Process comments for verification strings.
		Returns the UTC timestamp of the last processed comment. If no new
		comments were found, returns None.
	"""
	comments = expand_comments(thread)
	if not comments or int(comments[0].created_utc) <= prev_comment_time:
		print("No new comments found.")
		return None
	for comment in comments:
		if int(comment.created_utc) <= prev_comment_time:
			break
		print("+ Handling new comment. ID={}".format(comment.id))
		verifications = []	# Stores all verifications of a comment until it is processed.
		error_occurred = False
		# Start looking for verification count strings.
		paragraphs = comment.body.splitlines()
		for paragraph in paragraphs:
			match = RE_VERIFICATION_SYNTAX.match(paragraph)
			if match:
				print("... Verification count string found: "+paragraph)
				# Add user to added_count if he wasn't in there yet.
				data = match.groupdict()
				if not ALLOW_SELF_VERIFICATION and comment.author.name == data["username"]:
					print("... "+colors.WARNING+"[WARNING]"+colors.ENDC+" Trying to verify himself. Ignoring and messaging mods.")
					message_mods("Self-verification", """
					It appears [a user]({}) is attempting to verify themselves.
					This comment has been ignored and will have to be manually
					verified.
					""".format(comment.permalink))
					error_occurred = True
					break
				data["mail_count"] = int(data["mail_count"])
				data["letter_count"] = int(data["letter_count"])
				# Check if the COUNT_THRESHOLD_USER hasn't been exceeded.
				if data["mail_count"] + data["letter_count"] >= COUNT_THRESHOLD_USER:
					print("... "+colors.WARNING+"[WARNING]"+colors.ENDC+" High verification count for a single user. Ignoring and messaging mods.")
					message_mods("Verification count threshold exceeded", """
					It appears [a comment]({}) is attempting to verify a large
					email and/or letter count for a single user. This comment
					has been ignored and will have to be manually verified.
					""".format(comment.permalink))
					error_occurred = True
					break
				else:
					verifications.append(data)
		# Only verify the comment threshold id the user threshold wasn't exceeded.
		if not error_occurred:
			# Check the comment threshold.
			if total_verification_count(verifications) > COUNT_THRESHOLD_COMMENT:
				print("... "+colors.WARNING+"[WARNING]"+colors.ENDC+" High verification count for a single user. Ignoring and messaging mods.")
				message_mods("Verification count threshold exceeded", """
				It appears [a comment]({}) is attempting to verify a large
				email and/or letter count for a single user. This comment
				has been ignored and will have to be manually verified.
				""")
			else:
				# No errors, apply the verification counts.
				for data in verifications:
					global added_count
					if data["username"] not in added_count:
						added_count[data["username"]] = {"mail_count": 0, "letter_count": 0}
					added_count[data["username"]]["mail_count"] += data["mail_count"]
					added_count[data["username"]]["letter_count"] += data["letter_count"]
	return int(comments[-1].created_utc)


def get_flair_css_class(spreadsheet_row):
	for flair_css_class, requirement_fun in RANKS.items():
		if requirement_fun(spreadsheet_row):
			return flair_css_class


def recompute_spreadsheet_data(spreadsheet_data, added_count):
	""" Recomputes all values in the spreadsheet.
		Returns all flairs that changed during the recompute in the form
		[{username: string, flair: string}]
	"""
	changed_flairs = {}		# Will contain values {username: flairstring}
	for i, (username, mail_count, letter_count, flair_class) in enumerate(spreadsheet_data[1:], 1):
		if username[3:] in added_count:
			spreadsheet_data[i][1] = str(int(spreadsheet_data[i][1]) + added_count[username[3:]]["mail_count"])
			spreadsheet_data[i][2] = str(int(spreadsheet_data[i][2]) + added_count[username[3:]]["letter_count"])
			new_flair_class = get_flair_css_class(spreadsheet_data[i])
			# Only bother updating flairs that changed, paying special attention to n/a's that are non-existant flair classes.
			if new_flair_class != flair_class and not (not new_flair_class and flair_class == "n/a"):
				spreadsheet_data[i][3] = new_flair_class
				changed_flairs[username[3:]] = new_flair_class
			del added_count[username[3:]]
	# Append all users that haven't been handled yet to the end of the spreadsheet.
	for username, counts in added_count.items():
		new_flair_class = get_flair_css_class(spreadsheet_data[i])
		changed_flairs[username[3:]] = new_flair_class
		spreadsheet_data.append(["/u/"+username, counts["mail_count"], counts["letter_count"], new_flair_class])
	return changed_flairs


def update_flairs(changed_flairs):
	print("Updating flairs...")
	after = None

	flairs = []
	unknowns = []
	# Update existing flairs.
	for username, flair_css_class in changed_flairs.items():
		print("... /u/{} <- {}".format(username, flair_css_class))
		try:
			flair = r.get_flair(SUBREDDIT, username)
		except praw.errors.Forbidden:
			print(colors.ERROR+"[ERROR]"+colors.ENDC+" Could not retrieve flair information! Does the bot have mod privileges?".format(username))
			exit()
		if flair == None:
			print(colors.WARNING+"[WARNING]"+colors.ENDC+" /u/{} does not exist!".format(username))
			# TODO: do something more with the knowledge that the user doesn't exists?
			continue
		# The empty flair texts (None) need to be converted to empty strings.
		if flair["flair_css_class"] == None:
			flair["flair_text"] = ""
		if flair["flair_text"] == None:
			flair["flair_text"] = ""
		# Validate the flair classes with those defined.
		if flair["flair_css_class"] not in RANKS and flair["flair_css_class"] not in unknowns:
			unknowns.append(flair_css_class)
			print(colors.ERROR+"[ERROR]"+colors.ENDC+' Encountered an unknown CSS flair class "{}".'.format(flair_css_class))
		print("... Queuing flair {} for /u/{}".format(flair_css_class, flair["user"]))
		flair["flair_css_class"] = flair_css_class
		flairs.append(flair)
	# Only give a warning the first time an unknown class is encountered.
	if unknowns:
		input(colors.INPUT+"[INPUT NEEDED]"+colors.ENDC+" There were some unknown CSS flair classes!\n"
			"			   This probably means you forgot to define that class.\n"
			"			   Close the progam now and fix the error, or press ENTER\n"
			"			   to continue, ignoring any errors.")
	while flairs:
		# Update flairs.
		to_i = min(flairs.len, 100)
		r.set_flair_csv(SUBREDDIT, flairs[:to_i])
		print("Succesfully changed a section of the user's flairs")
		flairs = flairs[to_i:]
	print(colors.OK+"[SUCCESS]"+colors.ENDC+" Updated all user's flairs")


# Google Sheets API
SCOPES = "https://www.googleapis.com/auth/spreadsheets"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Google Sheets API Python Quickstart"
DATA_RANGE = FLAIR_SHEET+"!A:D"
# Global variables
SUBREDDIT = "penpals"
# Regular expressing expressing the syntax of the command.
RE_VERIFICATION_SYNTAX = re.compile(
		r"\A\s*"						# Any leading whitespace.
		# Reddit username, based on the Reddit source code.
		# First / is optional, as people seemed to forget it occasionally.
		# Entire /u/ part can be left out as well.
		r"(/?u/)?(?P<username>[\w\-]+)"
		r"[\s,_\-+]+"					# Delimiters.
		r"(?P<mail_count>[0-9]+)"
		r"[\s,_\-+]+"					# Delimiters.
		r"(?P<letter_count>[0-9+]+)"
		r"\s*\Z",						# Any trailing whitespace.
		re.UNICODE)


print("Authenticating with Docs API...", end="")
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
discoveryUrl = ("https://sheets.googleapis.com/$discovery/rest?version=v4")
service = discovery.build("sheets", "v4", http=http,
 						  discoveryServiceUrl=discoveryUrl)
print(colors.OK+" DONE"+colors.ENDC)

print("Authenticating with Reddit...", end="")
r = praw.Reddit("Python:PenpalsVerification by /u/BitwiseShift")
r.config.api_request_delay = 1.0
o = OAuth2Util.OAuth2Util(r)
o.refresh()
print(colors.OK+" DONE"+colors.ENDC)

# Keeps tracks of added counts per user.
added_count = {}		# Will contain count in the form {username: {mail_count: int, letter_count: int}}.

print("Getting spreadsheet data... ", end="")
prev_thread_id, prev_comment_time, spreadsheet_data = service.spreadsheets().values().batchGet(
		spreadsheetId=SPREADSHEET_ID, ranges=[PREV_THREAD_ID_CELL, PREV_COMMENT_TIME_CELL, DATA_RANGE]).execute()["valueRanges"]
# Set default values.
prev_thread_id = prev_thread_id.get("values", [[None]])[0][0]
prev_comment_time = int(prev_comment_time.get("values", [[0]])[0][0])
spreadsheet_data = spreadsheet_data.get("values", [])
# Pad rows, as Google leaves out empty rows at the end, i.e. empty css class strings.
spreadsheet_data = [row + [""]*(4-len(row)) for row in spreadsheet_data]

if prev_thread_id == None:
	print("No previous thread run found.")
	prev_comment_time = 0
	comment_time1 = None
else:
	print("Checking for new comments in previous thread run...")
	prev_thread = r.get_submission(submission_id=prev_thread_id)
	comment_time1 = process_comments(prev_thread, prev_comment_time)
	prev_comment_time = comment_time1 if comment_time1 else prev_comment_time

sticky = get_verification_thread()
# Check if the sticky was found.
if sticky:
	print("Verification thread found!")
else:
	print("Could not find new the verification thread!")
# Check if the sticky is different from the previous thread we processed.
if sticky.id == prev_thread_id:
	print("The verification thread hasn't changed!")
	comment_time2 = None
else:
	comment_time2 = process_comments(sticky, prev_comment_time)
	prev_comment_time = comment_time2 if comment_time2 else prev_comment_time
	prev_thread_id = sticky.id
# Only continue further if some new comments were found.
if comment_time1 or comment_time2:
	print("Handled all comments!")
	print("Computing new counts and flairs...", end="")
	changed_flairs = recompute_spreadsheet_data(spreadsheet_data, added_count)
	print(colors.OK+" DONE"+colors.ENDC)
	if changed_flairs:
		try:
			update_flairs(changed_flairs)
			print(colors.OK+" DONE"+colors.ENDC)
		except praw.errors.Forbidden:
			print(colors.ERROR+"\n[ERROR]"+colors.ENDC+" Unable to update the user's flairs! Does the bot have mod privileges?")
			exit()
	else:
		print("No flairs changed!")

	print("Writing persistence values to spreadsheet...", end="")
	data = [
		{"range": PREV_THREAD_ID_CELL, "values": [[prev_thread_id]]},
		{"range": PREV_COMMENT_TIME_CELL, "values": [[str(prev_comment_time)]]},
		{"range": DATA_RANGE, "values": spreadsheet_data}
	]
	service.spreadsheets().values().batchUpdate(
		body={"valueInputOption": "USER_ENTERED", "data": data},
		spreadsheetId=SPREADSHEET_ID).execute()
	print(colors.OK+" DONE"+colors.ENDC)
else:
	print("No new comments!")
print(colors.OK+"[SUCCESS]"+colors.ENDC+" Script finished!")
