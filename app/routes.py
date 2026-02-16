from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, date, timedelta
from app import db
from app.models import Task, TaskTemplate, CRON_PRESETS

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


# ============ Main Routes (HTML) ============

@main_bp.route('/')
def index():
    """Main weekly view"""
    return render_template('index.html')


@main_bp.route('/monthly')
def monthly_view():
    """Monthly view"""
    return render_template('monthly.html')


@main_bp.route('/templates')
def templates_view():
    """Manage recurring task templates"""
    return render_template('templates.html')


@main_bp.route('/print/weekly')
def print_weekly():
    """Print-friendly weekly view"""
    return render_template('print_weekly.html')


@main_bp.route('/print/monthly')
def print_monthly():
    """Print-friendly monthly view"""
    return render_template('print_monthly.html')


# ============ API Routes ============

# --- Tasks API ---

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get tasks with optional date range filter"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Task.query
    
    if start_date:
        start = datetime.fromisoformat(start_date).date()
        query = query.filter(Task.due_date >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date).date()
        query = query.filter(Task.due_date <= end)
    
    tasks = query.order_by(Task.due_date, Task.due_time, Task.priority).all()
    return jsonify([task.to_dict() for task in tasks])


@api_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        due_date=datetime.fromisoformat(data['due_date']).date(),
        due_time=datetime.strptime(data['due_time'], '%H:%M').time() if data.get('due_time') else None,
        priority=data.get('priority', 2)
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']).date()
    if 'due_time' in data:
        task.due_time = datetime.strptime(data['due_time'], '%H:%M').time() if data['due_time'] else None
    if 'priority' in data:
        task.priority = data['priority']
    if 'is_completed' in data:
        task.is_completed = data['is_completed']
        task.completed_at = datetime.utcnow() if data['is_completed'] else None
    
    db.session.commit()
    return jsonify(task.to_dict())


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204


@api_bp.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    task.toggle_complete()
    db.session.commit()
    return jsonify(task.to_dict())


# --- Task Templates API ---

@api_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all task templates"""
    templates = TaskTemplate.query.order_by(TaskTemplate.created_at.desc()).all()
    return jsonify([t.to_dict() for t in templates])


@api_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new task template"""
    data = request.get_json()
    
    template = TaskTemplate(
        title=data['title'],
        description=data.get('description', ''),
        cron_schedule=data['cron_schedule'],
        start_date=datetime.fromisoformat(data['start_date']).date() if data.get('start_date') else None,
        end_date=datetime.fromisoformat(data['end_date']).date() if data.get('end_date') else None,
        is_active=data.get('is_active', True)
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify(template.to_dict()), 201


@api_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template"""
    template = TaskTemplate.query.get_or_404(template_id)
    return jsonify(template.to_dict())


@api_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update a template"""
    template = TaskTemplate.query.get_or_404(template_id)
    data = request.get_json()
    
    if 'title' in data:
        template.title = data['title']
    if 'description' in data:
        template.description = data['description']
    if 'cron_schedule' in data:
        template.cron_schedule = data['cron_schedule']
    if 'start_date' in data:
        template.start_date = datetime.fromisoformat(data['start_date']).date() if data['start_date'] else None
    if 'end_date' in data:
        template.end_date = datetime.fromisoformat(data['end_date']).date() if data['end_date'] else None
    if 'is_active' in data:
        template.is_active = data['is_active']
    
    db.session.commit()
    return jsonify(template.to_dict())


@api_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    template = TaskTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return '', 204


@api_bp.route('/templates/<int:template_id>/toggle', methods=['POST'])
def toggle_template(template_id):
    """Toggle template active status"""
    template = TaskTemplate.query.get_or_404(template_id)
    template.is_active = not template.is_active
    db.session.commit()
    return jsonify(template.to_dict())


@api_bp.route('/templates/<int:template_id>/regenerate', methods=['POST'])
def regenerate_template_tasks(template_id):
    """Regenerate future tasks for a template after it's been updated"""
    template = TaskTemplate.query.get_or_404(template_id)
    
    # Delete future incomplete tasks for this template
    today = date.today()
    Task.query.filter(
        Task.template_id == template_id,
        Task.due_date >= today,
        Task.is_completed == False
    ).delete()
    db.session.commit()
    
    # Regenerate tasks for the next 30 days
    from app.scheduler import generate_tasks_for_range
    end_date = datetime.now() + timedelta(days=30)
    count = generate_tasks_for_range(datetime.now(), end_date)
    
    return jsonify({'regenerated': count})


@api_bp.route('/templates/presets', methods=['GET'])
def get_cron_presets():
    """Get available cron schedule presets"""
    return jsonify(CRON_PRESETS)


# --- Calendar API ---

@api_bp.route('/calendar/week', methods=['GET'])
def get_week_data():
    """Get tasks for a specific week"""
    date_str = request.args.get('date', date.today().isoformat())
    target_date = datetime.fromisoformat(date_str).date()
    
    # Get the Monday of the week
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get existing tasks
    tasks = Task.query.filter(
        Task.due_date >= start_of_week,
        Task.due_date <= end_of_week
    ).order_by(Task.due_date, Task.due_time, Task.priority).all()
    
    # Organize tasks by day
    week_data = {}
    current = start_of_week
    while current <= end_of_week:
        week_data[current.isoformat()] = {
            'date': current.isoformat(),
            'day_name': current.strftime('%A'),
            'tasks': []
        }
        current += timedelta(days=1)
    
    for task in tasks:
        day_key = task.due_date.isoformat()
        if day_key in week_data:
            week_data[day_key]['tasks'].append(task.to_dict())
    
    return jsonify({
        'start_date': start_of_week.isoformat(),
        'end_date': end_of_week.isoformat(),
        'days': list(week_data.values())
    })


@api_bp.route('/calendar/month', methods=['GET'])
def get_month_data():
    """Get tasks for a specific month"""
    year = int(request.args.get('year', date.today().year))
    month = int(request.args.get('month', date.today().month))
    
    # Get first and last day of month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get tasks for the month
    tasks = Task.query.filter(
        Task.due_date >= first_day,
        Task.due_date <= last_day
    ).order_by(Task.due_date, Task.due_time, Task.priority).all()
    
    # Organize tasks by day
    month_data = {}
    current = first_day
    while current <= last_day:
        month_data[current.isoformat()] = {
            'date': current.isoformat(),
            'day': current.day,
            'day_name': current.strftime('%A'),
            'tasks': []
        }
        current += timedelta(days=1)
    
    for task in tasks:
        day_key = task.due_date.isoformat()
        if day_key in month_data:
            month_data[day_key]['tasks'].append(task.to_dict())
    
    return jsonify({
        'year': year,
        'month': month,
        'month_name': first_day.strftime('%B'),
        'first_day': first_day.isoformat(),
        'last_day': last_day.isoformat(),
        'days': list(month_data.values())
    })


@api_bp.route('/generate-recurring', methods=['POST'])
def generate_recurring_tasks():
    """Manually trigger generation of recurring tasks for a date range"""
    data = request.get_json()
    start_date = datetime.fromisoformat(data['start_date'])
    end_date = datetime.fromisoformat(data['end_date'])
    
    from app.scheduler import generate_tasks_for_range
    count = generate_tasks_for_range(start_date, end_date)
    
    return jsonify({'generated': count})
