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
## [2026-04-14] - US-003: Shared Types, API Client & App Entry

### Implementation Summary
Created shared TypeScript types, configured Axios API client with authentication interceptors, environment configuration, custom Tailwind utilities, React Providers with QueryClient, and updated the app entry point.

### Files Created
- `frontend/src/shared/types/index.ts` — Exports all domain types: User, Expedition, Member, TokenResponse, WsMessage, Role (enum), ExpeditionStatus (enum), MemberState (enum)
- `frontend/src/shared/api/client.ts` — Axios instance with:
  - baseURL: `${ENV.API_URL}/api`
  - Request interceptor: reads `localStorage.auth_token` and sets `Authorization: Bearer` header
  - Response interceptor: on 401, clears token and reloads page
- `frontend/src/shared/config/env.ts` — ENV object exports API_URL from `import.meta.env.VITE_API_URL`
- `frontend/src/app/index.css` — Custom Tailwind @layer components:
  - `.glass-panel` — frosted glass effect (bg-opacity-10, backdrop-blur-md, border effects)
  - `.neon-border-cyan` — cyan border with glow shadow
  - `.neon-border-purple` — purple border with glow shadow
  - `.neon-text-cyan` — cyan text with drop shadow glow
  - `.neon-text-purple` — purple text with drop shadow glow
- `frontend/src/app/providers.tsx` — React Providers component wrapping QueryClientProvider with configured QueryClient (5min stale time, retry=1)

### Files Modified
- `frontend/src/main.tsx` — Updated to mount `<Providers><App /></Providers>` into #root (added Providers wrapper)
- `frontend/tsconfig.json` — Added `"types": ["vite/client"]` to compilerOptions for import.meta.env type support

### Build Verification
✅ `npm run build` exits with code 0
✅ TypeScript strict mode checks pass (`npm run type-check`)
✅ All imports/exports are properly typed
✅ Vite builds successfully to `dist/`

### Learnings
1. **Vite environment types**: Must add `"types": ["vite/client"]` to tsconfig.json for TypeScript to recognize `import.meta.env` properties
2. **Tailwind @layer components**: Use `@layer components` to define custom utility classes at the component layer (lower precedence than utilities, higher than base)
3. **Axios interceptors**: Request interceptors run before sending, response interceptors run after receiving. 401 handling should clear auth state and reload to redirect to login
4. **QueryClient configuration**: Default options can be set globally (staleTime, retry) and overridden per-query as needed
5. **Enum usage in TypeScript**: Domain enums (Role, ExpeditionStatus, MemberState) map to backend string values, making API contracts type-safe

---

## [2026-04-14] - US-004: Shared UI Components

### Implementation Summary
Created reusable cyberpunk-styled UI primitives (Button, Input, Modal, Badge, GlassPanel) for consistent theming across all feature UIs. All components use Orbitron font for labels/headings and leverage TailwindCSS with custom glass-panel and neon utilities.

### Files Created
- `frontend/src/shared/ui/Button.tsx` — Button component with:
  - Variants: primary (cyan), secondary (purple), danger (red), ghost (outlined cyan)
  - Props: variant, isLoading, disabled, and standard HTML button attributes
  - Loading state renders animated spinner
  - Disabled state dims button and disables pointer events
  - Neon glow shadows on hover for primary/secondary/danger variants
- `frontend/src/shared/ui/Input.tsx` — Input component with:
  - Props: label, error, and standard HTML input attributes
  - Glass-panel styling with dark-bg transparency
  - Orbitron font for label
  - Neon-cyan focus ring with border transition
  - Error state shows red border and error message below input
- `frontend/src/shared/ui/Modal.tsx` — Modal component with:
  - Props: isOpen, onClose, title, children
  - Glass overlay with backdrop-blur effect (darker background layer)
  - Closes on Escape key via useEffect hook
  - Closes on backdrop click (clicking outside modal)
  - Close button in top-right corner
  - Header with title and cyan border separator
  - Proper accessibility attributes (role="dialog", aria-modal="true")
- `frontend/src/shared/ui/Badge.tsx` — Badge component with:
  - Variants: cyan, purple, green, yellow, red, gray
  - Pill-shaped styling with semi-transparent background and colored borders
  - Orbitron font for consistent labeling
- `frontend/src/shared/ui/GlassPanel.tsx` — Glass card container with:
  - Glow options: cyan, purple, none
  - Glass-panel styling with backdrop-blur and transparency
  - Optional neon border and colored shadows based on glow variant
- `frontend/src/shared/ui/index.ts` — Barrel export for all UI components and their TypeScript props interfaces

### Build Verification
✅ `npm run build` exits with code 0
✅ TypeScript strict mode compilation succeeds
✅ All 79 modules transformed correctly
✅ Vite production build outputs to `dist/` successfully

### Learnings
1. **React.forwardRef with TypeScript**: Use `React.forwardRef<HTMLElement, Props>` pattern for components that need ref forwarding; wrap both component definition and props extension (e.g., `ButtonHTMLAttributes<HTMLButtonElement>`)
2. **useEffect cleanup in TypeScript**: Must ensure all code paths in useEffect return a cleanup function or undefined; early `if (!isOpen) return` is cleaner than conditional logic inside
3. **Orbitron font in Tailwind**: Font is available globally via index.css `@layer base`, so use `font-orbitron` class directly on text elements; configured in tailwind.config.js theme.fontFamily
4. **Glass-panel utility reuse**: Custom `.glass-panel` class defined in app/index.css combines `backdrop-blur-md`, `bg-opacity-10`, and border styling; reuse it as base class then add variants (glow colors, shadows)
5. **Tailwind arbitrary values**: Use `shadow-[0_0_30px_rgba(0,255,255,0.3)]` syntax for precise neon glow effects not in the standard Tailwind palette
6. **Component composition**: Leverage existing utilities and custom classes (glass-panel, neon colors) defined in previous iterations rather than reinventing styling

---
