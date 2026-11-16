import os
import sqlite3
from contextlib import contextmanager
from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)
MAX_TITLE_LENGTH = 200

# Stage 0: absolute path, so tasks.db always lives next to app.py
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db():
    """Commit on success, roll back on error, always close the connection."""
    conn = get_conn()
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def row_to_task(row):
    """Convert a database row to the API shape (done as true/false)."""
    return {'id': row['id'], 'title': row['title'], 'done': bool(row['done'])}

def init_db():
    with db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
            )
        ''')
        count = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        if count == 0:  # seed only on an empty table
            conn.executemany(
                'INSERT INTO tasks (title, done) VALUES (?, ?)',
                [('Buy milk', 0), ('Walk the dog', 1), ('Do homework', 0)],
            )

init_db()


@app.route('/')
def home():
    """
    Get API information
    ---
    responses:
      200:
        description: API information
        schema:
          type: object
          properties:
            name:
              type: string
            version:
              type: string
            endpoints:
              type: array
              items:
                type: string
    """
    return jsonify({
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    })


@app.route('/health')
def health():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Server is healthy
        schema:
          type: object
          properties:
            status:
              type: string
    """
    return jsonify({"status": "ok"})


@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    """
    Get all tasks
    ---
    responses:
      200:
        description: List of all tasks
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              done:
                type: boolean
            example:
              id: 1
              title: "Buy milk"
              done: false
    """
    with db() as conn:
        rows = conn.execute('SELECT * FROM tasks ORDER BY id').fetchall()
    return jsonify([row_to_task(r) for r in rows]), 200
  
  
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Get a single task by ID
    ---
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: The task ID
    responses:
      200:
        description: A single task
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            done:
              type: boolean
          example:
            id: 1
            title: "Buy milk"
            done: false
      404:
        description: Task not found
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: "Task 999 not found"
    """
    with db() as conn:
        row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(row_to_task(row)), 200


@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Create a new task and insert into database
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              description: The task title (required, max 200 characters)
              example: "Buy groceries"
            done:
              type: boolean
              description: Task completion status (optional, defaults to false)
              example: false
    responses:
      201:
        description: Task created successfully and inserted into database
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Unique task ID (auto-generated)
            title:
              type: string
              description: Task title
            done:
              type: boolean
              description: Task completion status
          example:
            id: 4
            title: "Buy groceries"
            done: false
      400:
        description: Bad request - invalid input
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: "Title is required"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.get_json(silent=True) or {}
    title = data.get('title')
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400
    title = title.strip()
    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({"error": f"Title must be {MAX_TITLE_LENGTH} characters or fewer"}), 400

    with db() as conn:
        cursor = conn.execute('INSERT INTO tasks (title, done) VALUES (?, ?)', (title, 0))
        new_id = cursor.lastrowid
    return jsonify({"id": new_id, "title": title, "done": False}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a task by ID
    ---
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: The task ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: The task title
              example: "Buy milk"
            done:
              type: boolean
              description: Task completion status
              example: true
    responses:
      200:
        description: Task updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            done:
              type: boolean
          example:
            id: 1
            title: "Buy milk"
            done: true
      400:
        description: Bad request - invalid input
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: "Title cannot be empty"
      404:
        description: Task not found
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: "Task 999 not found"
    """
    with db() as conn:
        row = conn.execute('SELECT id, title, done FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if row is None:
            return jsonify({"error": f"Task {task_id} not found"}), 404

        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be JSON"}), 400

        new_title = row['title']
        new_done = bool(row['done'])

        if 'title' in data:
            title = data['title']
            if not isinstance(title, str) or not title.strip():
                return jsonify({"error": "Title cannot be empty or whitespace"}), 400
            new_title = title.strip()

        if 'done' in data:
            if not isinstance(data['done'], bool):
                return jsonify({"error": "Done must be a boolean (true/false)"}), 400
            new_done = data['done']

        conn.execute(
            'UPDATE tasks SET title = ?, done = ? WHERE id = ?',
            (new_title, int(new_done), task_id),
        )
    return jsonify({'id': task_id, 'title': new_title, 'done': new_done}), 200


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task by ID
    ---
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: The task ID
    responses:
      204:
        description: Task deleted successfully (no content)
      404:
        description: Task not found
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: "Task 999 not found"
    """
    with db() as conn:
        row = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if row is None:
            return jsonify({"error": f"Task {task_id} not found"}), 404
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    return '', 204


if __name__ == '__main__':
    app.run(debug=True, port=8000)