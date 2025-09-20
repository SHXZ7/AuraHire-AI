# AuraHire AI

<div align="center">
  <img width="100" height="100" alt="Gemini_Generated_Image_ju3v3vju3v3vju3v" src=<img width="500" height="500" alt="Gemini_Generated_Image_ju3v3vju3v3vju3v-removebg-preview" src="C:\Users\HP\Documents\try\ml\aura.png" />

A comprehensive full-stack application featuring a Streamlit frontend and FastAPI backend with PostgreSQL database integration for intelligent resume-job matching.

## Features

🚀 **Quick Match Tab**
- Upload resume files (PDF, DOCX, TXT)
- Paste job descriptions with automatic skill extraction
- Configure scoring weights (Hard Skills 70% vs Semantic Match 30%)
- Get comprehensive match analysis with 100+ skill detection
- Real-time fuzzy matching and skill variations
- Actionable feedback with gap analysis

📄 **Resume Parser Tab**
- Extract text from uploaded resumes
- Detect emails and phone numbers
- Advanced skill extraction with 100+ technology skills
- Show text statistics and full content

💼 **Job Parser Tab**
- Analyze job descriptions
- Extract required skills automatically (100+ skills dictionary)
- Show cleaned and processed text
- Skill categorization and requirements parsing

🗄️ **Database Management Tabs**
- **Resumes**: View all processed resumes with extracted skills
- **Job Descriptions**: Browse stored job postings and requirements
- **Match Results**: Comprehensive match analysis history with scores
- **Audit Logs**: Track all system activities and operations

## Architecture

### Backend (FastAPI + PostgreSQL)
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Models**: Resume, JobDescription, MatchResult, AuditLog
- **CRUD Operations**: Complete database persistence layer
- **Advanced Matching**: Enhanced algorithm with 100+ skills and fuzzy matching
- **Async Support**: Modern async/await patterns for optimal performance

### Frontend (Streamlit)
- **Interactive UI**: Multi-tab interface with real-time updates
- **Database Visualization**: Browse stored data across all tables
- **File Upload**: Drag & drop resume processing
- **Real-time Scoring**: Configurable matching weights and parameters

## Setup & Usage

### Prerequisites

#### 1. PostgreSQL Database
Make sure PostgreSQL is running and create a database:
```sql
CREATE DATABASE resume_matcher;
```

#### 2. Environment Variables
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/resume_matcher
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn backend.main:app --reload
```

### Frontend Setup
```bash
cd frontend
pip install -r requirements.txt

# Start the Streamlit app
streamlit run app.py
```

The application will be available at:
- **Frontend**: `http://localhost:8501`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` with comprehensive endpoints:

### Core Matching Endpoints
- `POST /match-resume-file` - Advanced file-based matching with database storage
- `POST /parse-resume` - Resume parsing and skill extraction
- `POST /parse-job` - Job description analysis and skill parsing

### Database Endpoints
- `GET /resumes` - Retrieve stored resumes with pagination
- `GET /jobs` - Browse job descriptions with filtering
- `GET /matches` - View match results with scoring details
- `GET /audit-logs` - System activity tracking
- `GET /statistics` - Dashboard statistics and metrics

### Utility Endpoints
- `GET /` - API health check and status
- `GET /docs` - Interactive API documentation (Swagger UI)

## Enhanced Features

✅ **Advanced Skill Matching**
- 100+ technology skills with variations (Python/python, ML/Machine Learning)
- Fuzzy matching for similar skills and synonyms
- Exact and partial skill matching algorithms
- Industry-specific skill categorization

✅ **Database Persistence**
- PostgreSQL integration with full CRUD operations
- Resume deduplication by filename
- Complete match history with detailed scoring
- Audit trail for all system operations

✅ **Intelligent Analysis**
- Configurable scoring weights (default: 70% skills, 30% semantic)
- Gap analysis with actionable improvement suggestions
- Processing time tracking and performance metrics
- Confidence scoring for match reliability

✅ **Professional Interface**
- Real-time database visualization across multiple tabs
- Color-coded match verdicts (High/Medium/Low)
- Detailed skill breakdowns and missing skill highlighting
- Export capabilities and data management tools

## Technical Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLAlchemy 2.0 (ORM with async support)
- Alembic (Database migrations)
- pydantic-settings (Configuration management)
- asyncpg (PostgreSQL async driver)

**Frontend:**
- Streamlit (Web interface)
- pandas (Data manipulation)
- requests (API communication)

**Matching Engine:**
- Advanced NLP with skill extraction
- Fuzzy string matching algorithms
- Semantic similarity analysis
- Statistical scoring models

## Project Structure

```
ml/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/                 # SQLAlchemy models
│   │   ├── resume.py
│   │   ├── job_description.py
│   │   ├── match_result.py
│   │   └── audit_log.py
│   ├── crud/                   # Database operations
│   ├── services/               # Business logic
│   │   ├── matcher.py          # Enhanced matching algorithm
│   │   ├── parse_resume.py
│   │   └── parse_job.py
│   ├── database/               # Database configuration
│   └── utils/                  # Utility functions
├── frontend/
│   └── app.py                  # Streamlit interface
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```
