# Projects frontend

> **Current state:** this frontend was vibe coded with Claude so I could keep my focus on
> the backend (ProjectService, LoginService, the gateway). It's a thin UI to click through
> the API, not a finished product. Expect it to be rewritten or extended by hand later.

A small React app for ProjectService: log in, list your projects, create a project.
Anything not built yet has an empty "Not built yet" page.

## Stack

Same as the LoginService frontend: Vite, React 19, TypeScript, Tailwind 4,
TanStack Query, React Router. Same MVVM layout: each page is a View (`*Page.tsx`)
plus a ViewModel hook (`use*ViewModel.ts`), and `model.ts` holds the API calls.

## Running it

It's served through the gateway (`gateway/nginx.conf`) together with the LoginService
frontend, so both apps share one origin and therefore the same tokens in `localStorage`.

| URL (gateway, port 8088) | Served by |
|---|---|
| `/projects/*` | this app (nginx container) |
| `/api/v1/projects*` | ProjectService backend |
| `/auth/*`, other `/api/*` | LoginService frontend and backend |

```bash
docker compose up -d --build
```

Open http://localhost:8088/. If you're not logged in, you're sent to
`/auth/login?next=/projects/` and come back here afterwards.

**Local dev with hot reload:** `npm run dev`. The dev server (port 5173) proxies `/api`
and `/auth` to the gateway on 8088, so the gateway stack must be running. Log in at
http://localhost:5173/auth/ (not 8088), so the dev server's origin gets the token.

## How login works

- `src/shared/api.ts`: token store plus `http()`. It's the same code as LoginService's
  (same localStorage keys, same single-flight refresh on 401). The only addition is
  `ApiError`, which carries the HTTP status.
- `src/shared/RequireLogin.tsx`: wraps every route. With no token, it redirects to the login app.
- `src/main.tsx`: if a request is still 401 after the refresh attempt, the session is
  gone, so it goes back to login.
- Logout calls LoginService's `/api/v1/logout`, clears the tokens, and goes to `/auth/login`.

## Structure

```
src/
  main.tsx                          routes (basename /projects), query client
  shared/
    api.ts                          tokens, http(), ApiError
    auth.ts                         goToLogin(), logout()
    RequireLogin.tsx                route guard
    ui.tsx                          Page, Card, Field, Button, ErrorMessage, NotBuiltYet
  features/projects/
    model.ts                        Project type (mirrors ProjectPublic), projectsApi
    List/                           GET  /api/v1/projects
    Create/                         POST /api/v1/projects
    Detail/                         placeholder
    Upload/                         placeholder
```

## Not built yet

- **Upload:** creating a project only creates the database row and returns a presigned
  `upload_url` (MinIO). The `.blend` file still has to be `PUT` to that URL from the browser.
  That needs CORS on MinIO for the gateway origin.
- **Project detail:** `GET /api/v1/projects/{id}` (project plus scan details).
- **Rename** (`PATCH`) and **delete**.
