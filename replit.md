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
- **Key Technologies**: Flask, SQLAlchemy, Flask-Login, Flask-CORS

### Database (PostgreSQL)
- Tables: users, tasks, emotions, emotion_history, calendar_events, music_recommendations, book_recommendations, book_tags, book_tag_links
- Uses SQLAlchemy ORM for database operations

## Key Features

### 1. Dashboard
- User greeting with current date
- Emotion selection (Happy, Sad, Tired, Angry, Stressed, Neutral)
- Personalized task recommendations based on mood
- Music recommendations with YouTube links
- Book recommendations based on mood
- Mini calendar with emotion tracking
- Weekly mood statistics chart

### 2. Tasks
- Full CRUD operations
- Categories: Work, Study, Health, Personal
- Priority levels: Low, Medium, High
- Emotion-based task generation
- Filter by status and category

### 3. Calendar
- Monthly calendar view
- Add/edit/delete events
- Record emotions for any day
- Visual emotion indicators on calendar

### 4. Books
- Dedicated page for book recommendations
- **Tag-based filtering with 10 emotion tags** (Hopeful, Comforting, Peaceful, Growth, Emotional, Escapism, Recharge, Courage, New Perspective, Focus)
- **Jaccard Similarity Algorithm**: Books scored by tag match percentage
- **Tag Co-occurrence Algorithm**: Suggests related tags based on frequently paired tags
- Multi-select tag chips UI for refined book discovery
- Match score badge showing relevance percentage
- 15 curated books with 3 tags each
- Book details: title, author, genre, description, associated tags

### 5. Profile
- User settings management
- Preferred work time configuration
- Category preferences
- Emotion history with charts
- Energy level trends

## Recommendation Algorithm
The app uses a weighted scoring system that considers:
- Emotion-to-category mapping
- Priority preferences per emotion
- Task urgency (due date)
- User's personal category preferences

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - User login
- POST `/api/auth/logout` - User logout
- GET `/api/auth/me` - Get current user

### Emotions
- GET `/api/emotions` - List all emotions
- POST `/api/emotions/record` - Record emotion for a day
- GET `/api/emotions/today` - Get today's emotion
- GET `/api/emotions/history` - Get emotion history
- GET `/api/emotions/statistics` - Get emotion statistics

### Tasks
- GET `/api/tasks` - List tasks (with filters)
- POST `/api/tasks` - Create task
- PUT `/api/tasks/:id` - Update task
- DELETE `/api/tasks/:id` - Delete task
- GET `/api/tasks/recommended` - Get recommended tasks
- GET `/api/tasks/suggestions` - Get task suggestions

### Calendar
- GET `/api/calendar/events` - List events
- POST `/api/calendar/events` - Create event
- PUT `/api/calendar/events/:id` - Update event
- DELETE `/api/calendar/events/:id` - Delete event

### Books
- GET `/api/books/tags` - Get all book tags with book counts
- GET `/api/books` - Get books filtered by tags (params: tags[], limit)
- GET `/api/books/recommendations` - Get book recommendations by emotion (legacy, params: emotion, limit)

### Profile
- GET `/api/user/profile` - Get profile
- PUT `/api/user/profile` - Update profile
- GET `/api/dashboard/summary` - Get dashboard summary

## Recent Changes
- December 2, 2025: Implemented tag-based book recommendation system
  - Created BookTag and BookTagLink models for granular emotional tags
  - Added 10 Korean emotion tags (희망적인, 위로가 필요한, 평온함을 찾는, etc.)
  - Mapped 15 books to 3 tags each (45 tag associations)
  - New API: /api/books/tags (list tags), /api/books (filter by tags)
  - Updated Books page with multi-select tag chips UI
  - BookCard now displays associated tags with color styling
  - Removed book recommendations from Dashboard (books only in Books page)
- December 2, 2025: Added book recommendations feature
  - Created BookRecommendation model with 24 books (4 per emotion)
  - Added /api/books/recommendations endpoint
  - Created BookCard component and Books page
  - Added Books to navigation (now 5 pages)
  - Integrated book recommendations into Dashboard
- December 1, 2025: Initial project setup with complete MVP features
- Implemented emotion-based recommendation engine
- Created all 4 main pages: Dashboard, Tasks, Calendar, Profile
- Added music recommendations with YouTube links
- Implemented responsive design

## User Preferences
- Clean, minimal interface preferred
- Soft colors and rounded cards
- Left-side navigation with 5 menu items (Dashboard, Tasks, Calendar, Books, Profile)
