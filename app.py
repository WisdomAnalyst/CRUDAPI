from flask import Flask, jsonify, request
from flasgger import Swagger
import sqlite3

app = Flask(__name__)
swagger = Swagger(app)

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT 0
        )
    ''')
    
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



tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Do homework", "done": False}
]

next_id = 4


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
    for task in tasks:
        if task['id'] == task_id:
            return jsonify(task)
    
    return jsonify({"error": f"Task {task_id} not found"}), 404


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    # Validation 
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    title = data['title'].strip()
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    # INSERT into database
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, done) VALUES (?, ?)',
        (title, False)
    )
    conn.commit()
    
    # Get the ID the database assigned
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'id': new_id,
        'title': title,
        'done': False
    }), 201
    
      
      
    """
    Create a new task
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
              description: The task title
              example: "Buy milk"
    responses:
      201:
        description: Task created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Unique task ID
            title:
              type: string
              description: Task title
            done:
              type: boolean
              description: Task completion status
          example:
            id: 4
            title: "Buy milk"
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
    """
    global next_id
    
    
    data = request.get_json()
    
    
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    
    if 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    
    title = data['title']
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title cannot be empty or whitespace"}), 400
    
    
    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }
    
    
    tasks.append(new_task)
    
    
    next_id += 1
    
    
    return jsonify(new_task), 201




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
    # Find the task
    task = None
    for t in tasks:
        if t['id'] == task_id:
            task = t
            break
    
    # If task doesn't exist
    if not task:
        return jsonify({"error": f"Task {task_id} not found"}), 404
    
    # Get JSON data
    data = request.get_json()
    
    # Validation: Check if JSON was sent
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    # Update title if provided
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Title cannot be empty or whitespace"}), 400
        task['title'] = title.strip()
    
    # Update done if provided
    if 'done' in data:
        if not isinstance(data['done'], bool):
            return jsonify({"error": "Done must be a boolean (true/false)"}), 400
        task['done'] = data['done']
    
    # Return updated task
    return jsonify(task), 200

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
    # Find the task
    task = None
    for t in tasks:
        if t['id'] == task_id:
            task = t
            break
    
    # If task doesn't exist
    if not task:
        return jsonify({"error": f"Task {task_id} not found"}), 404
    
    # Remove the task
    tasks.remove(task)
    
    # Return 204 No Content (empty body)
    return '', 204


if __name__ == '__main__':
    app.run(debug=True, port=8000)
    
    