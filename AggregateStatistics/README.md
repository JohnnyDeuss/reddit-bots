# AggregateStatistics

This will aggregate flair statistics over the newest submissions returned by a
search. The generated statistics are total/avg upvotes, estimated total/avg
downvotes, estimated total/avg votes and average upvote percentage. The bot can
be altered to look for other kind of post by changing the search request.

This bot is extremely slow because it has to make a lot of requests. Getting
downvote count is very difficult, intentionally so. Even after the slow process
of gathering them, the result is still an estimate, as it is derived from the
`upvote_ratio` field. An upvote ratio of 71% may be given, while only 1 upvote
is given. It is impossible to get 71% upvote ratio with only 1 upvote. 71% can
be reached with 5 upvotes and 2 downvotes, so the upvote count is likely behind.
Don't run this bot perpetually, as it makes way too many requests for little
amounts of data.

Request posted [here](https://www.reddit.com/r/RequestABot/comments/54t6f3/bot_that_aggregates_upvote_percentage_of_threads/) by [/u/Ace_InTheSleeve](https://www.reddit.com/user/Ace_InTheSleeve).

## Installation instructions
Follow the instructions [here](https://github.com/JohnnyDeuss/reddit-bots).
