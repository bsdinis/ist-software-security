# Vulnerability 2: XSS in /create_post

- Vulnerability: XSS
- Where: `Content` input text field in /create_post.
- Impact: Users can create scripts that will run once other users access their main page (if the post is visible to them).

## Steps to reproduce

1. Register
2. Login
3. Navigate to the `'/create_post'` endpoint
4. Insert the following text in the `Content` text field: `<script window.location="https://www.google.com"></script>`
5. Set visibility to `Public`
6. Access the main page by pressing `FaceFive` at the top left corner of the page

[(POC)](vuln3.py)

## Impact

Severe. This allows the attacker to redirect users to vulnerable websites which allow the attacker to get information on the
victims, including, but not limited to their cookies.