from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import time
from datetime import datetime

# Import services & utils
from .services.matcher import match_resume_to_job
from .services.parse_resume import extract_text_from_file, parse_resume_comprehensive
from .services.parse_job import parse_job_description, parse_job_description_comprehensive
from .utils.extract_entities import extract_emails, extract_phones

# Import database components
from .database import get_db, create_tables
from .crud import (
    resume_repository, 
    job_description_repository, 
    match_result_repository, 
    audit_log_repository
)
from .models import Resume, JobDescription, MatchResult, AuditLog
from sqlalchemy.orm import Session

app = FastAPI(title="Enhanced Resume & Job Matcher API", version="2.0.0")

# Configure CORS for Streamlit Cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Streamlit app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Helper function for audit logging
def log_audit_event(
    db: Session,
    request: Request,
    event_type: str,
    event_action: str,
    resource_type: str = None,
    resource_id: int = None,
    response_status: int = 200,
    response_time_ms: int = None,
    error_message: str = None,
    business_event: str = None
):
    """Helper function to log audit events"""
    try:
        audit_log_repository.log_event(
            db=db,
            event_type=event_type,
            event_action=event_action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            endpoint=str(request.url.path),
            http_method=request.method,
            response_status=response_status,
            response_time_ms=response_time_ms,
            error_message=error_message,
            business_event=business_event
        )
    except Exception as e:
        # Don't let audit logging failures break the main request
        print(f"Audit logging failed: {e}")

# Models
class JobDescriptionRequest(BaseModel):
    text: str

class ParsedResume(BaseModel):
    text: str
    emails: List[str]
    phones: List[str]

class ParsedJobDescription(BaseModel):
    cleaned_text: str
    skills: List[str]

# Enhanced model for matching request
class MatchRequest(BaseModel):
    resume_text: str
    jd_text: str
    jd_skills: List[str]
    hard_weight: Optional[float] = 0.7  # Default 70% hard skills weight
    soft_weight: Optional[float] = 0.3  # Default 30% soft match weight

class ScoringWeights(BaseModel):
    hard: float
    soft: float

class MatchResult(BaseModel):
    score: float
    hard_score: float
    soft_score: float
    verdict: str
    matched_skills: List[str]
    missing_skills: List[str]
    extracted_resume_skills: List[str]
    common_keywords: List[str]
    feedback: str
    scoring_weights: ScoringWeights

# Enhanced Resume Parsing Models
class PersonalInfo(BaseModel):
    name: Optional[str]
    emails: List[str]
    phones: List[str]

class TechnicalProfile(BaseModel):
    skills: List[str]
    experience_years: Optional[int]
    certifications: List[str]

class Education(BaseModel):
    degree: str
    field: Optional[str]
    year: Optional[str]
    context: str

class ResumeStatistics(BaseModel):
    total_characters: int
    total_words: int
    total_lines: int
    skills_count: int
    education_count: int
    certifications_count: int

class ComprehensiveResumeResult(BaseModel):
    personal_info: PersonalInfo
    technical_profile: TechnicalProfile
    education: List[Education]
    sections: Dict[str, List[str]]
    statistics: ResumeStatistics
    raw_text: str
    filename: str

# Enhanced Job Description Parsing Models
class JobSections(BaseModel):
    requirements: str
    responsibilities: str
    qualifications: str
    benefits: str

class JobStatistics(BaseModel):
    total_characters: int
    total_words: int
    total_lines: int
    must_have_skills_count: int
    nice_to_have_skills_count: int
    qualifications_count: int

class ComprehensiveJobResult(BaseModel):
    role: Optional[str]
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    qualifications: List[str]
    experience_required: Optional[str]
    location: Optional[str]
    sections: JobSections
    statistics: JobStatistics
    cleaned_text: str
    raw_text: str

# Resume Parser
@app.post("/parse-resume", response_model=ParsedResume)
async def parse_resume(file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    """Extract text, emails, and phone numbers from uploaded resume file"""
    start_time = time.time()
    
    try:
        text = await extract_text_from_file(file)
        emails = extract_emails(text)
        phones = extract_phones(text)
        
        # Store basic resume data in database
        resume_data = {
            "filename": file.filename,
            "file_size": len(await file.read()),
            "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown',
            "raw_text": text,
            "emails": emails,
            "phones": phones,
            "total_characters": len(text),
            "total_words": len(text.split()),
            "total_lines": len(text.split('\n')),
            "is_processed": True
        }
        
        try:
            db_resume = resume_repository.create(db, resume_data)
            resume_id = db_resume.id
        except Exception as db_error:
            print(f"Database error: {db_error}")
            resume_id = None
        
        # Reset file position for response
        await file.seek(0)
        
        # Log audit event
        processing_time = int((time.time() - start_time) * 1000)
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_parse",
            event_action="CREATE",
            resource_type="resume",
            resource_id=resume_id,
            response_time_ms=processing_time,
            business_event=f"Resume parsed: {file.filename}"
        )
        
        return {"text": text, "emails": emails, "phones": phones}
        
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_parse",
            event_action="CREATE",
            response_status=500,
            response_time_ms=processing_time,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

# Comprehensive Resume Parser
@app.post("/parse-resume-comprehensive", response_model=ComprehensiveResumeResult)
async def parse_resume_comprehensive_endpoint(file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    """
    Advanced resume parsing with complete entity extraction:
    - Personal info (name, contacts)
    - Technical skills with 50+ technologies
    - Education with degrees and fields
    - Certifications and experience years
    - Section detection and statistics
    """
    start_time = time.time()
    
    try:
        result = await parse_resume_comprehensive(file)
        
        # Store comprehensive resume data in database
        resume_data = {
            "filename": result.get("filename", file.filename),
            "file_size": len(result.get("raw_text", "")),
            "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown',
            "raw_text": result.get("raw_text", ""),
            "candidate_name": result["personal_info"]["name"],
            "emails": result["personal_info"]["emails"],
            "phones": result["personal_info"]["phones"],
            "skills": result["technical_profile"]["skills"],
            "experience_years": result["technical_profile"]["experience_years"],
            "certifications": result["technical_profile"]["certifications"],
            "education": result["education"],
            "sections": result["sections"],
            "total_characters": result["statistics"]["total_characters"],
            "total_words": result["statistics"]["total_words"],
            "total_lines": result["statistics"]["total_lines"],
            "skills_count": result["statistics"]["skills_count"],
            "education_count": result["statistics"]["education_count"],
            "certifications_count": result["statistics"]["certifications_count"],
            "is_processed": True
        }
        
        try:
            db_resume = resume_repository.create(db, resume_data)
            resume_id = db_resume.id
        except Exception as db_error:
            print(f"Database error: {db_error}")
            resume_id = None
        
        # Log audit event
        processing_time = int((time.time() - start_time) * 1000)
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_parse_comprehensive",
            event_action="CREATE",
            resource_type="resume",
            resource_id=resume_id,
            response_time_ms=processing_time,
            business_event=f"Comprehensive resume parsed: {file.filename}"
        )
        
        return result
        
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_parse_comprehensive",
            event_action="CREATE",
            response_status=500,
            response_time_ms=processing_time,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

# Job Description Parser
@app.post("/parse-job", response_model=ParsedJobDescription)
async def parse_job(req: JobDescriptionRequest):
    """Parse job description and extract required skills"""
    return parse_job_description(req.text)

# Comprehensive Job Description Parser
@app.post("/parse-job-comprehensive", response_model=ComprehensiveJobResult)
async def parse_job_comprehensive_endpoint(req: JobDescriptionRequest):
    """
    Advanced job description parsing with complete entity extraction:
    - Role/title detection
    - Must-have vs nice-to-have skills categorization
    - Experience requirements and location
    - Section segmentation (requirements, responsibilities, etc.)
    - Qualification extraction and statistics
    """
    return parse_job_description_comprehensive(req.text)

@app.post("/match-resume-job", response_model=MatchResult)
async def match_resume(req: MatchRequest, request: Request = None, db: Session = Depends(get_db)):
    """
    Enhanced resume-job matching with configurable scoring weights.
    
    - hard_weight: Weight for exact skill matching (default 0.7)
    - soft_weight: Weight for semantic similarity (default 0.3)
    """
    start_time = time.time()
    
    try:
        # Perform matching
        result = match_resume_to_job(
            req.resume_text, 
            req.jd_text, 
            req.jd_skills,
            req.hard_weight,
            req.soft_weight
        )
        
        # Store match result in database (assuming resume and job exist)
        # In a real application, you'd look up the actual resume_id and job_description_id
        match_data = {
            "resume_id": None,  # Would be looked up in real implementation
            "job_description_id": None,  # Would be looked up in real implementation
            "overall_score": result["score"],
            "hard_score": result["hard_score"],
            "soft_score": result["soft_score"],
            "verdict": result["verdict"],
            "hard_weight": req.hard_weight,
            "soft_weight": req.soft_weight,
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "extracted_resume_skills": result["extracted_resume_skills"],
            "common_keywords": result["common_keywords"],
            "feedback": result["feedback"],
            "algorithm_version": "2.0.0",
            "processing_time_ms": int((time.time() - start_time) * 1000),
            "match_context": "api_call"
        }
        
        try:
            if match_data["resume_id"] and match_data["job_description_id"]:
                db_match = match_result_repository.create(db, match_data)
                match_id = db_match.id
            else:
                match_id = None
        except Exception as db_error:
            print(f"Database error: {db_error}")
            match_id = None
        
        # Log audit event
        processing_time = int((time.time() - start_time) * 1000)
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_job_match",
            event_action="CREATE",
            resource_type="match_result",
            resource_id=match_id,
            response_time_ms=processing_time,
            business_event=f"Resume-job matching completed with score: {result['score']}%"
        )
        
        return result
        
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_job_match",
            event_action="CREATE",
            response_status=500,
            response_time_ms=processing_time,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error during matching: {str(e)}")

# Convenience endpoint for file-based matching
class FileMatchResult(BaseModel):
    filename: str
    match_result: MatchResult

@app.post("/match-resume-file", response_model=FileMatchResult)
async def match_resume_file(
    file: UploadFile = File(...),
    jd_text: str = Form(""),
    jd_skills: str = Form(""),  # Comma-separated skills
    hard_weight: float = Form(0.7),
    soft_weight: float = Form(0.3),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Match uploaded resume file against job description.
    jd_skills should be comma-separated (e.g., "python,aws,docker")
    Also stores job description and match results in database.
    """
    start_time = time.time()
    
    try:
        # Parse resume
        resume_text = await extract_text_from_file(file)
        
        # Parse skills from comma-separated string
        skills_list = [skill.strip() for skill in jd_skills.split(",") if skill.strip()]
        
        # Debug print
        print(f"DEBUG: Raw jd_skills input: '{jd_skills}'")
        print(f"DEBUG: Parsed skills_list: {skills_list}")
        
        # Perform matching
        result = match_resume_to_job(resume_text, jd_text, skills_list, hard_weight, soft_weight)
        
        # Store job description in database if provided
        job_description_id = None
        if jd_text.strip():
            try:
                job_data = {
                    "title": "Job from Quick Matcher",
                    "company": "Unknown",
                    "raw_text": jd_text,
                    "must_have_skills": skills_list,
                    "total_words": len(jd_text.split()),
                    "total_characters": len(jd_text),
                    "must_have_skills_count": len(skills_list),
                    "is_processed": True
                }
                db_job = job_description_repository.create(db, job_data)
                job_description_id = db_job.id
                print(f"DEBUG: Stored job description with ID: {job_description_id}")
            except Exception as job_error:
                print(f"Job description storage error: {job_error}")
        
        # Store resume in database if not already stored
        resume_id = None
        try:
            # Check if resume with same filename already exists
            existing_resume = resume_repository.get_by_filename(db, file.filename)
            if existing_resume:
                resume_id = existing_resume.id
                print(f"DEBUG: Found existing resume with ID: {resume_id}")
            else:
                # Store new resume
                resume_data = {
                    "filename": file.filename,
                    "file_size": len(resume_text),
                    "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown',
                    "raw_text": resume_text,
                    "candidate_name": "Unknown",
                    "skills": result.get("extracted_resume_skills", []),
                    "total_words": len(resume_text.split()),
                    "total_characters": len(resume_text),
                    "skills_count": len(result.get("extracted_resume_skills", [])),
                    "is_processed": True
                }
                db_resume = resume_repository.create(db, resume_data)
                resume_id = db_resume.id
                print(f"DEBUG: Stored new resume with ID: {resume_id}")
        except Exception as resume_error:
            print(f"Resume storage error: {resume_error}")
        
        # Store match result in database
        if resume_id and job_description_id:
            try:
                processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
                
                # Convert numpy types to native Python types for PostgreSQL compatibility
                def convert_numpy_types(value):
                    """Convert numpy types to native Python types"""
                    if hasattr(value, 'item'):  # numpy scalar
                        return value.item()
                    return float(value) if isinstance(value, (int, float)) else value
                
                match_data = {
                    "resume_id": resume_id,
                    "job_description_id": job_description_id,
                    "overall_score": convert_numpy_types(result.get("score", 0)),
                    "hard_score": convert_numpy_types(result.get("hard_score", 0)),
                    "soft_score": convert_numpy_types(result.get("soft_score", 0)),
                    "verdict": result.get("verdict", "Low"),
                    "hard_weight": convert_numpy_types(result.get("scoring_weights", {}).get("hard", 0.7)),
                    "soft_weight": convert_numpy_types(result.get("scoring_weights", {}).get("soft", 0.3)),
                    "matched_skills": result.get("matched_skills", []),
                    "missing_skills": result.get("missing_skills", []),
                    "extracted_resume_skills": result.get("extracted_resume_skills", []),
                    "common_keywords": result.get("common_keywords", []),
                    "feedback": result.get("feedback", ""),
                    "processing_time_ms": processing_time,
                    "algorithm_version": "v2.0",
                    "confidence_level": convert_numpy_types(min(result.get("score", 0) / 100.0, 1.0))  # Convert percentage to 0-1
                }
                db_match = match_result_repository.create(db, match_data)
                print(f"DEBUG: Stored match result with ID: {db_match.id}")
            except Exception as match_error:
                print(f"Match result storage error: {match_error}")
        
        # Log audit event
        log_audit_event(
            db=db,
            request=request,
            event_type="match_analysis",
            event_action="CREATE",
            resource_type="match_result",
            business_event=f"Quick match analysis: {result.get('verdict')} match ({result.get('score')}%)"
        )
        
        return {
            "filename": file.filename,
            "match_result": result
        }
        
    except Exception as e:
        log_audit_event(
            db=db,
            request=request,
            event_type="match_analysis",
            event_action="CREATE",
            response_status=500,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

# New Database Endpoints

@app.get("/resumes")
async def get_resumes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get stored resumes with pagination"""
    try:
        resumes = resume_repository.get_multi(db, skip=skip, limit=limit)
        
        # Convert SQLAlchemy objects to dictionaries
        resume_dicts = []
        for resume in resumes:
            resume_dict = {
                "id": resume.id,
                "filename": resume.filename,
                "file_size": resume.file_size,
                "file_type": resume.file_type,
                "candidate_name": resume.candidate_name,
                "emails": resume.emails,
                "phones": resume.phones,
                "skills": resume.skills,
                "experience_years": resume.experience_years,
                "certifications": resume.certifications,
                "education": resume.education,
                "sections": resume.sections,
                "total_characters": resume.total_characters,
                "total_words": resume.total_words,
                "total_lines": resume.total_lines,
                "skills_count": resume.skills_count,
                "education_count": resume.education_count,
                "certifications_count": resume.certifications_count,
                "is_processed": resume.is_processed,
                "processing_error": resume.processing_error,
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
                "updated_at": resume.updated_at.isoformat() if resume.updated_at else None
            }
            resume_dicts.append(resume_dict)
        
        # Log audit event
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_list",
            event_action="VIEW",
            resource_type="resume",
            business_event=f"Retrieved {len(resumes)} resumes"
        )
        
        return {
            "resumes": resume_dicts,
            "total": resume_repository.count(db),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_list",
            event_action="VIEW",
            response_status=500,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/resumes")
async def debug_resumes(db: Session = Depends(get_db)):
    """Debug endpoint to check raw resume data"""
    try:
        resumes = db.query(Resume).limit(5).all()
        debug_data = []
        for resume in resumes:
            debug_data.append({
                "id": resume.id,
                "filename": resume.filename,
                "candidate_name": resume.candidate_name,
                "file_size": resume.file_size,
                "file_type": resume.file_type,
                "is_processed": resume.is_processed,
                "raw_text_length": len(resume.raw_text) if resume.raw_text else 0,
                "skills_count": len(resume.skills) if resume.skills else 0,
                "created_at": str(resume.created_at)
            })
        return {"debug_resumes": debug_data}
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/test-skills")
async def debug_test_skills():
    """Simple test to verify skill extraction works"""
    try:
        from .services.matcher import extract_skills_from_text, compute_hard_match
        
        # Test with known text and skills
        test_resume = "I have experience with Python, machine learning, data science, pandas, and react"
        test_jd_skills = ["python", "machine learning", "data science", "pandas", "javascript"]
        
        # Extract skills
        extracted_skills = extract_skills_from_text(test_resume)
        
        # Compute match
        hard_score = compute_hard_match(extracted_skills, test_jd_skills)
        
        return {
            "test_resume": test_resume,
            "test_jd_skills": test_jd_skills,
            "extracted_skills": extracted_skills,
            "hard_match_score": hard_score,
            "expected_matches": ["python", "machine learning", "data science", "pandas"]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/debug/match-test")
async def debug_match_test(req: MatchRequest):
    """Debug endpoint to test matching logic step by step"""
    try:
        from .services.matcher import extract_skills_from_text, compute_hard_match
        
        # Extract skills from resume
        resume_skills = extract_skills_from_text(req.resume_text)
        
        # Debug the inputs
        debug_info = {
            "jd_skills_input": req.jd_skills,
            "jd_skills_count": len(req.jd_skills),
            "resume_skills_extracted": resume_skills,
            "resume_skills_count": len(resume_skills),
            "resume_text_length": len(req.resume_text),
            "jd_text_length": len(req.jd_text)
        }
        
        # Test hard match
        hard_score = compute_hard_match(resume_skills, req.jd_skills)
        
        debug_info["hard_match_score"] = hard_score
        
        # Test individual skill matching
        resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
        jd_skills_lower = [skill.lower().strip() for skill in req.jd_skills]
        
        individual_matches = []
        for jd_skill in req.jd_skills:
            jd_skill_lower = jd_skill.lower().strip()
            found_in_resume = jd_skill_lower in resume_skills_lower
            individual_matches.append({
                "jd_skill": jd_skill,
                "found_in_resume": found_in_resume,
                "exact_match": jd_skill_lower in resume_skills_lower
            })
        
        debug_info["individual_skill_matches"] = individual_matches
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e), "traceback": str(e.__traceback__)}

@app.post("/debug/extract-skills")
async def debug_extract_skills(text: str):
    """Debug endpoint to test skill extraction"""
    try:
        from .services.matcher import extract_skills_from_text
        skills = extract_skills_from_text(text)
        return {
            "input_text": text[:200] + "..." if len(text) > 200 else text,
            "extracted_skills": skills,
            "skills_count": len(skills)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/resumes/{resume_id}")
async def get_resume(
    resume_id: int, 
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get a specific resume by ID"""
    try:
        resume = resume_repository.get(db, resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Log audit event
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_view",
            event_action="VIEW",
            resource_type="resume",
            resource_id=resume_id,
            business_event=f"Retrieved resume: {resume.filename}"
        )
        
        return resume
    except HTTPException:
        raise
    except Exception as e:
        log_audit_event(
            db=db,
            request=request,
            event_type="resume_view",
            event_action="VIEW",
            response_status=500,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def get_jobs(
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get stored job descriptions with pagination"""
    try:
        if active_only:
            jobs = job_description_repository.get_active_jobs(db, skip=skip, limit=limit)
        else:
            jobs = job_description_repository.get_multi(db, skip=skip, limit=limit)
        
        # Convert SQLAlchemy objects to dictionaries
        job_dicts = []
        for job in jobs:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "role": job.role,
                "salary_range": job.salary_range,
                "must_have_skills": job.must_have_skills,
                "nice_to_have_skills": job.nice_to_have_skills,
                "qualifications": job.qualifications,
                "experience_required": job.experience_required,
                "total_words": job.total_words,
                "total_characters": job.total_characters,
                "must_have_skills_count": job.must_have_skills_count,
                "nice_to_have_skills_count": job.nice_to_have_skills_count,
                "is_processed": job.is_processed,
                "processing_error": job.processing_error,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None
            }
            job_dicts.append(job_dict)
        
        # Log audit event
        log_audit_event(
            db=db,
            request=request,
            event_type="job_list",
            event_action="VIEW",
            resource_type="job_description",
            business_event=f"Retrieved {len(jobs)} job descriptions"
        )
        
        return {
            "jobs": job_dicts,
            "total": job_description_repository.count(db, is_active=True) if active_only else job_description_repository.count(db),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        log_audit_event(
            db=db,
            request=request,
            event_type="job_list",
            event_action="VIEW",
            response_status=500,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matches")
async def get_matches(
    skip: int = 0, 
    limit: int = 100,
    min_score: float = 0.0,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get stored match results with pagination"""
    try:
        if min_score > 0:
            matches = match_result_repository.get_best_matches(db, min_score=min_score, skip=skip, limit=limit)
        else:
            matches = match_result_repository.get_multi(db, skip=skip, limit=limit)
        
        # Convert SQLAlchemy objects to dictionaries
        match_dicts = []
        for match in matches:
            match_dict = {
                "id": match.id,
                "resume_id": match.resume_id,
                "job_description_id": match.job_description_id,
                "overall_score": match.overall_score,
                "hard_score": match.hard_score,
                "soft_score": match.soft_score,
                "verdict": match.verdict,
                "hard_weight": match.hard_weight,
                "soft_weight": match.soft_weight,
                "matched_skills": match.matched_skills,
                "missing_skills": match.missing_skills,
                "extracted_resume_skills": match.extracted_resume_skills,
                "common_keywords": match.common_keywords,
                "feedback": match.feedback,
                "algorithm_version": match.algorithm_version,
                "processing_time_ms": match.processing_time_ms,
                "confidence_level": match.confidence_level,
                "is_bookmarked": match.is_bookmarked,
                "user_rating": match.user_rating,
                "created_at": match.created_at.isoformat() if match.created_at else None,
                "updated_at": match.updated_at.isoformat() if match.updated_at else None
            }
            match_dicts.append(match_dict)
        
        # Log audit event
        log_audit_event(
            db=db,
            request=request,
            event_type="match_list",
            event_action="VIEW",
            resource_type="match_result",
            business_event=f"Retrieved {len(matches)} match results"
        )
        
        return {
            "matches": match_dicts,
            "total": match_result_repository.count(db),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        log_audit_event(
            db=db,
            request=request,
            event_type="match_list",
            event_action="VIEW",
            response_status=500,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics(db: Session = Depends(get_db), request: Request = None):
    """Get comprehensive system statistics"""
    try:
        resume_stats = resume_repository.get_statistics(db)
        job_stats = job_description_repository.get_statistics(db)
        match_stats = match_result_repository.get_statistics(db)
        audit_stats = audit_log_repository.get_statistics(db)
        
        # Log audit event
        log_audit_event(
            db=db,
            request=request,
            event_type="statistics_view",
            event_action="VIEW",
            business_event="Retrieved system statistics"
        )
        
        return {
            "resumes": resume_stats,
            "jobs": job_stats,
            "matches": match_stats,
            "audit": audit_stats
        }
    except Exception as e:
        log_audit_event(
            db=db,
            request=request,
            event_type="statistics_view",
            event_action="VIEW",
            response_status=500,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0, 
    limit: int = 100,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get audit logs with optional filtering"""
    try:
        if event_type:
            logs = audit_log_repository.get_by_event_type(db, event_type, skip=skip, limit=limit)
        else:
            logs = audit_log_repository.get_multi(db, skip=skip, limit=limit)
        
        return {
            "logs": logs,
            "total": audit_log_repository.count(db),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "message": "Enhanced Resume & Job Matcher API", 
        "version": "2.0.0",
        "features": [
            "Advanced skill extraction with 50+ technologies",
            "Stopword-filtered meaningful keywords",
            "Configurable hard/soft scoring weights", 
            "Gap-focused actionable feedback",
            "File upload support",
            "PostgreSQL database storage",
            "Comprehensive audit logging",
            "Statistical analytics"
        ],
        "database_endpoints": [
            "/resumes - Get stored resumes",
            "/jobs - Get stored job descriptions", 
            "/matches - Get match results",
            "/statistics - Get system statistics",
            "/audit-logs - Get audit logs"
        ]
    }
