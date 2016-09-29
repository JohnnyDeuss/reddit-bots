# reddit-bots
## Running the bots
Follow [the instructions in the sticky thread](https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/)
on [/r/RequestABot](https://www.reddit.com/r/RequestABot).
All my scripts require OAuth2Util, so be sure to follow the step that install it.
To use OAuth2Util, which is a way to authenticate with Reddit without using a password, you'll also need a to add
a configuration file called `oauth.ini` in the same directory as the bot script.
You can get the configuration file [here](https://github.com/SmBe19/praw-OAuth2Util/tree/master/OAuth2Util#config),
but you'll still need to fill in the `app_key` and `app_secret` fields.
The steps you need to follow to get the values for these fields are given in [the sticky thread](https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/) under the OAuth section.

If you ever get an ImportError, check the block of text at the top of the script to see if there are any modules you need
to install to get the script to work. If there is no information there you can always Google how to install it by Googling
"python install modulename". Usually, the way to install a module is by running "pip install modulename" in the command prompt.
If you can't get it work, you can always ask me.
