# Citation Generator

A web application for generating bibliographic citations in APA and MLA formats. Built with FastAPI backend and React TypeScript frontend.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+

### 1. Initial Setup (One Time Only)
```bash
git clone https://github.com/catebros/citation-generator.git
cd citation-generator
python -m venv venv
.\venv\Scripts\activate                    # Windows (use source venv/bin/activate for macOS/Linux)
pip install -r requirements.txt
```

### 2. Development Mode
```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn main:app --reload       # -> http://localhost:8000

# Terminal 2: Start Frontend Development
cd frontend
npm install
npm run dev                               # -> http://localhost:3000
```

### 3. Production Mode (Optional)
```bash
# Terminal 1: Start Backend (same as above)
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000    # -> http://localhost:8000

# Terminal 2: Build & Preview Production Frontend
cd frontend
npm run build
npm run preview                           # -> http://localhost:4173
```

### 4. Add Sample Data (Optional)
```bash
cd backend
python populate_db.py                    # Adds sample projects and citations
```

### URLs Summary
- **Frontend Development**: http://localhost:3000
- **Frontend Production**: http://localhost:4173  
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs


## Project Structure

```
citation-generator/
├── backend/                 # FastAPI backend
│   ├── config/             # Configuration files
│   ├── db/                 # Database setup
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access layer
│   ├── routers/            # API routes
│   ├── services/           # Business logic
│   ├── tests/              # Test suite
│   ├── main.py             # Application entry point
│   └── populate_db.py      # Database population script
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/         # Page components
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   └── public/            # Static assets
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Available Scripts

### Backend
```bash
# Run server in development mode with auto-reload
python -m uvicorn main:app --reload

# Run server directly with Python
python main.py

# Run server in production mode (no reload)
python -m uvicorn main:app --host 127.0.0.1 --port 8000 

# Check API health
curl http://localhost:8000/health
```

### Frontend
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

```

## Testing

### Backend Testing
The backend includes comprehensive test coverage:

```bash
cd backend

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_citation_service.py -v
```

**Test Database Isolation**: Tests automatically use a separate `test_citations.db` database to avoid corrupting production data.

## Database

### Database Operations

#### Reset Database
```bash
# Delete the database file to start fresh
rm backend/citations.db

# Run the app again to recreate tables
python -m uvicorn main:app --reload
```

#### Populate Sample Data
```bash
cd backend

# Add sample data
python populate_db.py

# Clear all data from database
python populate_db.py --clear
```

**Sample data includes**:
- 4 sample projects
- 12+ sample citations of different types (book, article, website, report)
- Proper associations between projects and citations

## Links

- **Report**: [Google Docs](https://docs.google.com/document/d/1lp3-weBMbTAuxRzb5KFo3h79LeWLcDAm-BwiYguAXzQ/edit?usp=sharing)