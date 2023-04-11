# Vulnerability 2: SQL Injection in /profile

- Vulnerability: SQL Injection
- Where: `/profile` endpoing: `Name`, `New Password`, `About` text input fields and on the `Profile Photo` name
- Impact: Arbitrary `UPDATE` queries on the database

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `/profile` endpoint
4. Edit the current name, new password, bio or new profile picture file name to to `',username='test',password='testpasswd' WHERE username='test' -- `
5. Write your current password on `Current Password` input text field
6. Logout
7. Login

Note: It is also possible to change the current user's name to `<script>alert(5);</script>',username='administrator', password='123' WHERE username='administrator' -- ` for an example, where the administrator's account `Name` field will be changed to a script, that will run once the name
is displayed on the website (usually when that person creates new posts or sends friend requests). This is similar to vuln6, but it is not possible to know
which user was at fault.

[(POC)](vuln2.py)

## Impact

Severe. This allows the attacker to change passwords of other users and other details such as name, bio and profile image.
