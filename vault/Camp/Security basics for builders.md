---
title: "Security basics for builders"
date: 2026-09-24
tags: [tech, code]
generated: 62948fded008
---
# Security basics for builders

The OWASP Top 10 is a ranked list of the most critical security risks to web applications, agreed by broad consensus. One habit protects even a small project: keeping secrets such as API keys out of the source code, and a code host can refuse a push that contains one. Reach for this topic before your first public repository, before you add a login, and whenever a key has to reach code that you share. And for an agent: never write a secret into a file that is committed, read it at runtime instead, and treat a blocked push from secret scanning as a real leak to fix, not a check to get around.

**History.** The OWASP Top 10 is "a standard awareness document for developers and web application security" that represents a broad consensus about the most critical security risks to web applications, and the most current release is the 2025 edition. Its 2025 list opens with A01 Broken Access Control, A02 Security Misconfiguration and A03 Software Supply Chain Failures, has A05 Injection and A07 Authentication Failures, and ends with A10 Mishandling of Exceptional Conditions. OWASP's Secrets Management Cheat Sheet notes that many organisations have secrets hardcoded within the source code in plaintext, and warns that environment variables are generally accessible to all processes and may be included in logs or system dumps. GitHub's push protection is a secret scanning feature designed to prevent hardcoded credentials from ever being pushed: rather than alerting after the fact, it blocks pushes that contain secrets before they reach the repository. NIST SP 800-218, published in February 2022, recommends the Secure Software Development Framework, a core set of high-level secure software development practices that can be integrated into each software development life cycle.

**Try in five minutes.** In a new folder, write .gitignore with the line .env, and app.py that reads API_KEY with os.environ.get and prints a clear message and exits when it is missing, with no key written in the file. Run python3 app.py once without the variable and once with API_KEY=test python3 app.py.

- Docs: [OWASP Top 10:2025](https://owasp.org/Top10/2025/), [OWASP Top Ten project page](https://owasp.org/www-project-top-ten/), [OWASP Cheat Sheet Series, Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [GitHub Docs, About push protection](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection), [Source: NIST SP 800-218, Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)
- Unlocks: [[Dependencies and the supply chain]]
- Shelf: Languages and code · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
