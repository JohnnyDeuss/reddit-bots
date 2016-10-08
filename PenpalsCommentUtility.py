"""
	This script extract the information needed for the PenpalsVerification
	script. All you need to do is enter the permalink below and run the script.
	You still need to have set up OAUTH before you can use this script.
"""
import praw
import OAuth2Util


COMMENT_PERMALINK = "https://www.reddit.com/r/penpals/comments/55bpim/monthly_verification_post_october_2016/d8fmtmo"


print("Authenticating with Reddit...")
r = praw.Reddit("Python:PenpalsVerification by /u/BitwiseShift")
o = OAuth2Util.OAuth2Util(r)
o.refresh()

s = r.get_submission(COMMENT_PERMALINK)
comment = s.comments[0]
print("prev_thread_id: "+s.id)
print("prev_comment_time: "+str(int(comment.created_utc)))
