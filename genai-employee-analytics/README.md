# GenAI Employee Analytics

Full-stack starter for employee analytics with a FastAPI backend and React frontend.

## Backend

1. Create a virtual environment and install dependencies:

```
pip install -r backend/requirements.txt
```

2. Run the API:

```
uvicorn app:app --reload --app-dir backend
```

- Root: http://localhost:8000/
- Basic stats: http://localhost:8000/basic-stats

## Frontend

1. Install dependencies:

```
cd frontend
npm install
```

2. Run the app:

```
npm start
```

The UI calls the backend at http://localhost:8000.
