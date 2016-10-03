"""
	This bot can be summoned to translate a submission. It does not use Google's autodetection to
	determine the language of the document, as you'd need an API key for that, which is to difficult
	for laymen and isn't free. It does use Google translate through a the Google translate page
	translator instead of the translate API.
	
	Uses the langdetect module to detect language. Install it with 'pip install langdetect'.
	Uses the iso-639 module to detect know what language code corresponds to which language. Install
	it with 'pip install iso-639'.
	
	Additional features to check for top level comments and multiple replies in the same thread may
	be necessary.
	
	Requested by /u/frost_biten.
	https://www.reddit.com/r/RequestABot/comments/555gew/a_translation_bot_for_rhabs/
	
	DISCLAIMER:
	This bot works without being a moderator, but you should never run a bot like this, that
	responds to every submission, without being a moderator of the subreddit it is running in or
	having the moderators' permission. Doing so anyway makes you a dick. No, no. No arguing, it
	makes you a dick and may get you and your bot banned.
"""
import urllib.request
import urllib.parse
import praw
import OAuth2Util
from bs4 import BeautifulSoup
import re
import langdetect
from iso639 import languages
from time import sleep
import socket
socket.setdefaulttimeout(10)		# Don't linger too long on pages that don't load


#
# Configuration
#

# Make sure Google translate supports your languages and enter its ISO 639-1 code.
# See https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# On the right is the text to display for the translated language, on the left is its ISO 639-1 code.
DEFAULT_TRANSLATIONS = ["fr", "en"]
TIME_BETWEEN_RUNS = 35		# The minimum time between runs is 35.
# The comment needed to summon the translator. The default syntax given will summon the bot
# "+/u/YOUR_USERNAME!". The {} in the below string gets replace by your username.
SUMMON_SYNTAX = "+/u/{}!"
# Setting this to True allows you to override the DEFAULT_TRANSLATIONS by adding a list of 2-letter
# language codes to the summon, e.g. "+/u/YOUR_USERNAME! en de" will translate to German and English
# instead of to the default translations. It will only work if the summon is followed by only the
# list of two letter codes. If what follows isn't that list, it will be ignored, e.g. if followed by
# a comment ""+/u/YOUR_USERNAME! I love this bot!" will translate to the defaults.
ALLOW_LANGUAGE_OVERRIDE = True
#  by putting them in this list. If the list is empty, it will repond to mentions originating from
# This bot does not run in a specific subreddit, you can limit in which subreddits this bot will act
# all subreddits.
ALLOWED_SUBREDDITS = ["BitwiseShiftTest", "Test", ]		# Without the /r/ part.

#
# Actual bot
#

# Change some of the config to be more usable.
# Store the language codes with their full name.
DEFAULT_TRANSLATIONS = {lang_code: languages.get(part1=lang_code).name for lang_code in DEFAULT_TRANSLATIONS}
# Convert all subreddits to lowercase.
ALLOWED_SUBREDDITS = [sr.lower() for sr in ALLOWED_SUBREDDITS]

TRANSLATION_URL = "https://translate.google.com/translate?sl={lang_from}&tl={lang_to}&u={url}"
COMMENT_REGEX = re.compile("<!--.*-->")

print("Authenticating...")
r = praw.Reddit('Python:SubmissionTranslator by /u/BitwiseShift')
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)
SUMMON_SYNTAX.format(r.user.name)
before = None


def get_lang_codes(body):
	lang_codes = body[len(SUMMON_SYNTAX):].split()
	all_two = len(lang_codes) and all([len(code) == 2 for code in lang_codes])
	return set(lang_codes) if all_two else set()


def parse_mention(mention):
	""" Parse the summon. Check validity and generate translations list. """
	ret = {"is_valid": mention.body.startswith(SUMMON_SYNTAX)}
	if not ret["is_valid"]:
		return ret
	ret["is_allowed"] = mention.subreddit.display_name.lower() in ALLOWED_SUBREDDITS or not ALLOWED_SUBREDDITS
	if not ret["is_allowed"]:
		return ret
	
	# Look for existing comments from the bot.
	comments = list(mention.replies)
	ret["commented_before"] = any(comment.author.name.lower() == r.user.name.lower() for comment in comments)

	poss_lang_codes = get_lang_codes(mention.body)
	if poss_lang_codes:
		ret["translate_to"] = {}
		for code in poss_lang_codes:
			try:
				ret["translate_to"][code] = languages.get(part1=code).name
			except KeyError:
				pass
	else:
		ret["translate_to"] = DEFAULT_TRANSLATIONS
	
	pprint(ret["translate_to"])
	return ret
	

def visible(element):
	# https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif COMMENT_REGEX.match(str(element)):
        return False
    return True

	
def run_bot():
	global before
	first = True
	
	mentions = r.get_mentions(sort="New", params={"before": before})	
	for mention in mentions:
		if first:				# Update the 'before'.
			first = False
			before = mention.name
		
		print("+ New mention: ID={}".format(mention.id))
		print("... From: "+mention.permalink)
		info = parse_mention(mention)
		
		if not info["is_valid"]:
			print("... Invalid summon.")
			continue
		if not info["is_allowed"]:
			print("... I'm not allowed to go into that subreddit!")
			continue
		if info["commented_before"]:
			print("... I've replied to this mention before! Ignoring.")
			continue
		submission = mention.submission
		if submission.is_self:
			pass
			print("... Text submission, using selftext")
			text = submission.title+"\n"+submission.selftext
		else:
			print("... Link submission, retrieving URL")
			try:
				f = urllib.request.urlopen(submission.url)
			except:
				print("... Something went wrong while getting the url, skipping.")
				continue
			html = f.read().decode()
			# Get all visible text in the document, to detect the language.
			soup = BeautifulSoup(html, 'html.parser')
			texts = soup.findAll(text=True)
			visible_texts = filter(visible, texts)
			text = "\n\n".join(visible_texts)
		print("... Detecting language")
		text_lang = langdetect.detect(text)
		
		print("... Posting translations")
		# Generate reply text for each translation language.
		replies = []
		
		for lang, lang_reply in info["translate_to"].items():
			if lang != text_lang:
				replies.append(("[{lang_reply} version]("+TRANSLATION_URL+").").format(lang_reply=lang_reply, lang_from=text_lang, lang_to=lang, url=urllib.parse.quote(submission.url)))
		reply_body = "\n\n".join(replies)
		mention.reply(reply_body)
		

print("Starting bot.")
while True:
	print("Checking new mentions.")
	run_bot()
	print("Waiting {} seconds to recheck mentions.".format(TIME_BETWEEN_RUNS))
	sleep(max(35, TIME_BETWEEN_RUNS))
