# MoodFlow - Emotion-Based Productivity Dashboard

## Overview
MoodFlow is a modern web application that helps users track their emotional state and receive personalized task, music, and book recommendations based on their current mood. Built with React frontend and Python Flask backend.

## Project Architecture

### Frontend (React + Vite)
- **Location**: `/frontend`
- **Port**: 5000
- **Key Technologies**: React, React Router, Axios, Recharts, Lucide React, date-fns

### Backend (Python Flask)
- **Location**: `/backend`
- **Port**: 8000
- **Key Technologies**: Flask, Flask-CORS

### Data Storage (PostgreSQL Database)
- **Database**: PostgreSQL (Neon-backed)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Environment**: DATABASE_URL environment variable
- Static data (emotions, music, books) stored in `static_data.py`

## Backend File Structure

```
backend/
├── app.py                    # Flask app factory with DB config
├── run.py                    # Entry point
├── models.py                 # SQLAlchemy database models
├── repository.py             # Database operations (CRUD)
├── static_data.py            # Static data (emotions, music, books)
├── recommendation_engine.py  # Task scoring algorithm
├── routes.py                 # API endpoints
└── uploads/                  # Photo uploads
```

## Key Features

### 1. Dashboard
- User greeting with current date
- Emotion selection (Happy, Sad, Tired, Angry, Stressed, Neutral)
- Personalized task recommendations based on mood
- Music recommendations with YouTube links
- Mini calendar with emotion tracking
- Weekly mood statistics chart

### 2. Tasks
- AI-based task suggestions (no manual input)
- Categories: Work, Study, Health, Personal
- Priority levels: Low, Medium, High
- Emotion-based task generation
- Delete tasks with trash icon

### 3. Calendar
- Monthly calendar view
- Record emotions for any day
- Visual emotion indicators on calendar

### 4. Books
- Tag-based filtering with 10 emotion tags
- AND logic for multi-tag filtering
- 15 curated books with 3 tags each

### 5. Profile
- User settings management

## Recommendation Algorithm

**Total Score = Category Score (57%) + Priority Score (43%)**

- Category weight from emotion-to-category mapping
- Priority scoring inverts based on emotion preference
- Happy/energetic = prefer High priority tasks
- Tired/sad = prefer Low priority tasks

## Demo Accounts (Simplified Login)

Only 4 fixed accounts can log in (no registration):

| Email | Password | Role |
|-------|----------|------|
| seven@gmail.com | ekdus123 | User |
| elly@gmail.com | ekdus123 | User |
| nicole@gmail.com | ekdus123 | User |
| admin@gmail.com | ekdus123 | Admin |

## API Endpoints

### Authentication (Simplified)
- `POST /api/auth/register` - Disabled (returns error)
- `POST /api/auth/login` - Login with demo account
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Emotions
- `GET /api/emotions` - List all emotions
- `POST /api/emotions/record` - Record emotion for a day
- `GET /api/emotions/history` - Get emotion history
- `GET /api/emotions/statistics` - Get emotion statistics
- `GET /api/emotions/diary/<date>` - Get diary entry for date

### Tasks
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `GET /api/tasks/recommended` - Get recommended tasks
- `GET /api/tasks/suggestions` - Get AI task suggestions

### Music
- `GET /api/music/recommendations` - Get music by emotion

### Books
- `GET /api/books/tags` - Get all book tags
- `GET /api/books` - Get books filtered by tags (AND logic)

### Profile
- `GET /api/user/profile` - Get profile
- `PUT /api/user/profile` - Update profile
- `GET /api/dashboard/summary` - Get dashboard summary

### File Upload
- `POST /api/upload/photo` - Upload photo
- `GET /api/uploads/<filename>` - Serve uploaded file

## Code Style Guidelines

This project uses **student-friendly** code patterns:
- Regular functions (no lambdas)
- Explicit if/else statements (no ternary operators)
- For loops (no list comprehensions)
- Bubble sort for sorting
- Clear variable names
- Comprehensive comments

## Recent Changes

- December 8, 2025: Database simplification
  - Removed CustomBook and CustomMusic models (no admin-managed custom content)
  - Books and music now come exclusively from static_data.py
  - Added MusicFavorite model for user music favorites
  - Users can add/remove items from favorites (BookFavorite, MusicFavorite)
  - Simplified routes.py - removed admin custom book/music endpoints
  - Added music favorites API endpoints

- December 8, 2025: PostgreSQL database migration
  - Changed from JSON file storage to PostgreSQL database
  - Created models.py with SQLAlchemy models (User, Task, EmotionHistory, BookFavorite, MusicFavorite)
  - Updated app.py with database configuration
  - Updated repository.py to use SQLAlchemy queries
  - Demo users are seeded on application startup

- December 3, 2025: Simplified authentication
  - Removed password hashing (no security for demo)
  - Only 4 demo accounts can log in
  - Registration disabled
  - Login page shows demo account info

## User Preferences
- Clean, minimal interface
- Soft colors and rounded cards
- Student-friendly code style (simple patterns)
- Left-side navigation with 5 menu items
- PostgreSQL database required for professor's requirements

## Running Locally

### Backend
```bash
cd backend
pip install flask flask-cors flask-login python-dotenv werkzeug
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Ports
- Backend: http://localhost:8000
- Frontend: http://localhost:5000
