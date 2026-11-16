# Stage 4 notes

**Query:** `UPDATE tasks SET done = 1;`

**What it returned:** DB Browser reported the rows changed. After saving with Ctrl+S, `GET /tasks` showed every task as done with no server restart, because the API and DB Browser read the same `tasks.db` file.
