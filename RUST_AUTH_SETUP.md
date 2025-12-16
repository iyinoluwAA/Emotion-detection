# Rust Auth Microservice Setup Guide

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Frontend   │────────▶│ Python Flask │────────▶│ Rust Auth  │
│  (React)    │         │  (Port 5000) │         │  (Port 8000)│
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               │ (validates JWT locally)
                               │
                               ▼
                        ┌──────────────┐
                        │ Emotion Model│
                        └──────────────┘
```

## How It Works (Like Supabase)

1. **User Registration/Login** → Python calls Rust auth service
2. **Rust Returns JWT** → Python forwards to frontend
3. **Frontend Stores JWT** → Sends with every request
4. **Python Validates JWT** → Validates locally (same secret, fast)
5. **Protected Endpoints** → Use `@require_auth` decorator

## Setup Steps

### Step 1: Start Rust Auth Service

```bash
cd /home/iyino/projects/toniebee/backend

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/toniebee"
export JWT_SECRET_KEY="your-secret-key-here"
export JWT_MAXAGE="15"  # 15 minutes
export FRONTEND_URL="http://localhost:5174"

# Run Rust service
cargo run
```

Rust service will run on `http://localhost:8000`

### Step 2: Configure Python Backend

Create `.env` file in `backend/` directory:

```bash
# Rust Auth Service URL
RUST_AUTH_URL=http://localhost:8000

# JWT Secret (MUST match Rust JWT_SECRET_KEY)
RUST_JWT_SECRET=your-secret-key-here

# Flask config
FLASK_ENV=development
```

### Step 3: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Test Integration

1. **Start Rust service** (port 8000)
2. **Start Python backend** (port 5000)
3. **Test registration:**
   ```bash
   curl -X POST http://localhost:5000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","password":"SecurePass123!!"}'
   ```

4. **Test login:**
   ```bash
   curl -X POST http://localhost:5000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"SecurePass123!!"}' \
     -c cookies.txt
   ```

5. **Test protected endpoint:**
   ```bash
   curl -X POST http://localhost:5000/detect \
     -H "Content-Type: multipart/form-data" \
     -F "image=@test.jpg" \
     -b cookies.txt
   ```

## Environment Variables

### Rust Service (.env in toniebee/backend/)
```bash
DATABASE_URL=postgresql://user:pass@localhost/toniebee
JWT_SECRET_KEY=your-secret-key-here
JWT_MAXAGE=15
FRONTEND_URL=http://localhost:5174
```

### Python Backend (.env in backend/)
```bash
RUST_AUTH_URL=http://localhost:8000
RUST_JWT_SECRET=your-secret-key-here  # Must match Rust JWT_SECRET_KEY
FLASK_ENV=development
```

## API Endpoints

### Auth Endpoints (Python proxies to Rust)

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user
- `GET /auth/verify?token=...` - Verify email

### Protected Endpoints (Require Auth)

- `POST /detect` - Emotion detection (now requires auth)

## Benefits of This Approach

1. ✅ **Reuse Rust Code** - No porting needed
2. ✅ **Better Security** - Rust's memory safety
3. ✅ **Separation of Concerns** - Auth is separate service
4. ✅ **Scalable** - Can scale services independently
5. ✅ **Learn Microservices** - Real-world architecture
6. ✅ **Fast Validation** - JWT validated locally (like Supabase)

## Troubleshooting

### Rust service not responding
- Check if Rust service is running: `curl http://localhost:8000/api/health`
- Check Rust logs for errors
- Verify DATABASE_URL is correct

### JWT validation fails
- Ensure `RUST_JWT_SECRET` matches Rust `JWT_SECRET_KEY`
- Check token is being sent (cookie or header)
- Verify token hasn't expired

### CORS errors
- Rust service CORS is configured for localhost:5173 and localhost:3000
- Python backend CORS allows all origins (can restrict in production)

## Next Steps

1. Test the integration locally
2. Add more protected endpoints
3. Add role-based access (admin/user)
4. Deploy both services (Railway for Python, separate service for Rust)


