# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run inside the Docker container. Start the stack first:

```bash
make storages       # start PostgreSQL + Redis
make app            # build and start the API container
make all            # start everything at once
```

**Tests** (run inside container via `make`, or directly with `docker exec expedition`):

```bash
make test           # unit + e2e
make test-unit      # pytest -m unit
make test-e2e       # pytest -m e2e

# Run a single test file or test
docker exec expedition pytest tests/users/unit/test_create_user.py
docker exec expedition pytest tests/users/ -m unit -k "test_create"
```

**Database migrations:**

```bash
make migrate                        # alembic upgrade head
make migrations msg="description"   # autogenerate new migration
make downgrade rev="revision_id"    # rollback to revision
```

**Linting / type checking** (inside container or venv):

```bash
ruff check src/
ruff format src/
ty check src/          # or: mypy src/
```

## Architecture Overview

**Modular Monolith + DDD + Clean Architecture.** Four modules: `auth`, `users`, `expeditions`, `websocket`. Each module (except `auth` and `websocket`) has four layers:

```
src/modules/<module>/
├── domain/         # aggregates, entities, value objects, domain events
├── application/    # use cases, commands, handlers (command + event)
├── infrastructure/ # SQLAlchemy UoW, repositories, external services
└── presentation/   # FastAPI routers, Pydantic request/response schemas
```

### Key Architectural Patterns

**Handler-owned Unit of Work (CRITICAL):**
```python
class MyCommandHandler:
    async def __call__(self, command: MyCommand) -> Result:
        async with self.uow:                    # handler opens UoW
            result = await use_case(command)    # use case gets repos, NOT uow
            await self.uow.commit()
        await self.uow.collect_events(result)   # events AFTER commit
        return result
```
Use cases receive repositories from `uow.repo_name`, never the UoW itself.

**MessageBus + Bootstrap:** Each module has a `MessageBus` wired in `MessagebusContainer` via `Bootstrap`. Commands map to exactly one handler; events map to a list of handlers. The bus processes a queue — command handlers emit events that re-enter the queue after the command completes.

**Imperative ORM mapping:** SQLAlchemy tables and domain dataclasses are decoupled. Mapper callables are registered in `src/adapters/database/models/_all_mappers.py` and called once at app startup (and once in tests via `map_models_to_orm` fixture).

**DI Container hierarchy:**
```
Container (main_container.py)
├── core       → BaseContainer      (DB manager, ws_manager)
├── uows       → UowContainer       (one UoW per module)
├── services   → ServicesContainer  (password, token services)
└── messagebus → MessagebusContainer (Bootstrap → MessageBus per module)
```
Wiring targets are declared in `Container.wiring_config`. Add new routers/modules there.

**Background tasks:** Taskiq with Redis broker (`src/tkq.py`). Scheduled tasks use both a Redis source and a Postgres source (`src/tkq_sched.py`). Per-module tasks live in `application/tasks.py`.

**Domain models** are `@dataclass(kw_only=True)` subclasses of `AggregateRoot` + `BaseWithTimestamps`. Events are added via `add_event()` inside domain methods; collected by the handler via `uow.collect_events(aggregate)`.

### Test Infrastructure

Tests use **SQLite in-memory** (via `aiosqlite`) — not PostgreSQL. The `ENVIRONMENT=test` config switches the DB URL. Core fixtures in `tests/conftest.py`:
- `db_manager` — SQLite async manager
- `test_db` — creates schema, drops after test
- `map_models_to_orm` — calls imperative mappers once
- `async_session` — raw session for repository tests
- `test_container` / `test_app` / `async_client` — for e2e tests
- `user_factory`, `expedition_factory`, `member_factory` — accept `persist=True` to write to DB

Module-level conftest goes in `tests/<module>/conftest.py`. Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`.

### Adding a New Module

1. Create `src/modules/<name>/{domain,application,infrastructure,presentation}` layers
2. Add mapper callables to `src/adapters/database/models/_all_mappers.py`
3. Add UoW to `UowContainer`, services to `ServicesContainer`
4. Wire commands/events in `MessagebusContainer`
5. Add router package to `Container.wiring_config` and include in `src/all_routers.py`

## API Endpoints

Base prefix: `/api`. Router classes enforce access: `ChiefAPIRouter` requires role `chief`, `MemberAPIRouter` requires role `member`, `AuthenticatedAPIRouter` accepts any authenticated user.

### `POST /api/auth/register`
Public. Accepts `CreateUserCommand` (email, password, name). Creates user, hashes password, emits `UserRegisteredEvent` + `UserChangedRoleEvent`. Returns `UserResponse`.

### `POST /api/auth/login`
Public. OAuth2 password form (`username` = email). Returns `TokenResponse` with a JWT access token.

### `GET /api/users/me`
Auth. Returns the profile of the currently authenticated user (decoded from JWT).

### `GET /api/users/{user_id}`
Auth. Fetches any user by UUID. Returns `UserResponse`.

### `GET /api/expeditions/`
Auth. Returns a list of all expeditions (no filtering).

### `GET /api/expeditions/{expedition_id}`
Auth. Returns a single expedition with its members loaded.

### `POST /api/expeditions/`
Chief. Body: `title`, `description`, `start_at`, `capacity`. Sets `chief_id` from the JWT. Returns created `ExpeditionResponse`.

### `PATCH /api/expeditions/{expedition_id}`
Chief. Updates `title` and/or `description`. Validates that the caller is the chief of the expedition.

### `DELETE /api/expeditions/{expedition_id}`
Chief. Deletes the expedition. Validates ownership. Returns `204 No Content`.

### `PATCH /api/expeditions/{expedition_id}/status`
Chief. Body: `{ "status": "<new_status>" }`. Changes expedition status; fires `ExpeditionStatusChangedEvent` which broadcasts a WS notification to all connected members.

### `POST /api/expeditions/{expedition_id}/members/invite`
Chief. Body: `{ "user_id": "<uuid>" }`. Validates the target user has role `member` (cross-module query via `GetUserUseCase`). Adds member with state `invited`; fires `MemberInvitedEvent` → WS broadcast.

### `DELETE /api/expeditions/{expedition_id}/members/{user_id}`
Chief. Removes a member from the expedition; fires `MemberRemovedEvent` → WS broadcast. Returns updated `ExpeditionResponse`.

### `POST /api/expeditions/{expedition_id}/members/confirm`
Member. The calling user confirms their own invitation (no body needed). Sets member state to `confirmed`; fires `MemberConfirmedEvent` → WS broadcast.

## WebSocket

### `WS /api/ws/expeditions/{expedition_id}?token=<jwt>`

Authentication is passed as a **query parameter** `token` (not a header), because browsers cannot set WS headers. The dependency `get_ws_current_user` decodes the token and looks up the user.

**Connection flow:**
1. Token is decoded → user resolved.
2. Expedition is loaded with `members` relationship.
3. If user is not a participant (`expedition.is_participant(user_id)`), the connection is closed with code `1008`.
4. Otherwise the socket is accepted and registered in `ExpeditionConnectionManager`.
5. The server only **receives** text frames (not processed — the loop just keeps the connection alive). All outbound messages are server-pushed via events.

**`ExpeditionConnectionManager`** is a singleton (registered in `BaseContainer`). It holds connections as `{expedition_id: {user_id: set[WebSocket]}}`. Disconnected sockets are pruned lazily during broadcast.

**Outbound WS events** (sent by domain event handlers after a command completes):

|      Event key      |             Trigger             |       Payload fields       |
|---------------------|---------------------------------|----------------------------|
| `expedition_status` | `ChangeExpeditionStatusCommand` | `expedition_id`, `status`  |
| `member_invited`    | `InviteMemberCommand`           | `expedition_id`, `user_id` |
| `member_confirmed`  | `ConfirmMemberCommand`          | `expedition_id`, `user_id` |
| `member_removed`    | `RemoveMemberCommand`           | `expedition_id`, `user_id` |

The WS manager is injected into expedition event handlers via the `dependencies` dict in `MessagebusContainer`.

## Rules Reference

Detailed rules live in `.claude/rules/`:
- `architecture.md` — layer constraints, handler-owned UoW pattern, CQRS
- `code-style.md` — type hints, dataclass/Pydantic conventions, custom exceptions
- `testing.md` — test structure, what to test, fixture conventions
- `workflow.md` — BA → DDD Architect → Developer → Security → QA → Tester → Docs
- `git-operations.md` — never commit/push automatically; no AI mentions in PRs
