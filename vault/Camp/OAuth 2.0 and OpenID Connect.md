---
title: "OAuth 2.0 and OpenID Connect"
date: 2026-09-24
tags: [tech, net]
generated: 5fc662643586
---
# OAuth 2.0 and OpenID Connect

OAuth 2.0 lets an application get limited access to an HTTP service, either for a user who approves it at an authorization server or on the application's own behalf, and the application receives an access token. OpenID Connect is an identity layer on top of it that lets the application verify who the user is. Reach for this topic when you add "Sign in with" to an app, when a tool asks you to authorize it, or when you have to choose which OAuth flow a client should use. And for an agent: use the authorization code grant with PKCE and the S256 method, never the resource owner password credentials grant, and not the implicit grant, which RFC 9700 says clients SHOULD NOT use.

**History.** RFC 6749, published by the IETF in October 2012, defines an authorization framework that "enables a third-party application to obtain limited access to an HTTP service", and it names four grant types: authorization code, implicit, resource owner password credentials and client credentials. RFC 7636 (September 2015) adds Proof Key for Code Exchange, PKCE, pronounced "pixy", against the authorization code interception attack, with code_challenge = BASE64URL-ENCODE(SHA256(ASCII(code_verifier))) for the S256 method. Its Appendix B works one example through: the code_verifier dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk gives the code_challenge E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM. RFC 9700, the Best Current Practice for OAuth 2.0 Security (January 2025), says public clients "MUST use PKCE", the resource owner password credentials grant "MUST NOT be used", and clients "SHOULD NOT use the implicit grant". OpenID Connect Core 1.0 describes OpenID Connect as "a simple identity layer on top of the OAuth 2.0 protocol", and its ID Token, a JSON Web Token, carries claims about how the end user was authenticated.

**Try in five minutes.** Write pkce.py with only the standard library: take the code_verifier from RFC 7636 Appendix B, hash it with hashlib.sha256, encode it with base64.urlsafe_b64encode, strip the trailing = padding, and print code_challenge=<the result>&code_challenge_method=S256. Run python3 pkce.py and compare it with the RFC.

- Docs: [RFC 6749, The OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749.html), [RFC 7636, Proof Key for Code Exchange by OAuth Public Clients](https://www.rfc-editor.org/rfc/rfc7636.html), [RFC 9700, Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html), [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- Shelf: Web, networks and APIs · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #net
