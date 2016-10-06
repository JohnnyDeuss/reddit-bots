# reddit-bots
This repository contains a collection of scripts and bots for Reddit. These
scripts were requested at
[/r/RequestABot](https://www.reddit.com/r/RequestABot). At the top of each
script, there will be a description of the task it performs and by whom and
where it was requested.

## Running the bots
To run these bots, your computer needs to have a number of things installed.
Each script is written in the Python 3 programming language and uses a number of
modules, which extend Python with features to make scripts easier to
write. If at any point you get stuck, try looking through
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

### Configuring the script
Each script is divided into four sections. From top to bottom, there is a large
block of text, explaining what the script is, followed by a list of module
imports, followed by the configuration, and finally followed by the actual bot
code. For nearly every script, you'll have to fill in the configuration section
to get it to work. There will be an example configuration already there, along
with comment text explaining what each option does.

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

### Running/scheduling
Some bots must be scheduled to run every once in a while. These are bots that
run multiple times, but it doesn't necessarily matter exactly when it is run,
e.g. deleting old posts, posts don't have to be deleted the second they reach
the deletion age. The block of text at the top of each script will tell you
whether the script needs to be scheduled ot not. To set up scheduling for a bot,
follow the instructions in the scheduling section of
[the sticky](https://www.reddit.com/r/RequestABot/comments/3d3iss/a_comprehensive_guide_to_running_your_bot_that/)

If the script you're using runs continually or just once, and does not need to
be scheduled, you can run it by double clicking it. If that doesn't work, you
can try entering `python c:/Path/to/script.py` in the command prompt.

## Disclaimer
I'm making these bots in my spare time. I will do my best to test them as
thoroughly as I can, but errors slip in, especially on new scripts. It is your
responsibility to verify that a script and its configuration work as you expect
it to by running it on a test subreddit before running them on your main
subreddit. If you don't bother testing it, you may end up kicking yourself for
it.
