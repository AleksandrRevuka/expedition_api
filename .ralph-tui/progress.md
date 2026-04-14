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

## [2026-04-14] - US-006
- **What was implemented:**
  - Updated `frontend/src/features/auth/api.ts`: RegisterPayload now includes first_name, last_name, role fields (matching backend CreateUserCommand)
  - Created `frontend/src/features/auth/components/LoginModal.tsx` with:
    - Email + password input fields
    - Auto-focused error handling with inline error display
    - Submit button with loading state during entire async chain
    - Link to switch to RegisterModal
    - Async chain: loginUser → fetchMe() → setAuth(token, user) → closes modal on success
  - Created `frontend/src/features/auth/components/RegisterModal.tsx` with:
    - First name, last name, email, password input fields
    - Role select dropdown (member/chief)
    - Auto-login flow: registerUser → loginUser → fetchMe() → setAuth(token, user)
    - Inline error display
    - Link to switch to LoginModal
    - Submit button with loading state during entire async chain
  - Created `frontend/src/features/auth/components/index.ts` for clean exports

- **Files changed:**
  - Modified: `frontend/src/features/auth/api.ts` (updated RegisterPayload interface)
  - Created: `frontend/src/features/auth/components/LoginModal.tsx`
  - Created: `frontend/src/features/auth/components/RegisterModal.tsx`
  - Created: `frontend/src/features/auth/components/index.ts`

- **Learnings:**
  - RegisterPayload must match backend CreateUserCommand exactly (first_name, last_name, role)
  - Modal form state should be managed with separate useState hooks for each field
  - Async chain order is critical: registerUser → login → fetchMe() → setAuth()
  - Loading state should disable all inputs and show loading text on button
  - Error messages should be displayed inline within modal, not alerts
  - Both modals use shared Modal.tsx component with custom form content inside
  - Switch links allow user to toggle between login/register without closing modal

- **Build verification:**
  - `npm run build` exits 0 - all TypeScript compiles successfully
  - No type errors in new code or existing codebase
  - All acceptance criteria met

---

## [2026-04-14] - US-009
- **What was implemented:**
  - Created `frontend/src/features/expeditions/components/ExpeditionCard.tsx`:
    - Displays expedition title, description, status badge (color-coded), member count/capacity, and start date
    - Status badges map to colors: planned=yellow, in_progress=cyan, completed=green, cancelled=red
    - Selected state shows cyan neon glow with enhanced shadow
    - Click handler calls onSelect(id) callback
  - Created `frontend/src/features/expeditions/components/ExpeditionList.tsx`:
    - Fetches expeditions using useQuery(['expeditions'], fetchExpeditions)
    - Shows animated loading spinner with label during fetch
    - Shows error state with error message and retry button
    - Shows empty state with role-specific message (chief vs member)
    - Chief users see '+ NEW' button above list to create new expeditions
    - Grid layout: 1 column mobile, 2 columns tablet, 3 columns desktop
    - Tracks selected expedition in local state
  - Created `frontend/src/features/expeditions/components/index.ts` for clean exports

- **Files changed:**
  - Created: `frontend/src/features/expeditions/components/ExpeditionCard.tsx`
  - Created: `frontend/src/features/expeditions/components/ExpeditionList.tsx`
  - Created: `frontend/src/features/expeditions/components/index.ts`

- **Learnings:**
  - Status enum values use snake_case (in_progress) but display text should use Title Case with spaces
  - Badge component supports variant prop (cyan, purple, green, yellow, red, gray) for status coloring
  - GlassPanel glow prop can be set conditionally based on selection state
  - Grid layout with Tailwind (md: and lg: breakpoints) adapts to different screen sizes
  - Loading/error states should prevent layout shift using fixed height containers with flex centering
  - Empty state messages differ based on user role (chief can create, member waits for invitation)
  - Selected state uses enhanced shadow effect `shadow-[0_0_40px_rgba(0,255,255,0.6)]` for cyan neon glow

- **Build verification:**
  - `npm run build` exits 0 - all TypeScript compiles successfully
  - No type errors in new code or existing codebase
  - All acceptance criteria met

---

## [2026-04-14] - US-011
- **What was implemented:**
  - Created `frontend/src/features/expeditions/components/CreateExpeditionModal.tsx`:
    - Form fields: title (text), description (textarea), start_at (datetime-local), capacity (number)
    - Calls createExpedition() with payload
    - Invalidates ['expeditions'] query on success
    - Closes modal on success
    - Shows loading state during submission
    - Displays inline errors on failure
  - Created `frontend/src/features/expeditions/components/EditExpeditionModal.tsx`:
    - Pre-fills title and description from expedition prop using useEffect
    - Calls updateExpedition() with title/description only (per API spec)
    - Invalidates both ['expedition', id] and ['expeditions'] on success
    - Closes modal on success
    - Shows loading state during submission
    - Displays inline errors on failure
  - Created `frontend/src/features/expeditions/components/InviteMemberModal.tsx`:
    - Single field for user ID (UUID)
    - Displays informational note: "The invited user must have the member role to accept the invitation."
    - Calls inviteMember(expeditionId, userId) with proper payload
    - Invalidates ['expedition', id] on success
    - Closes modal on success
    - Shows loading state during submission
    - Displays inline errors on failure
  - Updated `frontend/src/features/expeditions/components/index.ts` to export all three new modals

- **Files changed:**
  - Created: `frontend/src/features/expeditions/components/CreateExpeditionModal.tsx`
  - Created: `frontend/src/features/expeditions/components/EditExpeditionModal.tsx`
  - Created: `frontend/src/features/expeditions/components/InviteMemberModal.tsx`
  - Modified: `frontend/src/features/expeditions/components/index.ts`

- **Learnings:**
  - Modal form pattern is consistent: useState for each field, handleSubmit for async submission
  - useQueryClient().invalidateQueries({ queryKey: [...] }) is the pattern for cache invalidation
  - useEffect with expedition dependency is needed to pre-fill edit modals
  - All inputs should be disabled during loading to prevent double-submission
  - Inline error display (not alerts) provides better UX within modals
  - Datetime-local input type provides native date/time picker with ISO format
  - Textarea needs explicit rows prop and resize-none class to match form styling
  - User ID field uses font-mono class for UUID readability
  - Informational notes in modals use cyan background at low opacity for consistency with design system

- **Build verification:**
  - `npm run build` exits 0 - all TypeScript compiles successfully
  - No type errors in new code or existing codebase
  - All acceptance criteria met

---
## [2026-04-14] - US-010
- **What was implemented:**
  - Created `frontend/src/features/expeditions/components/ExpeditionDetail.tsx`:
    - Fetches expedition using useQuery(['expedition', id], () => fetchExpedition(id))
    - Displays: title, status badge (color-coded), description, start date, capacity (confirmed/total)
    - Shows member list with NameSkeleton placeholder while user data loads (never shows raw UUID)
    - State badges: confirmed=green, invited=yellow
    - Chief sees 'COMMANDS' panel with: Edit, Invite, Delete buttons and status switcher
    - Delete button shows confirmation dialog with confirm/cancel options
    - Status switcher shows all 4 status buttons (planned, in_progress, completed, cancelled) with current status highlighted
    - All command buttons show loading state during submission
    - Invited members see purple invitation banner with 'CONFIRM' button (only if not confirmed)
    - Members only see member list if chief or confirmed member
    - Chief can remove individual members via 'Remove' button in each member row
    - Calls useExpeditionWs(expeditionId, token, onAuthError) with logout on auth error
    - On delete success: calls onDeleted() callback (parent clears selection)
    - Shows loading spinner during fetch; error state with retry button on failure
  - Updated `frontend/src/features/expeditions/components/index.ts` to export ExpeditionDetail
  - MemberRow is a sub-component for rendering each member with name resolution via useUser hook

- **Files changed:**
  - Created: `frontend/src/features/expeditions/components/ExpeditionDetail.tsx`
  - Modified: `frontend/src/features/expeditions/components/index.ts`

- **Learnings:**
  - NameSkeleton pattern: show loading placeholder while user data loads instead of raw UUID
  - MemberRow uses useUser hook for name resolution with staleTime: Infinity (user data never changes)
  - Status badge variant determined by ExpeditionStatus enum value (not state)
  - Chief determination: `user?.role === Role.Chief && user?.id === expedition?.chief_id`
  - Member access determination: filter members by state === MemberState.Confirmed
  - Status switcher buttons: grid layout with disabled state when status matches current
  - Invitation banner only shows for invited members who are NOT confirmed (isInvited && !isMember)
  - WebSocket connection validated in hook based on expeditionId/token presence
  - Delete confirmation uses nested GlassPanel with red border for destructive action
  - All async operations disable buttons/inputs to prevent double-submission
  - Query invalidation after delete targets both ['expedition', id] and ['expeditions'] queries

- **Build verification:**
  - `npm run build` exits 0 - all TypeScript compiles successfully
  - No type errors in new code or existing codebase
  - All acceptance criteria met

---
