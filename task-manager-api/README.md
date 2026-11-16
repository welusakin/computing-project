# Task Manager REST API

The full public source is maintained in [welusakin/task-manager](https://github.com/welusakin/task-manager). That repository contains the Flask application, SQLAlchemy models, SQLite persistence, route and service modules, request validation, JSON error handling, filtering, sorting, and notification-preference endpoints.

## Stack

- Python and Flask for HTTP routing
- SQLAlchemy for persistence models and database access
- SQLite for a lightweight local database
- JSON request and response bodies

## API capabilities

- Create, read, update, and delete users and tasks
- Validate required task fields, priorities, statuses, and user references
- Filter tasks by user, status, or priority and sort results by supported fields
- Store per-user notification preferences
- Return consistent JSON error bodies for invalid requests and missing records

See the repository README for installation, endpoint examples, and the current source tree.
