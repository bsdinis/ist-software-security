# Vulnerability 4: SQL Injection in /edit_post

- Vulnerability: SQL Injection
- Where: `Content` field in `/edit_post`
- Impact: Allows attackers to change any post's visibility and content (created by any users)

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `/create_post` endpoint
4. Write text in `Content` field
5. Set visibility to `Public`
6. Press the `Create Post` button
7. Press the `Edit this post` button on the main page, under the post you created
8. Enter the following text in the `Content` field: `',id=1,type='Public',content='ThisIsNewContent' WHERE id=1 -- `
9. Press the `Create Post` button
10. Notice that you edited another post, that shows at the top of the page with the new content

[(POC)](vuln4.py)

## Impact

Severe. This allows the attacker to change any post's visibility and content (created by any users).
