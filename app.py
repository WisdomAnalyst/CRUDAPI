from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)


tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Do homework", "done": False}
]


@app.route('/')
def home():
    """
    Get API information
    ---
    responses:
      200:
        description: API information
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
            properties:
              id:
                type: integer
              title:
                type: string
              done:
                type: boolean
    """
    return jsonify(tasks)

# Endpoint 4: Get ONE task by ID
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
      404:
        description: Task not found
    """
    # Search for the task
    for task in tasks:
        if task['id'] == task_id:
            return jsonify(task)
    
    # If we get here, task wasn't found
    return jsonify({"error": f"Task {task_id} not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)