# Task Calendar

A task management application with weekly/monthly views, recurring tasks with cron-like scheduling, and print-friendly outputs.

## Features

- **Weekly View**: See all tasks for the current week with checkboxes to mark completion
- **Monthly View**: Calendar-style overview of the entire month
- **Recurring Tasks**: Define tasks that repeat on a schedule using cron expressions
- **Mobile-Friendly**: Responsive design that works on phones, tablets, and desktops
- **Print Support**: Clean print layouts for weekly and monthly views
- **PWA Ready**: Basic Progressive Web App support for installation on devices

## Tech Stack

- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (easily swappable to PostgreSQL/MySQL)
- **Frontend**: Vanilla JavaScript with responsive CSS
- **Scheduling**: APScheduler with croniter for cron expression parsing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Create a virtual environment**:
   ```bash
   cd calendar
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Open in browser**:
   Navigate to `http://localhost:5000`

## Usage

### Creating Tasks

1. Click the **"+ Add Task"** button or click on any day
2. Fill in the task details:
   - Title (required)
   - Description (optional)
   - Due date and time
   - Priority (High/Medium/Low)
3. Click **Save Task**

### Managing Recurring Tasks

1. Navigate to **Recurring Tasks** in the navigation
2. Click **"+ New Template"**
3. Enter the task details and schedule:
   - Use a preset schedule (Daily, Weekdays, Weekly, Monthly)
   - Or enter a custom cron expression

### Cron Expression Format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun-Sat)
│ │ │ │ │
* * * * *
```

**Examples**:
- `0 9 * * *` - Every day at 9:00 AM
- `0 9 * * 1-5` - Weekdays at 9:00 AM
- `0 9 * * 1` - Every Monday at 9:00 AM
- `0 9 1 * *` - First day of every month at 9:00 AM
- `0 9 * * 1,3,5` - Monday, Wednesday, Friday at 9:00 AM

### Printing

1. Navigate to the Weekly or Monthly view you want to print
2. Click the **print icon** in the navigation bar
3. Use your browser's print dialog to print or save as PDF

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks (with optional date filters) |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/<id>` | Get a specific task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |
| POST | `/api/tasks/<id>/toggle` | Toggle task completion |

### Task Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | List all templates |
| POST | `/api/templates` | Create a new template |
| GET | `/api/templates/<id>` | Get a specific template |
| PUT | `/api/templates/<id>` | Update a template |
| DELETE | `/api/templates/<id>` | Delete a template |
| POST | `/api/templates/<id>/toggle` | Toggle template active status |
| GET | `/api/templates/presets` | Get available cron presets |

### Calendar

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/week?date=YYYY-MM-DD` | Get week data |
| GET | `/api/calendar/month?year=YYYY&month=MM` | Get month data |
| POST | `/api/generate-recurring` | Generate recurring tasks |

## Project Structure

```
calendar/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── models.py        # Database models
│   ├── routes.py        # API and view routes
│   └── scheduler.py     # Recurring task scheduler
├── static/
│   ├── css/
│   │   ├── style.css    # Main styles
│   │   └── print.css    # Print-friendly styles
│   └── js/
│       ├── app.js       # Main JavaScript
│       └── sw.js        # Service worker (PWA)
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Weekly view
│   ├── monthly.html     # Monthly view
│   ├── templates.html   # Recurring tasks management
│   ├── print_weekly.html
│   └── print_monthly.html
├── requirements.txt
├── run.py               # Application entry point
└── README.md
```

## Deployment

### Using Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key...` |
| `DATABASE_URL` | Database connection URL | `sqlite:///tasks.db` |

## Future Enhancements

- [ ] React frontend for enhanced interactivity
- [ ] User authentication
- [ ] Task categories/tags
- [ ] Calendar export (iCal format)
- [ ] Email/push notifications
- [ ] Dark mode
- [ ] Drag-and-drop task reordering
- [ ] Task search and filtering

## License

MIT License - Feel free to use and modify as needed.
