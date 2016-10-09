# SubmissionTranslator

This bot can be summoned to translate a submission. It does not use Google's autodetection to
determine the language of the document, as you'd need an API key for that, which is to difficult
for laymen and isn't free. It does use Google translate through a the Google translate page
translator instead of the translate API.

Additional features to check for top level comments and multiple replies in the same thread may
be necessary.

Requested [here](https://www.reddit.com/r/RequestABot/comments/555gew/a_translation_bot_for_rhabs/)
by [/u/frost_biten](https://www.reddit.com/user/frost_biten).

## Installation instructions

Follow the instructions [here](https://github.com/JohnnyDeuss/reddit-bots#reddit-bots).
This script uses the `langdetect` module to detect languages. Install it by
running `pip install langdetect` in the command prompt. It also uses the
`iso-639` module to know which language code corresponds to which language.
Install it with running `pip install iso-639`.
