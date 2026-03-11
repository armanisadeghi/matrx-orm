**Matrx ORM — Supabase Connection Strategy**

Per-Project Connection Pool Configuration & Adaptive Queuing

# **1\. Background & Problem Statement**

AI Matrx runs four active Supabase projects across two billing tiers. Each project has different Postgres connection limits, IPv4 availability, and compute capacity. The ORM must be aware of these differences and route connections correctly — or batch jobs will exhaust the pool and fail silently.

The core constraint: Supabase limits direct Postgres connections by compute tier. Going over that limit produces: too many connections errors (SQLSTATE 53300). The fix is not just increasing limits — it is routing correctly per project and queuing intelligently when demand approaches saturation.

# **2\. Project Inventory**

**Live data as of March 2026:**

| Project | Plan | Compute | max\_conn | User Limit | IPv4 Direct | PG Version |
| :---- | :---- | :---- | ----- | ----- | :---- | :---- |
| **automation-matrix** | **Pro** | Small (2 vCPU / 4 GB RAM) | 90 | 87 | ✓ Yes (+$4/mo) | PostgreSQL 15 |
| **Matrx Flow** | Free | Nano (shared CPU / 512 MB RAM) | 60 | 57 | ✗ No (IPv6 only) | PostgreSQL 17 |
| **My Matrx** | Free | Nano (shared CPU / 512 MB RAM) | 60 | 57 | ✗ No (IPv6 only) | PostgreSQL 17 |
| **Matrx DM** | Free | Nano (shared CPU / 512 MB RAM) | 60 | 57 | ✗ No (IPv6 only) | PostgreSQL 17 |

**Key observations:**

* automation-matrix is the only project on a paid plan with IPv4 add-on. It can use direct connections or the transaction pooler.

* Matrx Flow, My Matrx, and Matrx DM are all on the Free tier with Nano compute (max\_connections \= 60). Their db.\[ref\].supabase.co host is IPv6-only — standard IPv4 networks cannot reach it.

* All projects have Supavisor running. The pooler hostname (not the db. host) is always IPv4-accessible on all plans.

# **3\. Supabase Connection Modes — What They Are**

| Mode | Port | Host | Max Conns | Works On | Best For |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Direct Postgres** | `5432` | `db.[ref].supabase.co` | \= max\_connections (90/60) | IPv4 add-on required for most networks | Migrations, long transactions, pgvector, advisory locks |
| **Session Pooler (Supavisor)** | `5432` | `[region].pooler.supabase.com` | Bounded by max\_connections (1 conn held per client session) | IPv4 ✓ (all plans) | Persistent connections, prepared statements, long-lived ORM pools. Free tier fallback. |
| **Transaction Pooler (Supavisor)** | `6543` | `[region].pooler.supabase.com` | Thousands of app conns → small PG pool (multiplexed) | IPv4 ✓ (all plans) | Batch jobs, high-concurrency, short-lived queries. BEST for ORM workers. |

## **3a. Transaction Pooler Limitations (important for ORM)**

When using transaction pooler (port 6543), the following Postgres features are NOT available because each query may run on a different backend connection:

* Prepared statements (use simple query protocol instead)

* SET LOCAL / session-scoped variables (do not persist across queries)

* Advisory locks

* LISTEN / NOTIFY

* COPY TO/FROM with streaming

For asyncpg/psycopg3: disable prepared statement caching or use statement\_cache\_size=0. For SQLAlchemy: use NullPool or pre-ping \+ short pool recycle.

## **3b. Session Pooler Limitation**

Session pooler holds a real Postgres connection open for the entire lifetime of the client session. This means concurrent sessions still count against max\_connections — it doesn't multiply your capacity. Its main benefit is IPv4 routing on free tier, not connection amplification.

# **4\. Per-Project ORM Configuration**

| Project | Plan | IPv4 Direct | ORM Pool Mode | Pool Min | Pool Max | Queue Threshold |
| :---- | :---- | :---- | :---- | ----- | ----- | :---- |
| **automation-matrix** | **Pro** | ✓ | `transaction (6543)` | 5 | 20 | 80% of 87 \= \~70 conns |
| **Matrx Flow** | Free | ✗ pooler only | `session (5432)` | 2 | 10 | 80% of 57 \= \~46 conns |
| **My Matrx** | Free | ✗ pooler only | `session (5432)` | 2 | 10 | 80% of 57 \= \~46 conns |
| **Matrx DM** | Free | ✗ pooler only | `session (5432)` | 2 | 10 | 80% of 57 \= \~46 conns |

## **4a. automation-matrix (Pro \+ IPv4 add-on)**

**Connection string format:**

`# Transaction pooler (recommended for batch/ORM workers)`

`postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`

`# Direct (use only for migrations, long transactions, advisory locks)`

`postgresql://postgres:[password]@db.txzxabzwovsujtloxrus.supabase.co:5432/postgres`

**ORM pool settings:**

* min\_size: 5, max\_size: 20

* Pool mode: transaction (6543)

* statement\_cache\_size: 0  (transaction pooler requirement)

* command\_timeout: 30

* Queue threshold: 70 active connections (80% of 87 user slots)

## **4b. Matrx Flow / My Matrx / Matrx DM (Free tier — IPv4 via session pooler only)**

**Connection string format:**

`# Session pooler — ONLY valid option for IPv4 networks`

`postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres`

Note: the pooler.supabase.com hostname on port 5432 routes to the session pooler on free tier. Port 6543 (transaction pooler) is also available but session pooler is safer for standard ORM connection pools that use prepared statements or session state.

**ORM pool settings:**

* min\_size: 2, max\_size: 10

* Pool mode: session (5432 on pooler host)

* command\_timeout: 30

* Queue threshold: 46 active connections (80% of 57 user slots)

**Region-to-pooler-host map:**

* us-west-1  →  aws-0-us-west-1.pooler.supabase.com

* us-east-1  →  aws-0-us-east-1.pooler.supabase.com

* us-west-2  →  aws-0-us-west-2.pooler.supabase.com

# **5\. ORM Project Config Schema**

Each project in the ORM should carry a typed config block. Suggested Python dataclass:

`@dataclass`

`class ProjectConnectionConfig:`

    `project_id:         str`

    `project_name:       str`

    `region:             str`

    `plan:               Literal['free', 'pro', 'team', 'enterprise']`

    `ipv4_addon:         bool        # True only if $4/mo add-on is paid`

    `max_pg_connections: int         # actual max_connections from Postgres`

    `user_conn_limit:    int         # max_connections - superuser_reserved`

    `pool_mode:          Literal['transaction', 'session']`

    `pool_min:           int`

    `pool_max:           int`

    `queue_threshold:    int         # connections at which queuing kicks in`

    `host:               str         # always pooler host (safe for IPv4)`

    `port:               int         # 6543=transaction, 5432=session`

    `direct_host:        str | None  # only set if ipv4_addon=True`

Instantiated configs:

`PROJECTS = {`

  `"automation-matrix": ProjectConnectionConfig(`

    `project_id="txzxabzwovsujtloxrus",  project_name="automation-matrix",`

    `region="us-west-1",     plan="pro",      ipv4_addon=True,`

    `max_pg_connections=90,  user_conn_limit=87,`

    `pool_mode="transaction",  pool_min=5,  pool_max=20,`

    `queue_threshold=70,`

    `host="aws-0-us-west-1.pooler.supabase.com",  port=6543,`

    `direct_host="db.txzxabzwovsujtloxrus.supabase.co",`

  `),`

  `"matrx-flow": ProjectConnectionConfig(`

    `project_id="piltcuysvfidhkzzfinw",  project_name="Matrx Flow",`

    `region="us-east-1",     plan="free",     ipv4_addon=False,`

    `max_pg_connections=60,  user_conn_limit=57,`

    `pool_mode="session",    pool_min=2,  pool_max=10,`

    `queue_threshold=46,`

    `host="aws-0-us-east-1.pooler.supabase.com",  port=5432,`

    `direct_host=None,`

  `),`

  `# my-matrx and matrx-dm follow same pattern as matrx-flow`

  `# (us-west-1 and us-west-2 pooler hosts respectively)`

`}`

# **6\. Adaptive Queuing Logic**

The ORM should monitor active connection count against queue\_threshold and gate new work accordingly. The goal: never queue unnecessarily, but never exhaust the pool either.

## **6a. Decision Tree**

* If active\_connections \< queue\_threshold → execute immediately, no queuing

* If active\_connections \>= queue\_threshold AND work is low-priority/batch → enqueue, wait for slot

* If active\_connections \>= queue\_threshold AND work is real-time/user-facing → execute with reduced timeout, fail fast

* If active\_connections \>= user\_conn\_limit \- 2 → reject or circuit-break immediately, return 503

## **6b. Suggested Implementation**

`class AdaptiveConnectionGate:`

    `def __init__(self, config: ProjectConnectionConfig):`

        `self.config = config`

        `self._semaphore = asyncio.Semaphore(config.pool_max)`

        `self._queue: asyncio.Queue = asyncio.Queue()`

    `async def acquire(self, priority: str = 'normal') -> AsyncContextManager:`

        `active = await self._get_active_connections()`

        `if active >= self.config.user_conn_limit - 2:`

            `raise PoolExhaustedError(f'{self.config.project_name}: pool saturated')`

        `if active >= self.config.queue_threshold and priority == 'batch':`

            `await self._queue.put(asyncio.current_task())`

            `await asyncio.wait_for(self._semaphore.acquire(), timeout=30)`

        `else:`

            `await asyncio.wait_for(self._semaphore.acquire(), timeout=5)`

        `return self._connection_context()`

## **6c. Polling Active Connections**

The ORM should periodically (every 10-15s) query pg\_stat\_activity to get a fresh connection count and update the gate. Do not query this on every request — use a cached value with a TTL:

`SELECT count(*) FROM pg_stat_activity`

`WHERE state IS NOT NULL AND pid <> pg_backend_pid();`

# **7\. Special Case: Running Migrations**

Migrations must use direct Postgres (port 5432 on db.\[ref\]). Supavisor in transaction mode does not support SET LOCAL, advisory locks, or multi-statement transaction blocks that many migration tools rely on.

Rule: migrations always bypass the ORM pool and use a dedicated short-lived direct connection. For free tier projects without IPv4 add-on, migrations must run from an IPv6-capable environment (CI/CD runner, VPS, or Supabase MCP tool) — not from a typical developer machine on a home/office IPv4 network.

* automation-matrix: direct connection available from any network (IPv4 add-on)

* All free tier projects: use Supabase MCP / dashboard SQL editor / IPv6 runner for migrations

* ORM should expose a separate migrate\_connection() context that returns a direct connection and bypasses the pool gate

# **8\. Upgrade Path**

If free tier projects start needing higher concurrency, options in order of cost:

* Add IPv4 add-on ($4/mo per project) — enables direct connections from IPv4 networks, no capacity increase

* Upgrade to Pro plan (\~$25/mo base) — unlocks compute upgrades

* Upgrade compute to Small ($10/mo) — raises max\_connections from 60 → 90

* Upgrade compute to Medium ($50/mo) — raises max\_connections to 120

For batch-heavy workloads on any tier: the transaction pooler (port 6543\) is free and available now on all projects. It is the single highest-leverage change available at zero cost.

# **9\. Summary Decision Matrix**

| Scenario | automation-matrix | Free Tier Projects | Action Required |
| :---- | :---- | :---- | :---- |
| Normal ORM queries | `Transaction pooler :6543` | `Session pooler :5432` | Use pooler host, not db. host |
| Large batch job | `Transaction pooler :6543 + queue gate` | `Session pooler :5432 + queue gate` | Enable queuing at 80% threshold |
| Database migration | `Direct :5432 (IPv4 OK)` | `Supabase MCP / IPv6 runner` | Never run via Supavisor |
| Pool exhausted | Circuit break, 503, alert | Circuit break, 503, alert | ORM raises PoolExhaustedError |

Document generated from live Supabase MCP data — March 2026\. Update ProjectConnectionConfig entries if plans, compute tier, or IPv4 add-ons change.