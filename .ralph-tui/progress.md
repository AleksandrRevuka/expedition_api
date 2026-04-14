# Expedition API - Progress Tracking

## Codebase Patterns
- API functions pattern: `async function(args): Promise<Type>` with JSDoc comments
- Types imported from `@/shared/types`, payloads defined inline in api.ts
- API client uses axios with interceptors for auth token injection
- Response types are fully typed with generics
- Import paths use `@/` alias for absolute imports
- Payload interfaces are co-located with functions for clarity

---

## [2026-04-14] - US-007
- **What was implemented:**
  - Created `frontend/src/features/expeditions/api.ts` with 9 typed API functions
  - Functions: fetchExpeditions(), fetchExpedition(id), createExpedition(payload), updateExpedition(id, payload), deleteExpedition(id), changeExpeditionStatus(id, status), inviteMember(expeditionId, userId), confirmMembership(expeditionId), removeMember(expeditionId, userId)
  - All functions properly typed using existing shared types (Expedition, ExpeditionStatus)
  - Payload interfaces defined inline for request/response clarity

- **Files changed:**
  - Created: `frontend/src/features/expeditions/api.ts`

- **Learnings:**
  - Payload interfaces should be exported alongside functions for reusability in components
  - Delete endpoints still return typed responses (consistent with API spec)
  - All expedition operations use same response type (Expedition) following REST conventions
  - Imports use `@/` absolute paths defined in frontend config
  - Status change requires wrapper object `{ status }` not direct enum

- **Build verification:**
  - `npm run build` exits 0 - all TypeScript compiles successfully
  - No type errors in new code or existing codebase

---

## [2026-04-14] - US-008
- **What was implemented:**
  - Created `frontend/src/features/websocket/manager.ts` with ExpeditionWsManager class
  - Handles WebSocket connection to `/api/ws/expeditions/{id}?token=<jwt>`
  - Implements exponential backoff reconnection (1s → 2s → 4s → ... → 30s max)
  - On 1008 close code: calls onAuthError callback and stops all reconnect attempts
  - Provides subscribe/unsubscribe handler pattern for message routing
  - Created `frontend/src/features/websocket/useWebSocket.ts` React hook
  - Hook only creates manager when both expeditionId and token are non-null
  - Automatically invalidates ['expedition', id] and ['expeditions'] queries on any message
  - Properly disconnects on unmount, preventing lingering connections

- **Files changed:**
  - Created: `frontend/src/features/websocket/manager.ts`
  - Created: `frontend/src/features/websocket/useWebSocket.ts`

- **Learnings:**
  - WebSocket URL construction uses query parameter for token (not headers) due to browser limitations
  - Exponential backoff formula: `Math.min(1000 * Math.pow(2, attempts), 30000)` cleanly caps at 30s
  - Error handlers must be bound to preserve `this` context in event listeners (used arrow functions)
  - React Query invalidation triggers refetch of specified query keys across all components
  - Hook dependencies must include queryClient to ensure proper cleanup and stability
  - Message handlers wrapped in try-catch to prevent one error from breaking other handlers
  - Stopped flag prevents race conditions between disconnect() and scheduled reconnects

- **Build verification:**
  - `npm run build` exits 0 - all TypeScript compiles successfully
  - No type errors in new code or existing codebase

---
