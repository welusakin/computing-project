# task-manager

REST API for tasks and users (Flask, SQLAlchemy, SQLite).

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    pytest -q
    flask --app app run

## API

| Method | Path | Notes |
|---|---|---|
| POST | `/tasks` | `title` required; optional `description`, `priority`, `user_id` |
| GET | `/tasks` | optional filters `?done=true|false` and `?priority={n}`; optional `?sort=priority` |
| GET | `/tasks/{id}` | |
| PATCH | `/tasks/{id}` | any of `title`, `description`, `done`, `priority`, `user_id` |
| DELETE | `/tasks/{id}` | |
| POST | `/users` | `name`, `email` |
| GET | `/users` | |
| GET | `/users/{id}` | |

### Priority

`priority` is an integer from 1 to 5 (1 = urgent, 5 = low). It is optional on
create and defaults to 3. `PATCH` accepts it; a `null` priority on `PATCH` is
ignored and the stored value is kept. `GET /tasks?priority={n}` returns only
tasks with that priority. `GET /tasks?sort=priority` orders the list by
priority (1 first), then id; without it the list is ordered by id. Anything outside 1–5, or not an integer, returns 422.

## Source in this project

The complete application and its tests are included in this folder. The standalone public repository is [welusakin/task-manager](https://github.com/welusakin/task-manager).
