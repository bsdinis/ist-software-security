# Vulnerability 7: Arbitrary SQL in /register

- Vulnerability: SQL Injection
- Where: `username` field on `/register`
- Impact: can execute multiple SQL statements

## Steps to reproduce

1. Navigate to the Register page
2. Close the username field with a `'` and insert your SQL payload, with `;` separating the statements. (eg: `'; drop table Posts -- `)


Note: there seems to be a WAF on the server controlling which payloads are valid (which seems a bit contrived, but we're not offering any creative commentary, this is a play). As such, only `DROP` payloads seem to be allowed.

[(POC)](vuln7.py)

## Impact

Zero from a privacy perspective. No user information is leaked.

Severe from a business perspective. Aside from shutting the website down while the DB is refreshed, unless there are recent backups the platform will have lost all users and interactions, which would probably be the end of it all.
