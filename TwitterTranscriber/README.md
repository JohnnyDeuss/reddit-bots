# TwitterTranscriber
Transcribe Twitter links mentioned in a submission body. This script will only
run within whitelisted subreddits. The script keeps track of which submission it
processed last within each subreddit and will not load older submissions again,
even after closing and reopening the bot. To make it handle the same submission
again you'll need to delete the persistence file. However, even after the
persistence file has been deleted, the bot will refuse to post in a thread it
has already commented in.

Requested [here](https://www.reddit.com/r/RequestABot/comments/57zdih/request_a_bot_that_looks_for_twitter_links_in_the/)
by [/u/ExternalTangents](https://www.reddit.com/user/ExternalTangents).

## Installation instructions
Follow the instructions [here](https://github.com/JohnnyDeuss/reddit-bots).
To transform the twitter HTML to markdown, you'll need to install the
BeautifulSoup module. This can done by running the command
`pip install beautifulsoup4` in the command prompt.
