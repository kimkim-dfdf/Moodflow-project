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

### Data Storage (JSON File)
- **File**: `backend/data.json` (created automatically)
- **No database connection required**
- Data persists in JSON file
- Static data (emotions, music, books) stored in `static_data.py`

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
- Match score showing relevance percentage
- 15 curated books with 3 tags each

### 5. Profile
- User settings management

## Recommendation Algorithm
Category (57%) + Priority (43%) weighted scoring:
- Category weight from emotion-to-category mapping
- Priority scoring inverts based on emotion preference
- Happy/energetic = prefer High priority
- Tired/sad = prefer Low priority

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - User login
- POST `/api/auth/logout` - User logout
- GET `/api/auth/me` - Get current user

### Emotions
- GET `/api/emotions` - List all emotions
- POST `/api/emotions/record` - Record emotion for a day
- GET `/api/emotions/history` - Get emotion history
- GET `/api/emotions/statistics` - Get emotion statistics

### Tasks
- GET `/api/tasks` - List tasks
- POST `/api/tasks` - Create task
- PUT `/api/tasks/:id` - Update task
- DELETE `/api/tasks/:id` - Delete task
- GET `/api/tasks/recommended` - Get recommended tasks
- GET `/api/tasks/suggestions` - Get AI task suggestions

### Music
- GET `/api/music/recommendations` - Get music by emotion

### Books
- GET `/api/books/tags` - Get all book tags
- GET `/api/books` - Get books filtered by tags (AND logic)

### Profile
- GET `/api/user/profile` - Get profile
- PUT `/api/user/profile` - Update profile
- GET `/api/dashboard/summary` - Get dashboard summary

## Backend Files
- `app.py` - Flask app setup (21 lines)
- `repository.py` - JSON file storage (270 lines)
- `static_data.py` - Static data: emotions, music, books (122 lines)
- `recommendation_engine.py` - Scoring algorithm (230 lines)
- `routes.py` - API endpoints (330 lines)
- `run.py` - Entry point (6 lines)

## Recent Changes
- December 3, 2025: Removed database completely
  - No PostgreSQL, no SQLite
  - Data stored in JSON file (`data.json`)
  - Created `repository.py` for data operations
  - Removed SQLAlchemy dependency
- December 3, 2025: Backend refactoring
  - Clean, student-friendly code style
  - Simple patterns (no lambdas, no list comprehensions)
  - Bubble sort for sorting
  - Explicit if/else statements

## User Preferences
- Clean, minimal interface
- Soft colors and rounded cards
- Student-friendly code style (simple patterns)
- Left-side navigation with 5 menu items
- No database connection required
