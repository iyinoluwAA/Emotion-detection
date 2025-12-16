# Authentication System Implementation Plan

## Current Problem

Right now, **ALL users share the same database**. If your friend in America tests the app, you can see their predictions in your logs. This is a **critical privacy issue** and prevents multi-tenant usage.

## Solution: Add User Authentication

We need to:
1. Add `user_id` to the predictions table
2. Implement JWT-based authentication
3. Protect endpoints with auth middleware
4. Filter all queries by `user_id`

## Implementation Options

### Option 1: Simple Python Auth (Recommended - Fastest)

**Pros:**
- Single codebase (Python only)
- No microservice complexity
- Easy to deploy
- Can reuse patterns from toniebee

**Cons:**
- Need to port auth logic from Rust to Python

**Time:** 2-3 hours

### Option 2: Use toniebee Auth as Microservice

**Pros:**
- Reuse existing Rust auth code
- Already tested and working

**Cons:**
- Two services to deploy/maintain
- Network latency for auth checks
- More complex setup

**Time:** 1-2 hours (if toniebee is already deployed)

## Recommended: Option 1 (Python Auth)

### Step 1: Database Migration

Add `user_id` column to predictions table:

```python
# backend/app/db_logger.py

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,  -- NEW: Link to user
    ts TEXT NOT NULL,
    filename TEXT,
    image_path TEXT,
    emotion TEXT,
    confidence REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_ts ON predictions(ts DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_emotion ON predictions(emotion);
"""
```

### Step 2: Create Auth Module

Create `backend/app/auth/` directory:

```
backend/app/auth/
├── __init__.py
├── jwt_utils.py      # JWT token generation/validation
├── password.py       # Password hashing (bcrypt)
├── middleware.py    # Auth decorator
└── routes.py         # Login/register endpoints
```

### Step 3: Update db_logger.py

Modify `log_prediction()` to require `user_id`:

```python
def log_prediction(db_path: str, user_id: int, filename: str, emotion: str, 
                   confidence: float, image_path: Optional[str] = None):
    # ... existing code ...
    cur.execute(
        "INSERT INTO predictions (user_id, ts, filename, image_path, emotion, confidence) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, ts, filename, image_path, emotion, confidence_val)
    )
```

### Step 4: Update All Queries

Filter by `user_id` in all queries:

```python
def tail_rows(db_path: str, user_id: int, limit: int = 10, ...):
    query = "SELECT id, ts, filename, image_path, emotion, confidence FROM predictions WHERE user_id = ?"
    params = [user_id]
    # ... rest of filters ...
```

### Step 5: Protect Endpoints

Add auth middleware to `/detect` and `/logs`:

```python
from app.auth.middleware import require_auth

@app.route("/detect", methods=["POST"])
@require_auth  # NEW: Requires authentication
def detect():
    user_id = request.user_id  # Set by middleware
    # ... existing code ...
    log_prediction(DB_PATH, user_id, used_filename, emotion, confidence, stored_filename)
```

## Quick Implementation (2-3 hours)

1. **Create auth module** (30 min)
   - JWT generation/validation
   - Password hashing with bcrypt
   - User registration/login

2. **Database migration** (30 min)
   - Add users table
   - Add user_id to predictions
   - Migration script

3. **Update endpoints** (1 hour)
   - Add auth middleware
   - Update all queries to filter by user_id
   - Add login/register routes

4. **Frontend updates** (30 min)
   - Add login/register UI
   - Store JWT token
   - Send token with requests

5. **Testing** (30 min)
   - Test with multiple users
   - Verify data isolation

## Dependencies to Add

```bash
pip install pyjwt bcrypt python-dotenv
```

## Environment Variables

```bash
# backend/.env
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_EXPIRATION_MINUTES=15
```

## Security Features

- ✅ JWT tokens (15 min expiration)
- ✅ Refresh tokens (optional, for better UX)
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting (already exists)
- ✅ CORS protection (already exists)

## Next Steps

1. Should I implement this now?
2. Do you want to use toniebee auth (microservice) or Python auth (simpler)?
3. Do you need refresh tokens or is 15-min JWT enough?

