# Matrx ORM — Write Queue & Pool Configuration Upgrade Guide

**Version:** This document covers the write-queue feature added March 2026.

**Audience:** Project managers and developers using `matrx_orm` as a dependency.

---

## What Changed

The ORM now includes a **built-in async write queue** that prevents `Timeout acquiring connection` errors under high concurrency. Write operations (INSERT, UPDATE, DELETE) are funneled through an ordered queue instead of racing for pool connections. Read operations are unaffected and continue to acquire connections directly.

Additionally, **connection pool settings are now configurable per-database** instead of hardcoded.

---

## Do I Need to Change Anything?

**No.** All new settings have defaults that match the previous behavior exactly. If you change nothing in your code, the ORM behaves identically to before — except that the write queue is now active by default, silently preventing pool timeouts on writes.

The write queue is **transparent**: `await manager.update_item(...)` still returns the result after the write completes. Callers do not see a difference in the API. They just stop getting timeout errors under load.

---

## New Configuration Fields

`DatabaseProjectConfig` now accepts these optional fields:

| Field | Type | Default | Description |
|---|---|---|---|
| `pool_mode` | `str` | `"session"` | `"session"` for standard poolers (port 5432), `"transaction"` for Supavisor transaction pooler (port 6543). |
| `pool_min` | `int` | `5` | Minimum idle connections in the asyncpg pool. |
| `pool_max` | `int` | `20` | Maximum connections in the asyncpg pool. |
| `command_timeout` | `int` | `10` | Seconds before a SQL command times out. |
| `write_queue_enabled` | `bool` | `True` | Whether writes go through the async queue. |
| `write_concurrency` | `int` | `10` | Max simultaneous writes holding pool connections. Remaining connections stay available for reads. |
| `write_queue_size` | `int` | `200` | Max writes waiting in the queue before `WriteQueueFullError` is raised. |
| `write_queue_timeout` | `float` | `30.0` | Max seconds a write waits in the queue before `WriteQueueTimeoutError` is raised. |

---

## Configuration Examples

### Minimum — No Changes Required

```python
register_database(DatabaseProjectConfig(
    name="my-project",
    host="aws-0-us-west-1.pooler.supabase.com",
    port="5432",
    database_name="postgres",
    user="postgres.myref",
    password="...",
    alias="my-project",
))
```

This works exactly as before. The write queue is active with sensible defaults.

### Free Tier Supabase (Session Pooler, Conservative Pool)

```python
register_database(DatabaseProjectConfig(
    name="my-free-project",
    host="aws-0-us-east-1.pooler.supabase.com",
    port="5432",
    database_name="postgres",
    user="postgres.myref",
    password="...",
    alias="my-free-project",
    pool_mode="session",
    pool_min=2,
    pool_max=10,
    write_concurrency=5,
    write_queue_size=100,
))
```

Keeps the pool small (free tier has 60 max connections shared across all clients) and reserves half the pool for reads.

### Pro Tier Supabase (Transaction Pooler, Higher Throughput)

```python
register_database(DatabaseProjectConfig(
    name="automation-matrix",
    host="aws-0-us-west-1.pooler.supabase.com",
    port="6543",
    database_name="postgres",
    user="postgres.myref",
    password="...",
    alias="automation-matrix",
    pool_mode="transaction",
    pool_min=5,
    pool_max=20,
    write_concurrency=15,
    write_queue_size=500,
    write_queue_timeout=60.0,
))
```

Transaction pooler multiplexes app connections onto a smaller Postgres pool, so higher `pool_max` is safe. More `write_concurrency` since the pooler handles contention server-side.

### Disable the Write Queue Entirely

```python
register_database(DatabaseProjectConfig(
    name="low-traffic",
    ...,
    write_queue_enabled=False,
))
```

Writes go directly to the pool as they did before. Only do this if you are certain your workload never exceeds pool capacity.

---

## Environment Variable Configuration

If you use `register_database_from_env()`, the new settings can also be read from environment variables:

| Env Var | Maps To |
|---|---|
| `{PREFIX}_POOL_MODE` | `pool_mode` |
| `{PREFIX}_POOL_MIN` | `pool_min` |
| `{PREFIX}_POOL_MAX` | `pool_max` |
| `{PREFIX}_COMMAND_TIMEOUT` | `command_timeout` |
| `{PREFIX}_WRITE_QUEUE_ENABLED` | `write_queue_enabled` (`true`/`false`) |
| `{PREFIX}_WRITE_CONCURRENCY` | `write_concurrency` |
| `{PREFIX}_WRITE_QUEUE_SIZE` | `write_queue_size` |
| `{PREFIX}_WRITE_QUEUE_TIMEOUT` | `write_queue_timeout` |

Keyword arguments to `register_database_from_env()` take precedence over env vars. Env vars take precedence over defaults.

---

## New Exceptions

Two new exception classes are exported from `matrx_orm`:

| Exception | Parent | When It Fires |
|---|---|---|
| `WriteQueueFullError` | `DatabaseError` | The write queue has `write_queue_size` pending writes. Backpressure signal — reduce write rate or increase the limit. |
| `WriteQueueTimeoutError` | `DatabaseError` | A write waited longer than `write_queue_timeout` in the queue. The write was **not** applied. Caller should retry or fail. |

Both are subclasses of `DatabaseError`, so existing `except DatabaseError` blocks will catch them. You only need to handle them separately if you want different behavior (e.g., returning a 503 for `WriteQueueFullError`).

---

## Auto-Activation Safety Net

Even if a project has not configured any write-queue settings, the ORM will **automatically enable the write queue at runtime** when it detects the first `Timeout acquiring connection` error. This means:

- Projects that never hit pool saturation: the queue is pre-created but never used. Zero overhead.
- Projects that hit saturation unexpectedly: the queue activates on the first timeout, and all subsequent writes are queued instead of failing. A warning is logged.

This provides protection without requiring any configuration.

---

## Retry Behavior

Write operations that go through the queue include automatic retry with exponential backoff:

- Up to **2 retries** on transient errors (connection timeout, too many connections, lost connection).
- Backoff delays: **0.5s**, then **1.0s**.
- Non-transient errors (syntax errors, constraint violations, etc.) propagate immediately without retry.

This retry only applies to writes routed through the queue. Direct reads are not retried.

---

## Tuning Guide

| Symptom | Action |
|---|---|
| `WriteQueueFullError` in logs | Increase `write_queue_size` or `pool_max`. Your app produces writes faster than the pool drains them. |
| `WriteQueueTimeoutError` in logs | Increase `write_queue_timeout` or `pool_max`. Writes are queued but the pool is saturated for too long. |
| Reads feel slow under write-heavy load | Decrease `write_concurrency` to reserve more pool connections for reads. |
| Writes feel slow but pool is not saturated | Increase `write_concurrency` to let more writes run in parallel. |
| `Timeout acquiring connection` on reads | Increase `pool_max` (the write queue only helps writes — reads still acquire directly). |
| Using Supabase transaction pooler | Set `pool_mode="transaction"` and use port `6543`. This is the highest-leverage change for batch workloads. |

---

## Transaction Compatibility

Writes inside a `transaction()` block bypass the write queue and use the transaction's dedicated connection directly. This is correct behavior — transactional writes must execute on the same connection.

```python
async with transaction():
    await User.create(name="alice")       # uses transaction connection, not queue
    await Profile.create(user_id=...)     # same connection, same transaction
```

---

## Summary of Changes for Quick Reference

1. **Zero-config upgrade.** No code changes needed. Defaults match prior behavior.
2. **Write queue active by default.** Prevents timeout errors on writes under load.
3. **Pool settings now configurable.** `pool_min`, `pool_max`, `pool_mode`, `command_timeout`.
4. **Two new catchable exceptions.** `WriteQueueFullError`, `WriteQueueTimeoutError`.
5. **Auto-activation on first timeout.** Even unconfigured projects get protection.
6. **Retry with backoff on writes.** Transient connection errors are retried automatically.
7. **Reads are completely unaffected.** No queuing, no behavioral change.
