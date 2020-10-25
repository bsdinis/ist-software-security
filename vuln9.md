# Vulnerability 9: Authorization bypass on /edit_post

- Vulnerability: Authorization bypass on /edit_post
- Where: `id` parameter on `/edit_post` query
- Impact: allows any users to change any post present in the database

## Steps to reproduce

1. Login as a user.
2. Access the endpoint `/edit_post?id=2` to edit the post with id=2.
3. Change the post content and/or visibilty and press `Create Post` button.
4. View the post with the new content.

[(POC)](vuln9.py)

## Impact

Medium. This allows anyone to change any post present in the database (content and/or visibility).
