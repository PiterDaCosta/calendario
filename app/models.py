from app import db
from datetime import datetime, date
from croniter import croniter


class TaskTemplate(db.Model):
    """Template for recurring tasks with cron-like scheduling"""
    __tablename__ = 'task_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cron_schedule = db.Column(db.String(100), nullable=False)  # Cron expression
    start_date = db.Column(db.Date, nullable=True)  # When recurrence starts (null = no limit)
    end_date = db.Column(db.Date, nullable=True)    # When recurrence ends (null = no limit)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to generated tasks
    tasks = db.relationship('Task', backref='template', lazy='dynamic')
    
    def get_next_occurrence(self, from_date=None):
        """Get the next occurrence based on cron schedule"""
        if from_date is None:
            from_date = datetime.now()
        try:
            cron = croniter(self.cron_schedule, from_date)
            return cron.get_next(datetime)
        except (ValueError, KeyError):
            return None
    
    def get_occurrences_in_range(self, start_date, end_date):
        """Get all occurrences within a date range, respecting template start/end dates"""
        occurrences = []
        
        # Adjust range based on template's start/end dates
        effective_start = start_date
        effective_end = end_date
        
        if self.start_date:
            template_start = datetime.combine(self.start_date, datetime.min.time())
            effective_start = max(start_date, template_start)
        
        if self.end_date:
            template_end = datetime.combine(self.end_date, datetime.max.time())
            effective_end = min(end_date, template_end)
        
        # If the effective range is invalid, return empty
        if effective_start > effective_end:
            return occurrences
        
        try:
            cron = croniter(self.cron_schedule, effective_start)
            while True:
                next_time = cron.get_next(datetime)
                if next_time > effective_end:
                    break
                occurrences.append(next_time)
        except (ValueError, KeyError):
            pass
        return occurrences
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'cron_schedule': self.cron_schedule,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Task(db.Model):
    """Individual task instance (can be standalone or from a template)"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    due_time = db.Column(db.Time)  # Optional specific time
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    priority = db.Column(db.Integer, default=2)  # 1=High, 2=Medium, 3=Low
    
    # Link to template (null for standalone tasks)
    template_id = db.Column(db.Integer, db.ForeignKey('task_templates.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def toggle_complete(self):
        """Toggle the completion status"""
        self.is_completed = not self.is_completed
        self.completed_at = datetime.utcnow() if self.is_completed else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'due_time': self.due_time.isoformat() if self.due_time else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'priority': self.priority,
            'template_id': self.template_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Common cron schedule presets for UI
CRON_PRESETS = {
    'daily': '0 9 * * *',           # Every day at 9 AM
    'weekdays': '0 9 * * 1-5',       # Monday to Friday at 9 AM
    'weekly_monday': '0 9 * * 1',    # Every Monday at 9 AM
    'weekly_friday': '0 9 * * 5',    # Every Friday at 9 AM
    'biweekly': '0 9 * * 1/2',       # Every other Monday
    'monthly_first': '0 9 1 * *',    # First day of month at 9 AM
    'monthly_last': '0 9 L * *',     # Last day of month at 9 AM
    'quarterly': '0 9 1 */3 *',      # First day of quarter at 9 AM
}
