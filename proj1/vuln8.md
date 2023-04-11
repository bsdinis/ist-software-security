# Vulnerability 8: SQL leak inside `/create_post`

- Vulnerability: SQL Injection
- Where: `Content` field on `/create_post`
- Impact: can leak contents one by one

Note: there is a similar vulnerability on several endpoints:
 - `/login` (username field)
 - `/register` (username field)
 - `/profile` (Name/About field): although it cannot reference the Users table since it is changing it.

## Steps to reproduce

1. Login as a user
2. Create a post with the following content:
```
' or updatexml(0,concat(0x7e,(select password from Users where username = 'administrator')),0) or '
```
3. Read the selected value in the error

Explanation: this tries to run a SQL function (`updatexml`), using a `select` subquery which gets the administrator's password. The error contains that password.

[(POC)](vuln8.py)

## Impact

Medium. Although this does give attackers access to the DB, that access is relatively blinded (ie: one has to guess a lot).
