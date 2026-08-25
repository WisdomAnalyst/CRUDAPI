from flask import Flask, jsonify, request
from flasgger import Swagger
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)
swagger = Swagger(app)

# ADD THIS LINE:
MAX_TITLE_LENGTH = 200

def init_db():
    """Initialize the database with tasks table and sample data"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT 0
        )
    ''')
    
    # Count rows first
    cursor.execute('SELECT COUNT(*) FROM tasks')
    if cursor.fetchone()[0] == 0: 
        cursor.executemany(
            'INSERT INTO tasks (title, done) VALUES (?, ?)',
            [
                ('Buy milk', 0),
                ('Walk the dog', 1),
                ('Do homework', 0)
            ]
        )
    
    conn.commit()
    conn.close()

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
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, done FROM tasks ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    
    tasks = [dict(row) for row in rows]
    return jsonify(tasks)


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
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, done FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return jsonify({"error": f"Task {task_id} not found"}), 404
    
    return jsonify(dict(row))


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
    # We'll fill this in next
    pass

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
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, done FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return jsonify({"error": f"Task {task_id} not found"}), 404
    
    data = request.get_json()
    
    if not data:
        conn.close()
        return jsonify({"error": "Request body must be JSON"}), 400
    
    new_title = row['title']
    new_done = row['done']
    
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str) or not title.strip():
            conn.close()
            return jsonify({"error": "Title cannot be empty or whitespace"}), 400
        new_title = title.strip()
    
    if 'done' in data:
        if not isinstance(data['done'], bool):
            conn.close()
            return jsonify({"error": "Done must be a boolean (true/false)"}), 400
        new_done = data['done']
    
    cursor.execute(
        'UPDATE tasks SET title = ?, done = ? WHERE id = ?',
        (new_title, int(new_done), task_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': task_id,
        'title': new_title,
        'done': bool(new_done)
    }), 200


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
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return jsonify({"error": f"Task {task_id} not found"}), 404
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return '', 204


if __name__ == '__main__':
    app.run(debug=True, port=8000)