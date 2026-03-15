# Capsule Corp Login Leak

Dr. Brief's engineering team deployed a new employee portal in a hurry before the Tenkaichi Budokai.

They left some **debug middleware** enabled in production that leaks internal state through HTTP headers.

The login endpoint is running at:

```
https://capsulecorp-portal.ctf.local/login
```

Interact with the login form and inspect the server's responses carefully.

**Hint:** Sometimes secrets slip through the cracks — or the headers.
