# MoodFlow - Emotion-Based Productivity Dashboard

## Overview
MoodFlow is a web application that helps users track their emotional state and receive personalized task and music recommendations based on their current mood. Built with React frontend and Python Flask backend. Designed for UK 3rd year university presentation.

## Project Architecture

### Frontend (React + Vite)
- **Location**: `/frontend`
- **Port**: 5000
- **Pages**: 4 (Dashboard, Tasks, Books, Profile)

### Backend (Python Flask)
- **Location**: `/backend`
- **Port**: 8000
- **Key Technologies**: Flask, SQLAlchemy, Flask-Login, Flask-CORS

### Database (PostgreSQL)
- Tables: users, tasks, emotions, emotion_history, music_recommendations, book_recommendations, book_tags, book_tag_links

## Key Features

### 1. Dashboard
- User greeting with current date
- Emotion selection (Happy, Sad, Tired, Angry, Stressed, Neutral)
- Personalized task recommendations based on mood
- Music recommendations with YouTube links
- Weekly mood statistics chart (Pie Chart)

### 2. Tasks
- Task CRUD operations
- Categories: Work, Study, Health, Personal
- Priority levels: Low, Medium, High
- Emotion-based task suggestions

### 3. Books
- Tag-based filtering with 10 emotion tags
- AND logic filtering (books must have ALL selected tags)
- 15 curated books with 3 tags each

### 4. Profile
- User settings display
- Emotion history with charts

## Algorithms Used (5 total)

### 1. Weighted Scoring Algorithm (Main)
```
Score = (Category × 0.4) + (Priority × 0.35) + (Urgency × 0.25)
```

### 2. Priority Matching
- Maps emotions to preferred task priorities

### 3. Urgency Scoring
- Calculates score based on days until due date

### 4. Popularity Sort
- Orders music/books by popularity_score

### 5. Tag AND Filtering
- Returns books matching ALL selected tags

## Code Style (Student-friendly)
- Regular `function` declarations (not arrow functions)
- `.then()/.catch()` pattern (not async/await)
- Explicit `if` statements (not ternary operators)
- For loops (not list comprehensions in Python)
- Simple, readable code structure

## Recent Changes
- December 2, 2025: Simplified code for presentation
  - Removed Calendar page (not core feature)
  - Changed all arrow functions to regular functions
  - Replaced async/await with .then()/.catch()
  - Simplified Python backend (class → functions)
  - Reduced code complexity for easy explanation

## User Preferences
- Clean, minimal interface
- 4 navigation items (Dashboard, Tasks, Books, Profile)
- Simple code patterns for presentation
