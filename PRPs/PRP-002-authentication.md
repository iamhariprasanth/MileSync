# PRP-002: User Authentication System

## Goal
Implement complete auth system with email/password and OAuth.

## Why
Users need secure authentication before accessing goal coaching features.

## Success Criteria
- [ ] User can register with email/password
- [ ] User can login and receive JWT
- [ ] Google OAuth flow works
- [ ] GitHub OAuth flow works
- [ ] Protected routes reject unauthenticated requests

## Files to Create/Update
```
backend/app/models/user.py
backend/app/schemas/user.py
backend/app/routes/auth.py
backend/app/services/auth_service.py
backend/app/services/oauth_service.py
backend/app/utils/dependencies.py

frontend/src/pages/Login.tsx
frontend/src/pages/Register.tsx
frontend/src/context/AuthContext.tsx
frontend/src/api/auth.ts
```

## Task Sequence
1. CREATE User model (id, email, password_hash, name, avatar_url, auth_provider)
2. CREATE auth schemas (RegisterRequest, LoginRequest, TokenResponse, UserResponse)
3. CREATE auth_service.py (hash_password, verify_password, create_token, decode_token)
4. CREATE oauth_service.py (google_auth_url, google_callback, github_auth_url, github_callback)
5. CREATE auth routes (/register, /login, /me, /google, /google/callback, /github, /github/callback)
6. CREATE get_current_user dependency for protected routes
7. CREATE AuthContext with login/logout/user state
8. CREATE Login page with email/password + social buttons
9. CREATE Register page
10. VALIDATE auth flow end-to-end

## Anti-Patterns
- Don't store plain text passwords
- Don't expose JWT secret in client code
- Don't skip token validation on protected routes

## Gotchas
- OAuth requires redirect URIs configured in Google/GitHub developer consoles
- JWT expiration must be handled on frontend
- Password hashing is CPU-intensive, use bcrypt

## Documentation References
- [python-jose](https://python-jose.readthedocs.io/)
- [Google OAuth](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth](https://docs.github.com/en/developers/apps/building-oauth-apps)
