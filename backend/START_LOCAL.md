# Local Development Setup

## Backend Setup

1. **Activate virtual environment:**
   ```bash
   cd backend
   source .venv/bin/activate
   ```

2. **Install dependencies (if not already installed):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download model (if not already downloaded):**
   ```bash
   chmod +x scripts/download_model.sh
   ./scripts/download_model.sh
   ```

4. **Start backend server:**
   ```bash
   python3 main.py
   # or
   python main.py  # if python points to python3
   ```
   
   Server will run at: `http://localhost:5000`

## Frontend Setup

1. **Install dependencies (if not already installed):**
   ```bash
   cd frontend
   npm install
   ```

2. **Start frontend dev server:**
   ```bash
   npm run dev
   ```
   
   Frontend will run at: `http://localhost:5173` (or similar)
   **It will automatically connect to local backend at `http://localhost:5000`**

## Testing

- Backend health: `curl http://localhost:5000/health`
- Frontend: Open browser to the URL shown by `npm run dev`

## Notes

- Frontend automatically uses `http://localhost:5000` in development mode
- Production (Vercel) still uses Render backend
- `.env.local` file is gitignored and won't be committed


