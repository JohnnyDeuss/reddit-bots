"""
	This will translate all submissions posted while the bot is running to other languages. It does
	not use Google's autodetection to determine the language of the document, as you'd need an API
	key for that, which is to difficult for laymen and isn't free. It does use Google translate
	through a the Google translate page translator instead of the translate API.
	
	Uses the langdetect module to detect language. Install it with 'pip install langdetect'.
	
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
import socket
socket.setdefaulttimeout(10)		# Don't linger too long on pages that don't load
from time import sleep, time


#
# Configuration
#

# Make sure Google translate supports you languages and enter its ISO 639-1 code.
# See https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# On the right is the text to display for the translated language, on the left is its ISO 639-1 code.
TRANSLATE_TO = {
	"fr": "Version Française",
	"en": "English version",
}
USERNAME = "BitwiseShift"
SUBREDDIT = "BitwiseShiftTest"			# Subreddit name, without the /r/ part.
TIME_BETWEEN_RUNS = 35					# In number of seconds, the minimum is 35 seconds


#
# Actual bot
#

TRANSLATION_URL = "https://translate.google.com/translate?sl={lang_from}&tl={lang_to}&u={url}"
COMMENT_REGEX = re.compile("'<!--.*-->")
print("Authenticating...")
r = praw.Reddit('Python:SubmissionTranslator by /u/BitwiseShift, run by {}'.format(USERNAME))
from pprint import pprint
r.config.permalink_url = "http://www.reddit.com/"		# debug
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

t_from = None
t_to = int(time()) + 8*60*60 - 1		# -1 will be undone in iteration.


def visible(element):
	# https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif COMMENT_REGEX.match(str(element)):
        return False
    return True

	
def run_bot():
	global t_to
	t_from = t_to + 1
	t_to = int(time()) + 8*60*60
	search_string = "timestamp:{}..{}".format(t_from, t_to)
	print("Retrieving new submissions...")
	submissions = r.search(search_string, subreddit=SUBREDDIT, sort="New", limit=1000, syntax="cloudsearch")
	for submission in submissions:
		print("+ New submission: ID={}".format(submission.id))
		if submission.is_self:
			pass
			print("... Text submission, using selftext")
			text = submission.title+"\n"+submission.selftext
		else:
			print("... Link submission, retrieving URL")
			try:
				f = urllib.request.urlopen(submission.url)
			except:
				print("... Something went wring while getting the url, skipping.")
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
		for lang, lang_reply in TRANSLATE_TO.items():
			if lang != text_lang:
				replies.append(("[{lang_reply}]("+TRANSLATION_URL+").").format(lang_reply=lang_reply, lang_from=text_lang, lang_to=lang, url=urllib.parse.quote(submission.url)))
		reply_body = "\n\n".join(replies)
		submission.add_comment(reply_body)


while True:
	print("Waiting {} seconds for incoming submissions.".format(TIME_BETWEEN_RUNS))
	sleep(max(35,TIME_BETWEEN_RUNS))
	run_bot()
