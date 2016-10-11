# SubmissionTranslator

This bot can be summoned to translate a submission. It does not use Google's
autodetection to determine the language of the document, as you'd need an API
key for that, which is to difficult for laymen and isn't free. It does use
Google translate through the Google translate page translator instead of the
translate API.

Requested [here](https://www.reddit.com/r/RequestABot/comments/555gew/a_translation_bot_for_rhabs/)
by [/u/frost_biten](https://www.reddit.com/user/frost_biten).

## How to summon it

The SubmissionTranslator has two different approaches to translating. It can
automatically post translations if the submission's language is detected to not
be one of the preferred languages (usually English). The second way it can post
a translation is by summoning it using `+/u/BotName!` (at least that is the
default), in which case the bot will translate to all the default languages
configured. Summoning works in any comment, not just top level comments.
Translating to arbitrary languages is possible by appending the language's
ISO 639 two letter code to the summon, e.g. `+/u/BotName! en fr de nl` will
translate to English, French, German and Dutch. Each of these methods can be
enabled/disabled in the configuration.

## Installation instructions

Follow the instructions [here](https://github.com/JohnnyDeuss/reddit-bots#reddit-bots).
This script uses the `langdetect` module to detect languages. Install it by
running `pip install langdetect` in the command prompt. It also uses the
`iso-639` module to know which language code corresponds to which language.
Install it with running `pip install iso-639`. It also uses the `regex` module
for powerful regular expression matching, which is used to more flexibly parse
mentions. Install it by running `pip install regex`.
