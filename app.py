from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# In-memory task storage
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Do homework", "done": False}
]

# Track next available ID
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


if __name__ == '__main__':
    app.run(debug=True, port=8000)