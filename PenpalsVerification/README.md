# PenpalsVerification

Bot to automate the verification threads of [/r/penpals](https://www.reddit.com/r/penpals).
On top of accessing Reddit, it also communicates with Google sheets, where a
spreadsheet is stored with all verification information. Comments in the
verification thread have to be top-level comments and verifications must be on
their own line and have to format "/u/USERNAME - MAIL_COUNT - SNAIL_MAIL_COUNT".
The script is rather robust and will also recognize things like: "/u/user 1 2",
"/u/user-1 2", "/u/user,1,2". As long as each part is separated by either a
space a comma or a hyphen, it will be recognized. Additional whitespace is
ignored, e.g. "/u/user  -  1   ,   2" is still fine. Even using multiple
separators in a row will work, e.g. "/u/user --- 1 ,- 2".

The spreadsheet has to have a certain format as well. Its first four columns
have to contain the username, email count, letter count and flair, in this order.
The first row is expected to be headers. Each row in those first columns is
expected to have all four values present, that also includes not having rows
that have just n/a for the in the flair column, but no username or counts.

Start this script either after you've posted your next verification thread,
so that the script won't add verifications from the current thread that you've
already added manually, or enter the "previous comment time" and "previous
thread" values in your spreadsheet. These values are used by the script to keep
track of the last comment it processed. To find the values of these cells, you
can copy run [this script](https://github.com/JohnnyDeuss/reddit-bots/blob/master/PenpalsCommentUtility.py).

This script will message the mods under some circumstances, such as crashes
and suspect verification counts. Sometimes, this will not work, because a
user can't send messages without entering a captcha. This may depend on link
karma and other factors, though I'm not exactly sure what qualifies a person
to get captchas.

Requested [here](https://www.reddit.com/r/RequestABot/comments/562dre/mod_of_rpenpals_requesting_a_bot_to_assist_with/)
by [/u/wmeacham](https://www.reddit.com/user/wmeacham).

## Installation instructions
First, follow the instructions [here](https://github.com/JohnnyDeuss/reddit-bots).
This bot has to be scheduled to run every so often. It can also be run manually,
but should be done at least before a new verification thread is posted.

This bot uses Google's Sheets API. Follow the steps given [here](https://developers.google.com/sheets/quickstart/python) to get that
working.
