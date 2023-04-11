# Fix Report of Group 23

## Phase 2 Deadline: 08Nov2020-23h59m)

- _Vulnerability 1: SQL Injection in search field in `/friends`_.
  - Root cause: The application would execute search queries with unprepared statements. Therefore, the attackers were able to inject SQL code in the search input field (in /friends), in order to obtain information on the database structure, tables' names and content.
  - Changes: Execute search queries with prepared statements, so that users cannot inject SQL code in the search input field.

- _Vulnerability 2: SQL Injection in `Name`, `New Password`, `About` and `Profile Photo` fields in `/profile`_.
  - Root cause: The application would update user's details, by executing an `UPDATE` type query with an unprepared statement.
  - Changes: Execute update queries with prepared statements, so that users cannot inject SQL code in any of the fields mentioned above.

- _Vulnerability 3: XSS on `/create_post`_.
  - Root cause: The application had the autoescape setting set to false so we could store some script on DB that the victim's browser would run later.
  - Changes: Change autoescape to true instead of false.

- _Vulnerability 4: SQL Injection in `Content` field in `/edit_post`_.
  - Root cause: The application would update a post's content, by executing an `UPDATE` type query with an unprepared statement.
  - Changes: Execute update queries with prepared statements, so that users cannot inject SQL code in the `Content` field.

- _Vulnerability 5: SQL Injection in `Username` field in `/login`_.
  - Root cause: The application would execute a `SELECT` type query with an unprepared statement, allowing users to login as any other user.
  - Changes: Execute login queries with prepared statements, so that users cannot inject SQL code in the `Username` field.

- _Vulnerability 6: XSS on `/profile`_.
  - Root cause: The application had the autoescape setting set to false so we could store some script on DB that the victim's browser would run later.
  - Changes: Change autoescape to true instead of false.

- _Vulnerability 7: Arbitrary SQL in `Username` field in `/register`_.
  - Root cause: The application would allow attackers to execute piggy-backed queries in the `Username` field, due to using unprepared statements.
  - Changes: Execute registration queries with prepared statements, so that users cannot run more than one query at the time.

- _Vulnerability 8: SQL Injection in `Content` field inside `/create_post`_.
  - Root cause: The application would update a post's content, by executing an `INSERT` type query with an unprepared statement.
  - Changes: Execute insert queries with prepared statements, so that users cannot inject SQL code in the `Content` field.

- _Vulnerability 9: Authorization bypass on `/edit_post`_.
  - Root cause: The application did not check whether the user editing the post was its author.
  - Changes: Added a check to refuse post edit attempts, made by any user, unless they are the post's author.

- _Vulnerability 10: SQL Injection and XSS in search field in `/friends`_.
  - Root cause: Since an attacker could perform arbitrary SQL SELECTS, they could inject JS code, performing a XSS.
  - Changes: Execute the query with prepared statements, making it impossible to inject JS code.
