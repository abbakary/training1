# DREVAS - Driver Training and Examination System

A comprehensive Django-based training and examination management system for truck drivers (Drevas).

## Features

### 🚛 Core Functionality
- **Driver Management**: Create and manage driver profiles with unique IDs
- **Training Sessions**: Organize training in batches/sessions
- **Exam Management**: Create exams with questions and assignments
- **PDF Generation**: Generate printable exam papers for drivers
- **Marking System**: Record marks after manual grading
- **Progress Tracking**: Monitor driver performance and exam results
- **Search & Filters**: Find drivers, exams, and results easily

### 👥 User Roles
- **Admin**: Full system control, manage organizations, users, and data
- **Trainer**: Create exams, assign to drivers, mark exams
- **Viewer**: Read-only access to reports and data

### 📊 Dashboard
- Overview statistics (total drivers, exams, results)
- Recent activity tracking
- Performance metrics
- Role-specific dashboards

## Technical Stack

- **Backend**: Django 4.2
- **Database**: SQLite (configurable to PostgreSQL)
- **Frontend**: Bootstrap 5 + Riho Admin Template
- **PDF Generation**: ReportLab
- **File Storage**: Local (configurable to cloud)

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Steps

1. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Create Directories**
```bash
mkdir -p static/riho
mkdir -p media
mkdir -p templates
```

4. **Initialize Database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser**
```bash
python manage.py createsuperuser
```

6. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

7. **Run Development Server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Project Structure

```
.
├── config/                 # Django settings and configuration
├── apps/
│   ├── core/              # Core functionality (auth, org management)
│   ├── drevas/            # Driver management
│   ├── exams/             # Exam management
│   └── marking/           # Results and marking
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Usage

### Admin Panel
Access at `/admin/` to manage:
- Organizations
- Users and roles
- Drivers (Drevas)
- Training sessions
- Exams and questions
- Results

### Creating an Exam

1. Navigate to **Exams** → **Create Exam**
2. Fill in exam details (title, subject, max marks, passing percentage)
3. Add questions with marks
4. Save the exam

### Assigning Exams

1. Go to the exam detail page
2. Click **Assign to Drivers**
3. Select drivers and set due date
4. System generates personalized exam papers

### Recording Marks

1. Navigate to **Results & Marking** → **Pending Marking**
2. Select an exam to mark
3. Enter marks for each question
4. System calculates percentage and status
5. Upload marked exam PDF (optional)
6. Save results

### Viewing Driver Progress

1. Go to **Drevas** → Select a driver
2. View:
   - Personal information
   - Training sessions enrolled
   - Exam results history
   - Overall statistics (passed/failed/average score)

## Models Overview

### Organization
- Name, address, contact details
- Parent entity for drivers and sessions

### Dreva (Driver)
- Full name, unique driver ID
- Contact information
- Status tracking (in_training, passed, failed, suspended)
- Associated with an organization

### TrainingSession
- Name, period, start/end dates
- Contains multiple exams
- Drivers enroll in sessions

### Exam
- Title, subject, description
- Max marks, duration, passing percentage
- Contains questions
- Assigned to specific drivers

### ExamQuestion
- Question text, type (short answer, essay, MCQ, true/false)
- Marks allocation
- Options for MCQ questions

### ExamAssignment
- Links exam to specific driver
- Tracks status (pending, completed, marked)
- Stores generated exam paper PDF

### ExamResult
- Driver's marks and performance
- Status (passed/failed/pending)
- Percentage calculation
- Marked exam PDF storage

## API Endpoints

### Dashboard
- `GET /` - Main dashboard

### Drevas
- `GET /drevas/` - List drivers
- `GET /drevas/<id>/` - Driver profile
- `POST /drevas/create/` - Create driver
- `POST /drevas/<id>/edit/` - Edit driver
- `GET /drevas/sessions/` - List sessions

### Exams
- `GET /exams/` - List exams
- `GET /exams/<id>/` - Exam details
- `POST /exams/create/` - Create exam
- `POST /exams/<id>/assign/` - Assign exam
- `GET /exams/assignment/<id>/pdf/` - Generate exam PDF

### Marking/Results
- `GET /marking/results/` - List results
- `GET /marking/results/<id>/` - Result details
- `POST /marking/assignment/<id>/marks/` - Record marks
- `GET /marking/dreva/<id>/progress/` - Driver progress

## Configuration

### Database Setup

#### SQLite (Default)
No additional configuration needed.

#### PostgreSQL
```python
# In config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'drevas_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### File Storage

#### Local Storage (Default)
Files stored in `media/` directory.

#### AWS S3
```python
# Install: pip install boto3 django-storages
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    },
}
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
```

## Email Configuration

```python
# In config/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## PDF Generation

The system uses **ReportLab** for PDF generation. Exam papers include:
- Header with organization name
- Driver and exam information
- Instructions
- Question list with space for answers
- Footer for examiner signature

## Security Considerations

1. **Change Secret Key**: Update `SECRET_KEY` in `config/settings.py`
2. **Set DEBUG=False**: In production
3. **Configure ALLOWED_HOSTS**: Add your domain
4. **Use Environment Variables**: For sensitive data
5. **Enable HTTPS**: In production
6. **Set CSRF_TRUSTED_ORIGINS**: For cross-origin requests

## Performance Optimization

- Database indexing on frequently searched fields
- Pagination for large datasets
- Caching for static files
- Query optimization with `select_related` and `prefetch_related`

## Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Using Netlify/Vercel
Deploy static files to CDN, run Django backend separately.

## Troubleshooting

### Migration Issues
```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Permission Errors
```bash
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
user.is_superuser = True
user.is_staff = True
user.save()
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project for commercial purposes.

## Support

For issues, feature requests, or questions:
- Email: support@drevas.com
- Documentation: https://drevas.readthedocs.io

## Changelog

### Version 1.0.0 (Initial Release)
- Complete driver management system
- Exam creation and assignment
- PDF exam paper generation
- Marking and result tracking
- Progress dashboard
- Search and filter functionality
