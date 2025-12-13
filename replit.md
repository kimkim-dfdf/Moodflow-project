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
- All reference data (emotions, music, books, tags) stored in PostgreSQL database
- Data is automatically seeded on application startup via `seed_all_static_data()`

## Backend File Structure

```
backend/
├── app.py                    # Flask app factory with DB config
├── run.py                    # Entry point
├── models.py                 # SQLAlchemy database models
├── repository.py             # Database operations (CRUD) and helper queries
├── recommendation_engine.py  # Task scoring algorithm
├── routes.py                 # API endpoints
├── seed_data.py              # Static data seeding (emotions, music, books, tags)
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
- Popular Books section (top 5 most reviewed)
- Book reviews with ratings
- Favorites with localStorage persistence

### 5. Music
- Dedicated music page with full music library
- Emotion-based filtering (6 emotion types)
- Search by title, artist, or genre
- Favorites with localStorage persistence
- YouTube links for each song

### 6. Profile
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

- December 13, 2025: Added more task suggestions
  - Added 3 more task suggestions per emotion (now 8 per emotion, 48 total)
  - File: backend/recommendation_engine.py (TASK_SUGGESTIONS dict)

- December 13, 2025: Removed book purchase feature
  - Removed shopping cart, checkout, and order functionality
  - Removed CartItem, Order, OrderItem database models
  - Removed price display from books (pure recommendation app now)
  - Books page now focuses on recommendations, reviews, and favorites

- December 11, 2025: Frontend code refactoring
  - Books.jsx: 1144줄 → 538줄로 축소 (53% 감소)
  - Music.jsx: 679줄 → 376줄로 축소 (45% 감소)
  - Reduced JSX duplication and simplified event handlers
  - Added Korean comments for educational purposes
  - Maintained student-friendly code patterns (var declarations, explicit for loops)

- December 11, 2025: Backend code refactoring
  - repository.py: 1078줄 → 788줄로 축소 (27% 감소)
  - routes.py: 1005줄 → 717줄로 축소 (29% 감소)
  - Added `to_dict_list()` helper function to reduce repetition
  - Added `get_json_or_error()` helper for request validation
  - Added Korean comments for educational purposes
  - Maintained student-friendly code patterns (no lambdas, no list comprehensions)

- December 11, 2025: Admin page enhancements
  - Added Orders tab to view all user purchase history
  - Added price field to Book add/edit modal
  - Books table now shows price column
  - New admin API endpoint: GET /api/admin/orders

- December 11, 2025: Frontend CSS cleanup
  - Removed unused CSS classes from index.css (~22 lines removed)
  - Removed .music-detail-modal, .music-modal-* classes (unused modal styles)
  - Removed .music-detail-page and related selectors (MusicDetail page removed)
  - Kept .music-detail-inline styles (still used by Music.jsx)

- December 11, 2025: Code cleanup
  - Removed unused API routes (/api/books/all, /api/orders)
  - Removed unused repository functions (get_user_orders, get_user_review_for_book)
  - Removed unused MusicDetail page (no navigation links to it)
  - Removed unused database columns (UserMusicTag.created_at, CartItem.created_at)
  - All prices now come from database, removed hardcoded fallbacks

- December 8, 2025: Code cleanup
  - Removed unused legacy functions from repository.py
  - Cleaned up deprecated functions (load_data, save_data, etc.)

- December 8, 2025: Full static data migration to PostgreSQL
  - Created new database models: Emotion, Music, Book, BookTag, BookTag_Book (many-to-many)
  - Moved all static data (emotions, music, books, tags) from static_data.py to database
  - Implemented seed_all_static_data() for automatic data seeding on startup
  - Removed static_data.py and data.json files
  - Updated repository.py with helper functions (get_all_emotions, get_music_by_emotion, get_books_by_tags, etc.)
  - All recommendation logic now queries database instead of in-memory lists

- December 8, 2025: PostgreSQL database migration
  - Changed from JSON file storage to PostgreSQL database
  - Created models.py with SQLAlchemy models
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

자세한 로컬 설치 방법은 `LOCAL_SETUP.md` 파일 참고

### Quick Start
```bash
# 백엔드
cd backend
pip install flask flask-cors flask-login flask-sqlalchemy psycopg2-binary python-dotenv werkzeug
python run.py

# 프론트엔드 (새 터미널)
cd frontend
npm install
npm run dev
```

### Ports
- Backend: http://localhost:8000
- Frontend: http://localhost:5000

### 제출 전 삭제할 파일
- `.replit`, `replit.md`, `replit.nix`
- `.upm/`, `.cache/`
