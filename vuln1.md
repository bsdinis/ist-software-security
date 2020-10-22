# Vulnerability 1: SQL Injection in login form allows to login as admin

- Vulnerability: SQL Injection
- Where: `username` in login form
- Impact: Allows access to `admin`'s profile and retrieve the flag for the challenge

## Steps to reproduce

1. Insert `username` = `admin' -- ` and `password` = `any` in login form
2. Access `Profile (admin)`
3. Flag is in field `Bio`

[(POC)](vuln1.py)
