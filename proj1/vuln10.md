# Vulnerability 1: SQL Injection and XSS in search field in /friends

- Vulnerability: SQL Injection and XSS
- Where: `/friends` endpoint: `search bar` in search my friends bar
- Impact: Arbitrary `SELECT` queries on the database

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `/friends` endpoint
4. Search for `'and 1=0 union select '<script>alert(1)</script>', 2, 3, 4, 5 --  `
5. Notice the alert that pops up.

[(POC)](vuln10.py)

## Impact

Medium. This allows the attacker to create a script in a sql injection attack. However, this will only affect the logged in user.
