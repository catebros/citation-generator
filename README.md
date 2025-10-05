# Citation Generator

A web application for generating bibliographic citations in APA and MLA formats. Built with FastAPI backend and React TypeScript frontend.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+

### 1. Initial Setup (One Time Only)

#### Windows (PowerShell)
```powershell
git clone https://github.com/catebros/citation-generator.git
cd citation-generator
python -m venv venv
. venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm install  
cd ..
```

#### macOS / Linux (bash/zsh)
```bash
git clone https://github.com/catebros/citation-generator.git
cd citation-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install   
cd ..
```

> Every time you open a new terminal, start from the folder created by `git clone` (the repo root), activate the venv, and then cd into the correct subfolder before running backend/frontend commands.

### 2. Add Sample Data (Optional)

#### Windows (PowerShell)
Open a new terminal, then:
```powershell
cd path\to\citation-generator
.venv\Scripts\Activate.ps1
cd backend
python populate_db.py
```

#### macOS / Linux (bash/zsh)
Open a new terminal, then:
```bash
cd path/to/citation-generator
source venv/bin/activate
cd backend
python populate_db.py
```


### 3. Development Mode

#### Windows (PowerShell)
Open a new terminal, then:
```powershell
cd path\to\citation-generator
.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn main:app --reload
```
Open another terminal for frontend:
```powershell
cd path\to\citation-generator
cd frontend
npm run dev
```

This will start the backend server at `http://localhost:8000` and the frontend development server at `http://localhost:3000`.

#### macOS / Linux (bash/zsh)
Open a new terminal, then:
```bash
cd path/to/citation-generator
source venv/bin/activate
cd backend
python -m uvicorn main:app --reload
```
Open another terminal for frontend:
```bash
cd path/to/citation-generator
cd frontend
npm run dev
```

This will start the backend server at `http://localhost:8000` and the frontend development server at `http://localhost:3000`.


### 4. Production Mode (Optional)

#### Windows (PowerShell)
Open a new terminal, then:
```powershell
cd path\to\citation-generator
.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Open another terminal for frontend:
```powershell
cd path\to\citation-generator
cd frontend
npm run build
npm run preview
```

This will start the backend server at `http://localhost:8000` and the frontend production server at `http://localhost:4173`.

#### macOS / Linux (bash/zsh)
Open a new terminal, then:
```bash
cd path/to/citation-generator
source venv/bin/activate
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Open another terminal for frontend:
```bash
cd path/to/citation-generator
cd frontend
npm run build
npm run preview
```

This will start the backend server at `http://localhost:8000` and the frontend production server at `http://localhost:4173`.

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
> **Note:**  
> The tests are configured to run as a group using pytest because there is a `conftest.py` configuration file in the backend test suite.  
> This file sets up fixtures such as a dedicated test database and ensures proper isolation and cleanup between tests.  
> Running tests individually with `python test_xxx.py` will not use these fixtures and may affect your production database.  
> **Always run tests using `pytest` to ensure safe and isolated test execution.**

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