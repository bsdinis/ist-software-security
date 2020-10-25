# Vulnerability 4: SQL Injection in /login

- Vulnerability: SQL Injection
- Where: `Username` field in `/login` form
- Impact: Allows attackers to login as any user, if they know a username

## Steps to reproduce

1. Go to the login page
2. Insert the following text in the `Username` field: `administrator' -- `
3. Insert a random password in the password field
4. Notice that you are logged in as the `administrator` user

[(POC)](vuln5.py)

## Impact

Severe. This allows the attacker to login with any user account, as long as he knows the account's username.
