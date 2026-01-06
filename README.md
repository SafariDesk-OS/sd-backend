# SafariDesk Backend

A powerful, modern helpdesk and ticketing system backend built with Django REST Framework. SafariDesk provides comprehensive ticket management, SLA tracking, knowledge base, task management, and team collaboration features.

## 🚀 Features

### Ticket Management
- **Multi-channel Support**: Email, Web Portal, Phone, Chat, Chatbot, API, and Internal ticket creation
- **Smart Assignment**: Auto-assignment, manual assignment, and assignment rules
- **Status Tracking**: Customizable ticket statuses with workflow automation
- **Priority Management**: Critical, High, Medium, and Low priority levels
- **Ticket Merging**: Combine duplicate or related tickets
- **Bulk Operations**: Archive, delete, restore, and export tickets in bulk
- **Advanced Filtering**: Filter by status, priority, assignee, department, category, and date ranges

### SLA (Service Level Agreement)
- **Flexible SLA Policies**: Define multiple SLA policies with different targets
- **Priority-based Targets**: Different resolution times per priority level
- **Business Hours**: Calendar hours, business hours, or custom operational hours
- **SLA Configuration**: Enable/disable SLA tracking system-wide
- **Breach Detection**: Automatic detection and notification of SLA breaches
- **Holiday Management**: Account for holidays in SLA calculations

### Task Management
- **Linked Tasks**: Attach tasks to tickets for detailed work tracking
- **Task Status**: Track task progress independently
- **Assignment**: Assign tasks to specific team members
- **Comments**: Collaborate on tasks with comments and attachments

### Knowledge Base
- **Category Management**: Organize articles in hierarchical categories
- **Rich Content**: Full WYSIWYG editor support for articles
- **Search**: Powerful full-text search across articles
- **Public/Private**: Control article visibility
- **Analytics**: Track article views and popularity

### Team Collaboration
- **Departments**: Organize agents by department
- **Role-based Access**: Admin, Agent, and Customer roles
- **Watchers**: Add team members to follow ticket updates
- **Internal Notes**: Private comments visible only to agents
- **@Mentions**: Mention team members in comments for notifications

### Notifications & Communication
- **Email Integration**: SMTP configuration for email notifications
- **Real-time Updates**: WebSocket support for live updates
- **Email Replies**: Reply to tickets directly from email
- **Notification Preferences**: Customizable notification settings per user

### Security & Multi-tenancy
- **Multi-tenant Architecture**: Support multiple businesses/workspaces
- **Authentication**: JWT-based authentication with OTP verification
- **Password Security**: Secure password hashing and reset flows
- **Domain Verification**: Verify business domain ownership
- **Permission System**: Granular permission controls

## 🛠️ Technology Stack

- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL (primary), MySQL support
- **Cache**: Redis (optional, for performance)
- **Task Queue**: Celery with Redis/RabbitMQ backend
- **WebSocket**: Django Channels for real-time features
- **File Storage**: Local storage or cloud storage (configurable)
- **Email**: SMTP integration
- **API Documentation**: DRF auto-generated documentation

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher (or MySQL 8.0+)
- Redis (optional, for caching and Celery)
- SMTP server (for email functionality)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SafariDesk-Back.git
cd SafariDesk-Back
```

### 2. Create Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=safariDesk
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Celery (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Upload
MEDIA_ROOT=/path/to/media
MEDIA_URL=/media/
FILE_BASE_URL=http://localhost:8000

# CORS Settings (for frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Database Setup

```bash
# Create database
createdb safariDesk

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Load Initial Data (Optional)

```bash
# Set up default configurations
python manage.py shell
>>> from util.BusinessSetup import BusinessSetup
>>> setup = BusinessSetup()
>>> setup.run_setup()
>>> exit()
```

## 🚀 Running the Application

### Development Server

```bash
python manage.py runserver 8000
```

The API will be available at `http://localhost:8000`

### With Celery (for async tasks)

Terminal 1 - Django:
```bash
python manage.py runserver
```

Terminal 2 - Celery Worker:
```bash
celery -A RNSafarideskBack worker --loglevel=info
```

Terminal 3 - Celery Beat (for scheduled tasks):
```bash
celery -A RNSafarideskBack beat --loglevel=info
```

### With Docker (Optional)

```bash
docker-compose up -d
```

## 📁 Project Structure

```
SafariDesk-Back/
├── main/                   # Main app
├── tenant/                 # Multi-tenant functionality
│   ├── models/            # Database models
│   ├── views/             # API views
│   ├── serializers/       # DRF serializers
│   ├── routes/            # URL routing
│   └── services/          # Business logic
├── users/                 # User management
├── shared/                # Shared utilities
│   ├── models/           # Shared models
│   ├── services/         # Shared services
│   ├── tasks/            # Celery tasks
│   └── workers/          # Background workers
├── util/                  # Utility functions
├── RNSafarideskBack/      # Project settings
│   ├── settings/         # Environment-specific settings
│   ├── urls.py           # Main URL configuration
│   └── celery.py         # Celery configuration
├── templates/             # Email templates
├── media/                 # User uploads
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## 🔌 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Key Endpoints

#### Authentication
- `POST /auth/login/` - User login
- `POST /auth/register/` - User registration
- `POST /auth/verify-otp/` - OTP verification
- `POST /auth/password-reset/` - Password reset

#### Tickets
- `GET /ticket/list/` - List all tickets
- `POST /ticket/create/` - Create new ticket
- `GET /ticket/get/{ticket_id}` - Get ticket details
- `PUT /ticket/update/status/{id}` - Update ticket status
- `PUT /ticket/update/priority/{id}` - Update ticket priority
- `PUT /ticket/update/due-date/{id}` - Update ticket due date
- `POST /ticket/assign/` - Assign ticket to agent
- `POST /ticket/{pk}/add-note/` - Add internal note

#### SLA
- `GET /sla/policies/` - List SLA policies
- `POST /sla/policies/` - Create SLA policy
- `GET /sla/config/current/` - Get SLA configuration
- `POST /sla/config/update_config/` - Update SLA configuration

#### Tasks
- `GET /task/list/` - List tasks
- `POST /task/create/` - Create task
- `PUT /task/update-status/` - Update task status

#### Knowledge Base
- `GET /kb/articles/` - List articles
- `POST /kb/articles/` - Create article
- `GET /kb/categories/` - List categories
- `GET /kb/articles/search/` - Search articles

For complete API documentation, visit `/api/docs/` when running the server.

## ⚙️ Configuration

### SLA Configuration

Enable or disable SLA tracking:

```python
# Via API
POST /api/v1/sla/config/update_config/
{
    "allow_sla": true,
    "allow_holidays": true
}
```

### Email Templates

Customize email templates in the `templates/` directory:
- `assigned-ticket.html` - Ticket assignment notification
- `new-ticket.html` - New ticket notification
- `password-reset.html` - Password reset email
- `otp.html` - OTP verification email

### Business Hours

Configure business hours via admin panel or API to calculate SLA correctly.

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test tenant

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Deployment

### Production Checklist

1. Set `DEBUG=False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use production-grade database (PostgreSQL)
4. Set up Redis for caching and Celery
5. Configure proper CORS settings
6. Use environment variables for sensitive data
7. Set up SSL/TLS certificates
8. Configure static file serving (Nginx/Apache)
9. Set up database backups
10. Configure logging and monitoring

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location /static/ {
        alias /path/to/SafariDesk-Back/staticfiles/;
    }

    location /media/ {
        alias /path/to/SafariDesk-Back/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Gunicorn (Production Server)

```bash
pip install gunicorn
gunicorn RNSafarideskBack.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Supervisor Configuration

```ini
[program:safariDesk]
command=/path/to/env/bin/gunicorn RNSafarideskBack.wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=/path/to/SafariDesk-Back
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/safariDesk/app.log
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write docstrings for functions and classes
- Add tests for new features
- Update documentation as needed

## 🐛 Bug Reports

Please report bugs by opening an issue on GitHub. Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- All contributors who have helped shape SafariDesk
- Open source libraries that make this project possible

## 📞 Support

- Documentation: [https://docs.safariDesk.com](https://docs.safariDesk.com)
- GitHub Issues: [https://github.com/yourusername/SafariDesk-Back/issues](https://github.com/yourusername/SafariDesk-Back/issues)
- Email: support@safariDesk.com

## 🗺️ Roadmap

- [ ] AI-powered ticket categorization
- [ ] Mobile app integration
- [ ] Advanced reporting and analytics
- [ ] Third-party integrations (Slack, Teams, etc.)
- [ ] Multi-language support
- [ ] Custom workflows and automation rules
- [ ] Customer satisfaction surveys
- [ ] Live chat widget

---

Made with ❤️ by the SafariDesk Team
