# Project Report of Group 23

Group Image available [here](http://68e327e55ef49b75ccd392ac75311e4ec6965f6e8fe813b4d94bf660ff18.project.ssof.rnl.tecnico.ulisboa.pt/)

- Vulnerability 1: SQL Injection in search field in /friends [(link)](vuln1.md)
- Vulnerability 2: SQL Injection in /profile [(link)](vuln2.md)
- Vulnerability 3: XSS in /create_post [(link)](vuln3.md)
- Vulnerability 4: SQL Injection in /edit_post [(link)](vuln4.md)
- Vulnerability 5: SQL Injection in /login [(link)](vuln5.md)
- Vulnerability 6: XSS in /profile [(link)](vuln6.md)
- Vulnerability 7: Arbitrary SQL in /register [(link)](vuln7.md)
- Vulnerability 8: SQL leak inside /create_post [(link)](vuln8.md)
- Vulnerability 9: Authorization bypass on /edit_post [(link)](vuln9.md)
- Vulnerability 10: SQL Injection and XSS in search field in /friends [(link)](vuln10.md)

## Notes

- Each reported vulnerability should have a PoC (a script)
  - In case you cannot script it, detail it as much as possible
- Each PoC should receive as 1st argument the http address (and port) of the server.
- For the case of XSS, if you need to receive the result in an external server, that address (and port) should be provided as the 2nd argument.
- Your PoC should set up all the needed values. Your PoC in the end should have an `assert` that validates your claims.
