# MassSquatterMessager

This script will investigate a mass squater's subreddits and figure out which of them are
username subreddits. Every username subreddit will be verified to make sure that the user it is
named after isn't also a moderator of it. Every user who's username subreddit is being squated
will be messaged. This scrapes the squatter's user page to find the subreddits he moderated, as
Reddit doesn't have an API call for this.

For some users, sending messages requires the solving of a captcha, this is
not supported by the script at the moment.

Requested [here](https://www.reddit.com/r/RequestABot/comments/55dlxk/need_a_bot_to_send_mass_pms_to_users_matching_a/)
by [/u/Stuart98](https://www.reddit.com/user/Stuart98).

## Installation instructions
First, follow the instructions [here](https://github.com/JohnnyDeuss/reddit-bots).
For the scraping of HTML, you'll need to install the BeautifulSoup module. This
can done by running the command `pip install beautifulsoup4` in the command
prompt.

## Disclaimer
This script was purposefully made to message only people whose username
subreddit is being squatted by a mass squatter. This bot could be altered to
mass message anyone. Don't do this unless you have a damn good reason. Don't be
a dick. Mass messaging is spam if there isn't a good reason and spamming gets
you banned. ***Don't be a dick***.
