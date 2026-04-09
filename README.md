# WorkFlow - Job Portal Application

## Project Description

WorkFlow is a comprehensive Django-based web application designed to connect job seekers with recruiters. The platform allows recruiters to post job opportunities, manage their company profiles, and review applications, while job seekers can create profiles, upload resumes, and apply to jobs. The application incorporates AI-powered features for intelligent job matching using semantic search and ATS (Applicant Tracking System) scoring.

## Key Features

### For Job Seekers:
- User registration and profile creation
- Resume upload and parsing
- Education and experience tracking
- Skill management
- Job search and application
- Application status tracking
- Saved jobs functionality

### For Recruiters:
- Company profile management with document verification
- Job posting with detailed requirements
- Subscription plans (Free, Basic, Premium)
- Application review and management
- AI-powered candidate matching
- Resume pooling (premium feature)
- AI chat support (premium feature)

### AI-Powered Features:
- Semantic job matching using vector embeddings
- ATS score calculation for resumes
- Skill matching and scoring
- Entity recognition for resume content
- Job categorization (Excellent, Good, Low match)

### Admin Features:
- User and company approval system
- Plan management
- Document verification workflow

## Technology Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite (with pgvector support for vector operations)
- **Frontend**: HTML, CSS, JavaScript (with Django templates)
- **AI/ML**: Hugging Face models, spaCy for NLP
- **File Storage**: Local media storage for uploads
- **Authentication**: Django's built-in authentication system

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- Git

### Steps

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```
   cd d:\FinalProject\Jobportel
   ```

2. **Activate the virtual environment**:
   - The project includes a virtual environment in the `Portel/` folder.
   - Activate it using:
     ```
     Portel\Scripts\activate
     ```

3. **Install dependencies**:
   - If there's a `requirements.txt` file, run:
     ```
     pip install -r requirements.txt
     ```
   - Otherwise, install core packages:
     ```
     pip install django pgvector django-widget-tweaks huggingface-hub spacy
     ```
   - Download spaCy model:
     ```
     python -m spacy download en_core_web_sm
     ```

4. **Database Setup**:
   - Run migrations:
     ```
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Create Superuser** (for admin access):
   ```
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```
   python manage.py runserver
   ```
   - Access the application at `http://127.0.0.1:8000/`

## Project Structure

```
Jobportel/
├── db.sqlite3                    # SQLite database
├── manage.py                     # Django management script
├── accounts/                     # User authentication app
├── main/                         # Main application logic
├── recruiter/                    # Recruiter-specific features
├── Seeker/                       # Job seeker features
├── Superuser/                    # Admin features
├── Templates/                    # HTML templates
├── static/                       # Static files (CSS, JS)
├── media/                        # User-uploaded files
│   ├── company_logos/
│   ├── job_banners/
│   ├── profile_pics/
│   ├── recruter_docs/
│   └── resume/
└── Jobportel/                    # Project settings
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## How It Works

### User Registration and Authentication
- Users can register as either job seekers or recruiters
- Django's authentication system handles login/logout
- Profiles are created post-registration with additional details

### Job Posting Workflow
1. Recruiters complete their company profile and upload verification documents
2. Admin approves the recruiter account
3. Recruiters subscribe to a plan (Free/Basic/Premium)
4. Post jobs with title, description, skills, salary, etc.
5. Jobs are vectorized for semantic matching

### Job Application Process
1. Job seekers create profiles and upload resumes
2. Resumes are parsed and vectorized
3. ATS scoring and entity recognition are performed
4. Seekers can search and apply to jobs
5. AI matching calculates compatibility scores

### Matching Algorithm
- **Semantic Matching**: Uses vector embeddings to compare job descriptions with resumes
- **Skill Matching**: Compares required skills with candidate skills
- **ATS Scoring**: Evaluates resume format and content
- **Entity Scoring**: Recognizes relevant entities in resumes
- **Final Score**: Weighted combination determining match category

### Subscription System
- **Free Plan**: Basic job posting
- **Basic Plan**: Limited jobs, basic features
- **Premium Plan**: Unlimited jobs, resume pooling, AI chat

## API and Integrations

The application uses:
- **pgvector**: For vector similarity searches
- **Hugging Face**: For AI model inference
- **spaCy**: For natural language processing
- **Django Widget Tweaks**: For form rendering

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended for pgvector)
4. Set up static file serving
5. Configure media file storage
6. Use environment variables for secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

This project is for educational purposes. Please check local laws for commercial use.

## 🌐 Live Demo
https://workflow-t5gn.onrender.com
