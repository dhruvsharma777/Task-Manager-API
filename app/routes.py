from flask import request, jsonify, Blueprint, redirect, url_for
from app import db
from app.models import Task
from app.utils import token_required

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Redirects to the API documentation."""
    return redirect('/apidocs')

@bp.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    """
    Create a new task
    This endpoint creates a new task for the authenticated user.
    ---
    security:
      - bearerAuth: []
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
              description: The title of the task.
            description:
              type: string
              description: A detailed description of the task.
    responses:
      201:
        description: Task created successfully.
        schema:
          $ref: '#/definitions/Task'
      400:
        description: Bad request (e.g., missing title).
      401:
        description: Unauthorized (invalid or missing token).
    definitions:
      Task:
        type: object
        properties:
          id:
            type: integer
          title:
            type: string
          description:
            type: string
          completed:
            type: boolean
          created_at:
            type: string
            format: date-time
          updated_at:
            type: string
            format: date-time
          user_id:
            type: integer
    """
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400

    new_task = Task(
        title=data['title'],
        description=data.get('description', ""),
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201

@bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    """
    Get all tasks with filtering and pagination
    Retrieves a list of tasks for the authenticated user, with options for pagination and filtering by completion status.
    ---
    security:
      - bearerAuth: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: The page number for pagination.
      - name: per_page
        in: query
        type: integer
        default: 10
        description: The number of items per page.
      - name: completed
        in: query
        type: boolean
        description: Filter tasks by their completion status (true/false).
    responses:
      200:
        description: A paginated list of tasks.
        schema:
          type: object
          properties:
            tasks:
              type: array
              items:
                $ref: '#/definitions/Task'
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
      401:
        description: Unauthorized (invalid or missing token).
    """
   
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
   
    query = Task.query.filter_by(user_id=current_user.id)
    if 'completed' in request.args:
        is_completed = request.args.get('completed').lower() in ['true', '1', 't']
        query = query.filter_by(completed=is_completed)

    paginated_tasks = query.paginate(page=page, per_page=per_page, error_out=False)
    tasks = [task.to_dict() for task in paginated_tasks.items]

    return jsonify({
        'tasks': tasks,
        'total': paginated_tasks.total,
        'pages': paginated_tasks.pages,
        'current_page': paginated_tasks.page
    })

@bp.route('/tasks/<int:id>', methods=['GET'])
@token_required
def get_task(current_user, id):
    """
    Get a single task by ID
    Retrieves the details of a specific task belonging to the authenticated user.
    ---
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The unique ID of the task to retrieve.
    responses:
      200:
        description: Task details retrieved successfully.
        schema:
          $ref: '#/definitions/Task'
      401:
        description: Unauthorized (invalid or missing token).
      404:
        description: Task not found.
    """
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return jsonify(task.to_dict())

@bp.route('/tasks/<int:id>', methods=['PUT'])
@token_required
def update_task(current_user, id):
    """
    Update a task
    Updates the details of an existing task.
    ---
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The unique ID of the task to update.
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: The new title for the task.
            description:
              type: string
              description: The new description for the task.
            completed:
              type: boolean
              description: The new completion status for the task.
    responses:
      200:
        description: Task updated successfully.
        schema:
          $ref: '#/definitions/Task'
      400:
        description: Bad request (e.g., invalid data).
      401:
        description: Unauthorized (invalid or missing token).
      404:
        description: Task not found.
    """
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    
    db.session.commit()
    return jsonify(task.to_dict())

@bp.route('/tasks/<int:id>', methods=['DELETE'])
@token_required
def delete_task(current_user, id):
    """
    Delete a task
    Deletes a specific task by its ID.
    ---
    security:
      - bearerAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The unique ID of the task to delete.
    responses:
      200:
        description: Task deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Task deleted successfully
      401:
        description: Unauthorized (invalid or missing token).
      404:
        description: Task not found.
    """
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200