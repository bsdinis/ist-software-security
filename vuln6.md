# Vulnerability 6: XSS in /profile

- Vulnerability: XSS
- Where: `/profile` endpoint: User details form.
- Impact: Users can create scripts and insert them into their name/about/photo name. Once their profile is displayed, the script will run (including when they create a new post for an example).

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `/profile` endpoint
4. Insert the following text in the `Name` text field: `<script>alert(5);</script>`
5. Enter the current password for your user
6. Press the `Update profile` button
7. Navigate to the `/create_post` endpoint
8. Create a new post with any content
9. Logout
10. Register a new user
11. Navigate to the main page (`/`) and notice the alert being displayed.

[(POC)](vuln6.py)

Note: Similarly, instead of creating a post, a malicious user might simply send a friend request to the target. In addition to this, it is possible to upload
a new image file with the following name `"><body onload=alert(5)>` (It does not work on Windows). This will also run a script everytime the user profile picture is displayed.

## Impact

Medium. This allows the attacker to redirect users to vulnerable websites which allow the attacker to get information on the
victims, including, but not limited to their cookies.
