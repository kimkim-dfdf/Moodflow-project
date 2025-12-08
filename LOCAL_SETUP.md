# MoodFlow 로컬 설치 가이드

## 1. 필수 설치 프로그램

### Python 3.11+
- 다운로드: https://www.python.org/downloads/
- 설치 시 "Add Python to PATH" 체크 필수

### Node.js 18+
- 다운로드: https://nodejs.org/
- LTS 버전 권장

### PostgreSQL 14+
- 다운로드: https://www.postgresql.org/download/
- 설치 시 비밀번호 기억해두기

---

## 2. 데이터베이스 설정

### PostgreSQL 데이터베이스 생성

```bash
# PostgreSQL 접속 (Windows: SQL Shell 실행)
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE moodflow;

# 접속 종료
\q
```

> **참고:** 테이블과 초기 데이터는 백엔드 실행 시 자동으로 생성됩니다!
> - 7개 테이블 자동 생성 (users, tasks, emotion_history, emotions, music, books, book_tags)
> - 6개 감정, 24개 음악, 15개 책, 10개 태그 자동 시드
> - 4개 데모 계정 자동 생성

---

## 3. 프로젝트 다운로드

```bash
# 프로젝트 폴더 생성 및 이동
mkdir moodflow
cd moodflow

# 파일 복사 (Replit에서 Download as zip 후 압축 해제)
```

---

## 4. 백엔드 설정

### 4-1. 터미널에서 backend 폴더로 이동
```bash
cd backend
```

### 4-2. 가상환경 생성 및 활성화

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4-3. 패키지 설치
```bash
pip install flask flask-cors flask-login flask-sqlalchemy psycopg2-binary python-dotenv werkzeug gunicorn
```

### 4-4. 환경 변수 파일 생성

backend 폴더에 `.env` 파일 생성:

```
DATABASE_URL=postgresql://postgres:비밀번호@localhost:5432/moodflow
SECRET_KEY=your-secret-key-here
```

**주의:** `비밀번호` 부분을 PostgreSQL 설치 시 설정한 비밀번호로 변경

### 4-5. 백엔드 실행
```bash
python run.py
```

성공 시 출력:
```
Starting MoodFlow Backend Server...
Server running at: http://localhost:8000
```

---

## 5. 프론트엔드 설정

### 5-1. 새 터미널 열고 frontend 폴더로 이동
```bash
cd frontend
```

### 5-2. 패키지 설치
```bash
npm install
```

### 5-3. 프론트엔드 실행
```bash
npm run dev
```

> **참고:** `vite.config.js`에 프록시 설정이 이미 되어있어서
> `/api` 요청이 자동으로 `http://localhost:8000`으로 전달됩니다.
> `axios.js` 파일 수정은 필요 없습니다.

성공 시 출력:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5000/
```

---

## 6. 앱 접속

브라우저에서 `http://localhost:5000` 접속

### 로그인 계정

| 이메일 | 비밀번호 | 역할 |
|--------|----------|------|
| seven@gmail.com | ekdus123 | 일반 사용자 |
| elly@gmail.com | ekdus123 | 일반 사용자 |
| nicole@gmail.com | ekdus123 | 일반 사용자 |
| admin@gmail.com | ekdus123 | 관리자 |

---

## 7. 문제 해결

### 데이터베이스 연결 오류
- PostgreSQL 서비스가 실행 중인지 확인
- `.env` 파일의 DATABASE_URL 확인
- 비밀번호에 특수문자 있으면 URL 인코딩 필요

### 포트 충돌
- 백엔드: 8000 포트 사용 중이면 `run.py`에서 포트 변경
- 프론트엔드: 5000 포트 사용 중이면 `vite.config.js`에서 변경

### CORS 오류
- 백엔드와 프론트엔드가 모두 실행 중인지 확인
- `axios.js`의 baseURL이 올바른지 확인

---

## 8. 제출 전 삭제할 파일

로컬 실행과 무관한 Replit 전용 파일들:
- `.replit`
- `replit.md`
- `replit.nix`
- `.upm/`
- `.cache/`

---

## 파일 구조 요약

```
moodflow/
├── backend/
│   ├── app.py              # Flask 앱 설정
│   ├── run.py              # 서버 시작점
│   ├── models.py           # 데이터베이스 모델 (7개 테이블)
│   ├── repository.py       # 데이터 저장소
│   ├── routes.py           # API 엔드포인트
│   ├── recommendation_engine.py  # 추천 알고리즘
│   ├── seed_data.py        # 초기 데이터 시드 (자동 실행)
│   ├── .env                # 환경 변수 (직접 생성)
│   └── uploads/            # 업로드 파일
│
├── frontend/
│   ├── src/
│   │   ├── pages/          # 7개 페이지
│   │   ├── components/     # 4개 컴포넌트
│   │   ├── context/        # 2개 컨텍스트
│   │   └── api/            # API 설정
│   ├── package.json
│   └── vite.config.js
│
└── LOCAL_SETUP.md          # 이 파일
```
