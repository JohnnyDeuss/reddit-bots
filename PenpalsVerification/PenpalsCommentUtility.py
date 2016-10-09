"""
	This script extracts the information needed for the PenpalsVerification
	script. Only set the "prev comment time" and "prev thread" values if you've
	already manually handled all comments before, and including, the comment
	whose permalink you'll copy. The permalink for this comment has to be
	entered below. You still need to have set up OAUTH before you can use this
	script.
"""
import praw
import OAuth2Util


COMMENT_PERMALINK = "https://www.reddit.com/r/penpals/comments/55bpim/monthly_verification_post_october_2016/d8fmtmo"


print("Authenticating with Reddit...")
r = praw.Reddit("Python:PenpalsVerificationUtility by /u/BitwiseShift")
o = OAuth2Util.OAuth2Util(r)
o.refresh()

s = r.get_submission(COMMENT_PERMALINK)
comment = s.comments[0]
print("prev_thread_id: "+s.id)
print("prev_comment_time: "+str(int(comment.created_utc)))
