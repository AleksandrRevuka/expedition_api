# Ralph Progress Log

This file tracks progress across iterations. Agents update this file
after each iteration and it's included in prompts for context.

## Codebase Patterns (Study These First)

*Add reusable patterns discovered during development here.*

---

## [2026-04-14] - US-002: Frontend Project Scaffold

### Implementation Summary
Created a fully configured Vite + React + TypeScript + TailwindCSS frontend project with cyberpunk theme support.

### Files Created
- `frontend/package.json` — declares all required dependencies with correct versions
- `frontend/tsconfig.json` — strict TypeScript config with path aliases (@/*)
- `frontend/tsconfig.node.json` — config for Vite
- `frontend/vite.config.ts` — Vite configuration with React plugin, path alias, and API proxy (localhost:8000, ws: true)
- `frontend/tailwind.config.js` — Tailwind theme with cyberpunk colors (neon-cyan, neon-purple, dark-bg), custom shadows and animations
- `frontend/postcss.config.js` — PostCSS with Tailwind and Autoprefixer
- `frontend/index.html` — HTML with Google Fonts (Orbitron, Share Tech Mono) and Vite script
- `frontend/src/main.tsx` — React entry point with StrictMode
- `frontend/src/App.tsx` — Sample component using TailwindCSS and cyberpunk colors
- `frontend/src/index.css` — Tailwind directives with font family configuration
- `frontend/public/vite.svg` — Vite logo asset
- `frontend/.gitignore` — standard Node.js/Vite ignores

### Build Verification
✅ `npm run build` exits with code 0
✅ All TypeScript strict mode checks pass
✅ Vite compiles successfully to `dist/`

### Learnings
1. **TypeScript React setup**: Must include `@types/react` and `@types/react-dom` devDependencies for JSX compilation with strict mode
2. **Tailwind in Vite**: Need postcss.config.js to process Tailwind directives in CSS modules
3. **Path aliases**: Configured in both `tsconfig.json` (baseUrl + paths) and `vite.config.ts` (resolve.alias)
4. **WebSocket proxy**: Vite proxy supports `ws: true` for WebSocket connections to backend
5. **Google Fonts**: Preconnect links improve load performance for custom fonts in cyberpunk theme

---

## [2026-04-14] - US-001: Docker & Nginx Infrastructure

### Implementation Summary
Implemented full Docker and Nginx setup for the frontend to run containerized and proxy API calls to the backend container.

### Files Created
- `frontend/Dockerfile` — multi-stage build: node:20-alpine builds Vite artifacts, nginx:alpine serves them on port 3000
- `frontend/nginx.conf` — Nginx configuration with:
  - WebSocket proxying to `/api/ws/` with upgrade headers and 86400s timeout
  - API proxying to `/api/` with proper forwarded headers
  - SPA routing fallback to `/index.html`
  - Client max body size 20M for file uploads
- `docker/frontend.yaml` — Docker Compose service for expedition-frontend (port 3000, external network)
- `frontend/.env` — environment file with empty VITE_API_URL= (uses Nginx proxy)
- `frontend/.env.example` — documented configuration options for development vs production

### Makefile Updates
- Added `FRONTEND_FILE` variable pointing to `docker/frontend.yaml`
- Added `frontend` target: builds and starts frontend container
- Added `frontend-down` target: stops frontend container
- Added `frontend-logs` target: streams frontend container logs
- Added `all-full` target: creates expedition network, starts full stack (storages + app + frontend)
- Updated help section with all new targets

### Build Verification
✅ `npm run build` exits with code 0 (frontend builds successfully)
✅ `docker compose -f docker/frontend.yaml --env-file .env build` succeeds
✅ All compose files validate correctly together
✅ Makefile targets parse and execute correctly

### Learnings
1. **Docker Compose validation**: service dependencies are validated even on `docker compose build`. Removed `depends_on: expedition` from frontend.yaml to allow standalone builds (Docker Compose validates service references)
2. **Nginx WebSocket**: Requires `Upgrade` and `Connection` headers plus `proxy_http_version 1.1` for proper WebSocket proxying
3. **SPA routing in Nginx**: Use `try_files $uri $uri/ /index.html` to serve index.html for all non-existent paths (client-side routing)
4. **Multi-stage Docker builds**: Builder stage only adds ~140KB JavaScript; nginx:alpine final image is much smaller than including build tools
5. **External Docker networks**: Use `external: true` to allow multiple compose files to share the same network. Network must be created before compose up (handled in Makefile)
6. **Nginx configuration in Dockerfile**: Copy nginx.conf from source to `/etc/nginx/nginx.conf` before copying built assets to ensure proper reload behavior

---
