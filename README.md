# Fix Report of Group XX

## Phase 2 Deadline: 08Nov2020-23h59m)

_In this template we are using the SQL exercises' image running at `http://mustard.stt.rnl.tecnico.ulisboa.pt:12101/`_

- _Vulnerability 1: SQL Injection in login form allows to login as admin_.
  - Root cause: the source of this vulnerability was yada yada yada.
  - Changes: Fixed function `login` by doing yada yada yada.

- _Vulnerability 2: SQL Injection in Bio of Profile allows to update value of `jackpot_val`_.
  - Root cause: the source of this vulnerability was yada yada yada.
  - Changes: Fixed function `edit_profile` by doing yada yada yada.

## Notes

- __Use the same numbering that you used for Phase 1.__
- Edit the files directly so that in the final commit there are no vulnerabilities in your application.
- Refer in each commit which vulnerability is fixed.
- Test your own PoCs against the fixed application in order to verify that the vulnerabilities are no longer present (the `assert`s in the end should now fail).
- If you find vulnerabilities that you did not exploit, you may also fix those.
