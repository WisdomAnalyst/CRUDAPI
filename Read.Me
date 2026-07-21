




# Task API

A minimal Flask REST API for managing tasks with automatic Swagger documentation.

## Installation

```bash
pip install flask flasgger

2. Run
python app.py
3. View API Documentation
Open your browser and go to:

http://localhost:8000/apidocs/
You'll see an interactive interface where you can test all features without writing code.

What Can You Do?
View all tasks - See your complete to-do list
View one task - Look up a specific task by its ID
Add a task - Create a new task to your list
Update a task - Change a task's title or mark it as done
Delete a task - Remove a task from your list
Check if API is running - Health check endpoint



Prompt:

Create a professional Flask REST API for a task management system with the following requirements:

Core Functionality
Build a complete CRUD API for managing tasks
Each task has: id (integer), title (string), done (boolean)
Pre-populate with 3 sample tasks (ids 1-3)
Use auto-incrementing IDs starting from 4

API Endpoints Required
1. GET / - Return API metadata (name, version, endpoints list)
2. GET /health - Health check endpoint
3. GET /tasks - Retrieve all tasks
4. GET /tasks/<id> - Retrieve a single task by ID (return 404 if not found)
5. POST /tasks - Create a new task (return 201 on success)
6. PUT /tasks/<id> - Update a task (partial updates allowed, return 200)
7. DELETE /tasks/<id> - Delete a task (return 204 on success)

Code Quality & Organization
Extract repeated logic into helper functions (e.g., finding tasks)
Create a separate validation function for title validation
Use clear section comments to organize code (In-memory storage, Helper functions, Routes)
Add inline comments explaining non-obvious logic
Follow PEP 8 style guide (double quotes, consistent spacing)

Validation Requirements
Title is required (cannot be missing)
Title must be a string (not null, number, or other type)
Title cannot be empty or contain only whitespace (must be trimmed)
The "done" field must be a boolean (true/false) when provided
Request body must be valid JSON (handle malformed JSON gracefully)
Return appropriate 400 error responses with descriptive messages

Error Handling
Use request.get_json(silent=True) to prevent crashes on malformed JSON
Return 404 with error message when task not found
Return 400 with descriptive error messages for validation failures
Include error examples in Swagger documentation

Documentation & Swagger Integration
Use Flasgger for automatic Swagger/OpenAPI documentation
Add docstrings to every route with Swagger YAML
Organize endpoints with tags (Meta, Tasks) for better UI organization
Include detailed parameter descriptions
Provide example request/response bodies in documentation
Show example error responses (404, 400)
Include multiline descriptions with JSON examples

HTTP Status Codes
200 for successful GET, PUT operations
201 for successful POST (resource created)
204 for successful DELETE (no content)
400 for validation/bad request errors
404 for resource not found

Data Storage
Use in-memory list (no database required)
Use global next_id counter for auto-incrementing IDs
Data persists during server runtime only

Server Configuration
Run on localhost:8000
Enable debug mode for development
Use Flask's built-in server



AI vs me


1. The AI extracted repeated logic into helper functions:

find_task(task_id) - Eliminates 3 duplicate loops
validate_title(title) - Centralizes validation logic
this helps to Reduces bugs from inconsistent implementations,
Makes testing easier (test the helper once vs. testing 3 endpoints)


2. Safer Error Handling
My code - can crash
data = request.get_json()  
# Raises exception on malformed JSON

AI code - graceful
data = request.get_json(silent=True)  # Returns None, doesn't crash
Real-world impact: If a client sends {title: "test"} (missing quotes), my code crashes with a 500 error. 
The AI's returns a clean 400 error.

3. AI code Return cleaned data from validators - Avoid redundant .strip() calls
