# Insert handler and mixin architecture design

## 1. Goals and constraints

**Goals**

- **Unify** all “insert” operations behind a single, coherent API.
- **Modularize** logic so each domain (messages, nodes, devices, etc.) lives in its own file and class.
- **Preserve flexibility** for future growth (new insert types, new modules, new handlers).
- **Support both styles** of access:
  - Member-method style: `handlers.insert_message(msg)`
  - Dictionary-style dispatch: `handlers["insert_message"](msg)` or `handlers["insertMessage"](msg)`
- **Avoid dynamic binding hacks** (no `setattr` with closures, no global handler dicts at runtime).

**Constraints**

- Existing code and mental model already use per-domain files like `message_inserts.py`, `node_inserts.py`.
- We want to keep filenames as `*_inserts.py`.
- DB access is via a shared `db` connection; new design should use `self.db`, not global imports.
- Some handler names historically used camelCase (`insertMessage`); new design prefers snake_case (`insert_message`) but should offer backward compatibility where it’s cheap.

---

## 2. High-level architecture

### 2.1 Core concept

We define:

1. **Per-domain mixin classes** (e.g., `MessageInserts`, `NodeInserts`, `MetricInserts`) that encapsulate related “insert” operations as **instance methods**.

2. A single **aggregator class** `InsertHandlers` that:
   - Inherits from all `*Inserts` mixins.
   - Holds the shared `db` connection.
   - Provides dictionary-like access (`__getitem__`, `__contains__`, `__iter__`).
   - Optionally enforces name consistency and catches conflicts.

The result is:

- **Logical separation by domain** (files/classes).
- **Unified runtime entry point** (`InsertHandlers` instance).
- No more module-level `*_inserts = {...}` dicts.
- No more global `db` imports in insert modules.

---

## 3. Module-level structure

### 3.1 Directory layout

All insert-related logic lives under `src/db`:

```text
src/
  db/
    inserts/
      message_inserts.py
      channel_inserts.py
      config_inserts.py
      contact_inserts.py
      device_inserts.py
      diagnostic_inserts.py
      metric_inserts.py
      node_inserts.py
    insert_handlers.py
# Query handler and mixin architecture design

## 1. Goals and relationship to InsertHandlers

We want the query side to mirror the insert side you just finished:

- **Per-domain query classes** (e.g., `ConfigQueries`, `NodeQueries`) living in `src/db/queries/`.
- A single **aggregator** `QueryHandlers` one directory up (`src/db/query_handlers.py`).
- Support both:
  - **Method-style** access: `queries.list_nodes()`
  - **Dictionary-style** dispatch: `queries["list_nodes"](…)`
- Remove:
  - Global `db` imports inside query functions in favor of `self.db`.
  - The global `query_handlers` dict and `handle_query` function.

This keeps the architecture symmetric:

- Inserts: `*Inserts` + `InsertHandlers`
- Queries: `*Queries` + `QueryHandlers`

---

## 2. Directory and file structure

### 2.1 Final layout

```text
src/
  db/
    queries/
      config_queries.py
      contact_queries.py
      device_queries.py
      diagnostic_queries.py
      message_queries.py
      metric_queries.py
      node_queries.py
    query_handlers.py
