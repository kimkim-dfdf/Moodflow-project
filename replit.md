# MoodFlow - Emotion-Based Productivity Dashboard

## Overview
MoodFlow is a modern web application that helps users track their emotional state and receive personalized task and music recommendations based on their current mood. Built with React frontend and Python Flask backend.

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
- Tables: users, tasks, emotions, emotion_history, calendar_events, music_recommendations
- Uses SQLAlchemy ORM for database operations

## Key Features

### 1. Dashboard
- User greeting with current date
- Emotion selection (Happy, Sad, Tired, Angry, Stressed, Neutral)
- Personalized task recommendations based on mood
- Music recommendations with YouTube/Spotify links
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

### 4. Profile
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

### Profile
- GET `/api/user/profile` - Get profile
- PUT `/api/user/profile` - Update profile
- GET `/api/dashboard/summary` - Get dashboard summary

## Recent Changes
- December 1, 2025: ✅ COMPLETED - Enhanced emotion selector with AI analysis + Fixed emotion analysis algorithm
  - "How are you feeling today?" now supports factor-based mood analysis
  - Users can analyze mood via 6 factors: sleep quality, energy level, stress level, concentration, motivation, mood rating
  - System automatically determines appropriate emotion from factors
  - Sliders with values 1-5 for each factor with visual feedback
  - Still supports direct emoji selection (original functionality)
  - Database successfully migrated with 6 new columns in emotion_history table
  - Fixed emotion analysis algorithm to properly rank emotions (Neutral calculation corrected)
  - Backend /api/emotions/analyze endpoint working correctly with accurate emotion detection
  - Frontend EmotionSelector component with toggle between modes
  - All workflows restarted and stable
- Previous: Initial project setup with complete MVP features
- Implemented emotion-based recommendation engine
- Created all 4 main pages: Dashboard, Tasks, Calendar, Profile
- Added music recommendations with external links
- Implemented responsive design

## User Preferences
- Clean, minimal interface preferred
- Soft colors and rounded cards
- Left-side navigation with 4 menu items only
