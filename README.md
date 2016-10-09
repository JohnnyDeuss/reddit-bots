# reddit-bots
This repository contains a collection of scripts and bots for Reddit. These
scripts were requested at
[/r/RequestABot](https://www.reddit.com/r/RequestABot). Each script is
accompanied with a README.md file that explains what the script does, who
requested it and any additional install instructions that may be necessary for
that script. Some scripts may also be accompanied by .cfg files, which contain
a possible configuration for that script, along with an explanation of what that
that configuration will do.

## Running the scripts
To run these scripts, your computer needs to have a number of things installed.
Each script is written in the Python 3 programming language and uses a number of
modules, which extend Python with features to make scripts easier to write. If
at any point you get stuck, try looking through
[the sticky](https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/)
on [/r/RequestABot](https://www.reddit.com/r/RequestABot) or in the comment
section of the original request. If all else fails, feel free to contact me
directly, either through Github or as
[/u/BitwiseShift](https://www.reddit.com/user/bitwiseshift) on Reddit.

### Python 3
***How do I get it?*** Install [Python 3](https://www.python.org/downloads/).

***What is it?*** Python 3 is an interpreted programming language, which means
your computer needs to have an interpreter to understand the code. This is
similar to how you need to install the Java Virtual Machine to run Java
programs. Python is extremely good at writing powerful programs in few lines of
code. At the same time, Python is very secure, since it runs directly on the
source code, meaning that the code can be verified by third parties. This is why
[/r/RequestABot](https://www.reddit.com/r/RequestABot) doesn't allow .exe's
and .jar's, because they may contain malicious code while being difficult to
verify.

### PRAW
***How do I get it?*** Install the Python Reddit Api Wrapper (PRAW) module. You
can do this by running `pip install praw` in the command prompt/terminal.

***What is it?*** This module allows Python to make requests to the Reddit API
in a couple of lines of code. It also automatically enforces the Reddit
bottiquette rules.

### OAuth2Util
***How do I get it?*** Install the OAuth2Util module. You can install this by
running `pip install praw-oauth2util`. For this module to work, you'll need to
set up OAuth authentication. First, copy the configuration file found
[here](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md#config)
and save it as `oauth.ini` in the same directory as the script. Now follow the
instructions in the OAuth section of [the sticky](https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/).
At the end of these instructions, you'll have an app key and secret, these need
to be filled in into the `app_key` and `app_secret` fields of the `oauth.ini`
configuration file.

***What is it?*** OAuth2Util is a module designed for PRAW. It handles OAuth
verification in a single line of code. OAuth is a type of authorization that
grants a script access to an account without requiring a password. It also
allows you to restrict which information a script can access.

### Other modules
Sometimes, a script will require additional modules to be installed. Normally,
there will be information on what these are and how to get them in the block of
text at the top of the script. If you ever get an `ImportError` while running
the script, it means you're missing a module. Often, you can install these
missing modules by running `pip install {MODULE_NAME}`. If that doesn't work,
try Googling "Python install {MODULE_NAME}".

### Configuring the script
Each script is divided into four sections. From top to bottom, there is a large
block of text, explaining what the script is, followed by a list of module
imports, followed by the configuration, and finally followed by the actual bot
code. Nearly every script will need to give a configuration for it to work.

There are two ways to enter a configuration. The first way is to fill in the
configuration section. This is the easiest method, but is only useful if you
plan on using only one configuration. If you want to use multiple
configurations, e.g. one configuration per subreddit you're running the script
on, you should load the configuration from a config file. To do this, copy the
configuration section of the script into its own file. An example config file
for [`OldCommentRemover.py`](https://github.com/JohnnyDeuss/reddit-bots/blob/master/OldCommentRemover/OldCommentRemover.py) is given [here](https://github.com/JohnnyDeuss/reddit-bots/blob/master/OldCommentRemover/remove_all.cfg).

### Running/scheduling
If you're not using a config file, you can usually run a script by double
clicking it. Otherwise, you can enter `python3 c:/Path/to/script.py [config_file]`
in the command prompt to run the script. Here, `config_file` is an optional
value that points to the config file you want it to use, e.g.
`python3 OldCommentRemover.py remove_all.cfg` will run the [`OldCommentRemover.py`](https://github.com/JohnnyDeuss/reddit-bots/blob/master/OldCommentRemover/OldCommentRemover.py)
script with the [`remove_all.cfg`](https://github.com/JohnnyDeuss/reddit-bots/blob/master/OldCommentRemover/remove_all.cfg) config file.

Some bots must be scheduled to run every once in a while. These are bots that
run multiple times, but it doesn't necessarily matter exactly when it is run,
e.g. deleting old posts, posts don't have to be deleted the second they reach
the deletion age. The block of text at the top of each script will tell you
whether the script needs to be scheduled or not. To set up scheduling for a bot,
follow the instructions in the scheduling section of
[the sticky](https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/)

## Disclaimer
I'm making these bots in my spare time. I will do my best to test them as
thoroughly as I can, but errors slip in, especially on new scripts. It is your
responsibility to verify that a script and its configuration work as you expect
it to by running it on a test subreddit before running them on your main
subreddit. If you don't bother testing it, you may end up kicking yourself for
it.
