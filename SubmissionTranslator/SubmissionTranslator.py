from sys import argv, exit
import urllib.request
import urllib.parse
import praw
import OAuth2Util
from bs4 import BeautifulSoup
import re
import langdetect
from iso639 import languages
from time import sleep, time
import socket
socket.setdefaulttimeout(10)	# Don't linger too long on pages that don't load


#
# Configuration
#

# Make sure Google translate supports your languages and enter its ISO 639-1
# code. See https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.
# On the right is the text to display for the translated language, on the left
# is its ISO 639-1 code.
DEFAULT_TRANSLATIONS = ["fr", "en", ]
TIME_BETWEEN_RUNS = 35		# The minimum time between runs is 35.
# Automatically translate incoming submissions. Only submission in a language
# given in AUTO_TRANSLATED_LANGUAGES will be translated. Auto-translate always
# translates to the default translations.
ENABLE_AUTO_TRANSLATE = True
# Languages that will be automatically translated, without having to be summoned.
# Any detected language that is not in this list will be translated to the
# default languages.
AUTO_TRANSLATE_IF_NOT = ["en", ]
# Allows the bot to be summoned to a thread with a command (see below).
ENABLE_SUMMONING = True
# The comment needed to summon the translator. The default syntax given will
# summon the bot "+/u/YOUR_USERNAME!". The {} in the below string gets replace
# by your username. To disable summoning
SUMMON_SYNTAX = "+/u/{}!"
# Setting this to True allows you to override the DEFAULT_TRANSLATIONS by adding
# a list of 2-letter language codes to the summon, e.g. "+/u/YOUR_USERNAME! en de"
# will translate to German and English instead of to the default translations.
# It will only work if the summon is followed by only the list of two letter
# codes. If what follows isn't that list, it will be ignored, e.g. if followed
# by a comment ""+/u/YOUR_USERNAME! I love this bot!" will translate to the
# defaults.
ALLOW_LANGUAGE_OVERRIDE = True
# This bot runs in specific subreddits. These subreddits have to be listed below.
# Only incoming submissions on and mentions coming from these subreddits will be
# processed.
ALLOWED_SUBREDDITS = ["BitwiseShiftTest", ]		# Without the /r/ part.



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

# Change some of the config to be more usable.
# Store the language codes with their full name.
DEFAULT_TRANSLATIONS = {lang_code: languages.get(part1=lang_code).name for lang_code in DEFAULT_TRANSLATIONS}
# Convert all subreddits to lowercase.
ALLOWED_SUBREDDITS = [sr.lower() for sr in ALLOWED_SUBREDDITS]

TRANSLATION_URL = "https://translate.google.com/translate?sl={lang_from}&tl={lang_to}&u={url}"
COMMENT_REGEX = re.compile("<!--.*-->")

print("Authenticating...")
r = praw.Reddit("Python:SubmissionTranslator by /u/BitwiseShift")
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)
SUMMON_SYNTAX = SUMMON_SYNTAX.format(r.user.name).lower()
before_mention = None
before_submission = {sr: None for sr in ALLOWED_SUBREDDITS}


def get_lang_codes(body):
	lang_codes = body[len(SUMMON_SYNTAX):].split()
	all_two = len(lang_codes) and all([len(code) == 2 for code in lang_codes])
	return set(lang_codes) if all_two else set()


def parse_mention(mention):
	""" Parse the summon. Check validity and generate translations list. """
	ret = {"is_valid": mention.body.lower().startswith(SUMMON_SYNTAX)}
	if not ret["is_valid"]:
		return ret
	ret["is_allowed"] = mention.subreddit.display_name.lower() in ALLOWED_SUBREDDITS or not ALLOWED_SUBREDDITS
	if not ret["is_allowed"]:
		return ret

	# Look for existing comments from the bot.
	comments = list(mention.replies)
	ret["commented_before"] = any(comment.author.name.lower() == r.user.name.lower() for comment in comments)

	poss_lang_codes = get_lang_codes(mention.body.lower())
	if ALLOW_LANGUAGE_OVERRIDE and poss_lang_codes:
		ret["translate_to"] = {}
		for code in poss_lang_codes:
			try:
				ret["translate_to"][code] = languages.get(part1=code).name
			except KeyError:
				pass
	else:
		ret["translate_to"] = DEFAULT_TRANSLATIONS
	return ret


def visible(element):
	# https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
	if element.parent.name in ["style", "script", "[document]", "head", "title"]:
		return False
	elif COMMENT_REGEX.match(str(element)):
		return False
	return True


def get_language(submission):
	if submission.is_self:
		pass
		print("... Text submission, using selftext.")
		text = submission.title+"\n"+submission.selftext
	else:
		print("... Link submission, retrieving URL.")
		try:
			f = urllib.request.urlopen(submission.url)
		except:
			print("... Something went wrong while getting the url, skipping.")
			return None
		html = f.read().decode(f.info().get_content_charset()).encode("ascii", errors="ignore")
		# Get all visible text in the document, to detect the language.
		soup = BeautifulSoup(html, 'html.parser')
		texts = soup.findAll(text=True)
		visible_texts = filter(visible, texts)
		text = "\n\n".join(visible_texts)
	print("... Detecting language")
	return langdetect.detect(text)


def generate_translation(text_lang, translate_to, url):
	print("... Posting translations")
	# Generate reply text for each translation language.
	replies = []

	for lang, lang_reply in translate_to.items():
		if lang != text_lang:
			replies.append(("[{lang_reply} version]("+TRANSLATION_URL+").").format(lang_reply=lang_reply, lang_from=text_lang, lang_to=lang, url=urllib.parse.quote(url)))
	return "\n\n".join(replies)


def commented_before_top_level(submission):
	comments = list(submission.comments)
	oldLen = 0
	newLen = len(comments)
	while newLen != oldLen:
		oldLen = newLen
		submission.replace_more_comments()
		comments = list(submission.comments)
		newLen = len(comments)
	is_mine = [comment.author.name == r.user.name for comment in comments]
	return any(is_mine)


def run_bot():
	if ENABLE_SUMMONING:
		global before_mention
		mentions = r.get_mentions(sort="New", params={"before": before_mention})
		first = True
		for mention in mentions:
			if first:				# Update the 'before'.
				first = False
				before_mention = mention.name
			print("+ New mention: ID={}".format(mention.id))
			print("... From: "+mention.permalink)
			info = parse_mention(mention)
			if not info["is_valid"]:
				print("... Invalid summon.")
			elif not info["is_allowed"]:
				print("... I'm not allowed to go into that subreddit!")
			elif info["commented_before"]:
				print("... I've replied to this mention before! Ignoring.")
			else:
				language = get_language(mention.submission)
				if language:
					reply_body = generate_translation(language, info["translate_to"], mention.submission.url)
					mention.reply(reply_body)
	if ENABLE_AUTO_TRANSLATE:
		global before_submission
		for subreddit in ALLOWED_SUBREDDITS:
			print("[/r/{}] Retrieving new submissions...".format(subreddit))
			submissions = r.get_subreddit(subreddit).get_new(sort="New", limit=1000, syntax="cloudsearch",
					params={"before": before_submission[subreddit]})
			for submission in submissions:
				if first:				# Update the 'before'.
					first = False
					before_submission[subreddit] = submission.name
				print("+ New submission: ID={}".format(submission.id))
				if not commented_before_top_level(submission):
					language = get_language(submission)
					if language and language not in AUTO_TRANSLATE_IF_NOT:
						reply_body = generate_translation(language, DEFAULT_TRANSLATIONS, submission.url)
						submission.add_comment(reply_body)
					else:
						print("... Does not meet translation criteria! Ignoring.")
				else:
					print("... Commented before! Ignoring.")



print("Starting bot.")
while True:
	print("Checking new mentions.")
	run_bot()
	print("Waiting {} seconds to recheck mentions.".format(TIME_BETWEEN_RUNS))
	sleep(max(35, TIME_BETWEEN_RUNS))
