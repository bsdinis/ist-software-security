# Vulnerability 6: XSS in /profile

- Vulnerability: XSS
- Where: `Name` input field in user details form.
- Impact: Users can create scripts and insert them into their name. Once their name is displayed, the script will run (including when they create a new post for an example).

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `'/profile'` endpoint
4. Insert the following text in the `Name` text field: `<script>alert(5);</script>`
5. Enter the current password for your user
6. Press the `Update profile` button
7. Navigate to the `'/create_post'` endpoint
8. Create a new post with any content
9. Navigate to the main page (`'/'`) and notice the alert being displayed.

[(POC)](vuln6.py)

## Impact

Severe. This allows the attacker to redirect users to vulnerable websites which allow the attacker to get information on the
victims, including, but not limited to their cookies.