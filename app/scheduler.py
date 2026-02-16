from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter

scheduler = None


def init_scheduler(app):
    """Initialize the background scheduler for recurring tasks"""
    global scheduler
    
    if scheduler is not None:
        return
    
    scheduler = BackgroundScheduler()
    
    # Run task generation daily at midnight
    scheduler.add_job(
        func=lambda: generate_daily_tasks(app),
        trigger=CronTrigger(hour=0, minute=0),
        id='daily_task_generation',
        name='Generate daily recurring tasks',
        replace_existing=True
    )
    
    scheduler.start()
    
    # Generate tasks for the next 7 days on startup
    with app.app_context():
        generate_tasks_for_range(
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )


def generate_daily_tasks(app):
    """Generate recurring tasks for the next 7 days"""
    with app.app_context():
        generate_tasks_for_range(
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )


def generate_tasks_for_range(start_date, end_date):
    """Generate task instances from templates for a date range"""
    from app import db
    from app.models import Task, TaskTemplate
    
    templates = TaskTemplate.query.filter_by(is_active=True).all()
    generated_count = 0
    
    for template in templates:
        occurrences = template.get_occurrences_in_range(start_date, end_date)
        
        for occurrence in occurrences:
            # Check if task already exists for this template and date
            existing = Task.query.filter_by(
                template_id=template.id,
                due_date=occurrence.date()
            ).first()
            
            if not existing:
                task = Task(
                    title=template.title,
                    description=template.description,
                    due_date=occurrence.date(),
                    due_time=occurrence.time(),
                    template_id=template.id
                )
                db.session.add(task)
                generated_count += 1
    
    db.session.commit()
    return generated_count


def parse_cron_expression(cron_expr):
    """Validate and parse a cron expression, returns helpful error or None if valid"""
    try:
        # Test the cron expression
        croniter(cron_expr, datetime.now())
        return None  # Valid
    except (ValueError, KeyError) as e:
        return str(e)


def get_next_occurrences(cron_expr, count=5):
    """Get the next N occurrences for a cron expression"""
    try:
        cron = croniter(cron_expr, datetime.now())
        return [cron.get_next(datetime) for _ in range(count)]
    except (ValueError, KeyError):
        return []
