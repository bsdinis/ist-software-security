# Vulnerability 2: SQL Injection in /update_profile

- Vulnerability: SQL Injection
- Where: `/update_profile` endpoing: `Name`, `New Password`, `About` text input fields and on the `Profile Photo` name
- Impact: Arbitrary `UPDATE` queries on the database

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `/update_profile` endpoint
4. Edit the current name, new password, bio or new profile picture file name to to `',username='test',password='testpasswd' WHERE username='test' -- `
5. Write your current password on `Current Password` input text field
6. Logout
7. Login

[(POC)](vuln2.py)

## Impact

Severe. This allows the attacker to change passwords of other users and other details such as name, bio and profile image.
