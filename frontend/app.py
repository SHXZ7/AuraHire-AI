import streamlit as st
import requests
import json
from typing import Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="AuraHire AI",
    page_icon="🎯",
    layout="wide"
)

# API Configuration
API_BASE_URL = "https://aurahire-ai.onrender.com"

def call_api(endpoint: str, method: str = "GET", data: Dict = None, files: Dict = None) -> Dict[Any, Any]:
    """Helper function to call FastAPI endpoints"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {}

def main():
    # Header
    st.title("🎯 AuraHire AI")
    st.markdown("**AI-powered resume analysis with advanced skill extraction and semantic matching**")
    
    # Sidebar for API status
    with st.sidebar:
        st.markdown("### 🔌 API Status")
        try:
            status = call_api("/")
            if status:
                st.success("✅ API Connected")
                st.json(status)
            else:
                st.error("❌ API Disconnected")
        except:
            st.error("❌ API Disconnected")
            st.markdown("Make sure to run: `uvicorn backend.main:app --reload`")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Quick Match", "📄 Resume Parser", "💼 Job Parser", "📊 Database History"])
    
    # Tab 1: Quick Resume-Job Matching
    with tab1:
        st.header("🚀 Resume-Job Quick Matcher")
        st.markdown("Upload your resume and paste a job description for instant AI analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Resume Upload")
            uploaded_file = st.file_uploader(
                "Choose resume file", 
                type=['pdf', 'docx', 'txt'],
                help="Upload PDF, DOCX, or TXT files"
            )
            
            if uploaded_file:
                st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        with col2:
            st.subheader("💼 Job Description")
            jd_text = st.text_area(
                "Paste job description",
                height=200,
                placeholder="Paste the complete job description here..."
            )
            
            required_skills = st.text_input(
                "Required Skills (comma-separated)",
                placeholder="python, aws, docker, react, sql",
                help="Enter key skills mentioned in the job description"
            )
        
        # Scoring Configuration
        st.subheader("⚙️ Scoring Configuration")
        col3, col4 = st.columns(2)
        
        with col3:
            hard_weight = st.slider(
                "Hard Skills Weight (%)", 
                min_value=0, max_value=100, value=70,
                help="Weight for exact skill matching"
            ) / 100
        
        with col4:
            soft_weight = st.slider(
                "Semantic Match Weight (%)", 
                min_value=0, max_value=100, value=30,
                help="Weight for overall text similarity"
            ) / 100
        
        # Normalize weights
        total_weight = hard_weight + soft_weight
        if total_weight > 0:
            hard_weight = hard_weight / total_weight
            soft_weight = soft_weight / total_weight
        
        st.info(f"📊 Final weights: {hard_weight:.1%} Hard Skills + {soft_weight:.1%} Semantic Match")
        
        # Match button
        if st.button("🎯 Analyze Match", type="primary", use_container_width=True):
            if uploaded_file and jd_text and required_skills:
                with st.spinner("🔍 Analyzing resume against job requirements..."):
                    
                    # Prepare data for API call
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "jd_text": jd_text,
                        "jd_skills": required_skills,
                        "hard_weight": hard_weight,
                        "soft_weight": soft_weight
                    }
                    
                    # Call matching API
                    result = call_api("/match-resume-file", method="POST", data=data, files=files)
                    
                    if result:
                        display_match_results(result.get("match_result", {}))
            else:
                st.warning("⚠️ Please upload a resume, enter job description, and specify required skills")
    
    # Tab 2: Resume Parser
    with tab2:
        st.header("📄 Enhanced Resume Parser & Analyzer")
        st.markdown("Advanced entity extraction with skills, education, certifications, and more")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Upload Resume")
            resume_file = st.file_uploader(
                "Upload Resume", 
                type=['pdf', 'docx', 'txt'],
                key="resume_parser"
            )
        
        with col2:
            st.subheader("� Parsing Options")
            use_comprehensive = st.checkbox(
                "🚀 Use Enhanced Parser", 
                value=True,
                help="Extract skills, education, certifications, and more"
            )
        
        if resume_file and st.button("📤 Parse Resume", use_container_width=True):
            with st.spinner("� Extracting resume content..."):
                files = {"file": (resume_file.name, resume_file.getvalue(), resume_file.type)}
                
                if use_comprehensive:
                    # Use comprehensive parser
                    result = call_api("/parse-resume-comprehensive", method="POST", files=files)
                    
                    if result:
                        st.success("✅ Resume parsed successfully!")
                        display_comprehensive_resume_results(result)
                else:
                    # Use basic parser
                    result = call_api("/parse-resume", method="POST", files=files)
                    
                    if result:
                        st.success("✅ Resume parsed successfully!")
                        display_basic_resume_results(result)
    
    # Tab 3: Job Parser
    with tab3:
        st.header("💼 Enhanced Job Description Parser")
        st.markdown("Advanced job analysis with role detection, skill categorization, and section extraction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_text = st.text_area(
                "Job Description Text",
                height=300,
                placeholder="Paste the complete job description here..."
            )
        
        with col2:
            st.subheader("� Parsing Options")
            use_comprehensive = st.checkbox(
                "🚀 Use Enhanced Parser", 
                value=True,
                help="Extract role, prioritized skills, experience, location, and sections"
            )
            
            st.info("**Enhanced Features:**\n- Role/title detection\n- Must-have vs nice-to-have skills\n- Experience & location extraction\n- Section segmentation")
        
        if job_text and st.button("🔍 Parse Job Description", use_container_width=True):
            with st.spinner("🔎 Analyzing job description..."):
                data = {"text": job_text}
                
                if use_comprehensive:
                    # Use comprehensive parser
                    result = call_api("/parse-job-comprehensive", method="POST", data=data)
                    
                    if result:
                        st.success("✅ Job description analyzed successfully!")
                        display_comprehensive_job_results(result)
                else:
                    # Use basic parser
                    result = call_api("/parse-job", method="POST", data=data)
                    
                    if result:
                        st.success("✅ Job description analyzed successfully!")
                        display_basic_job_results(result)
    
    # Tab 4: Database History
    with tab4:
        st.header("📊 Database History & Analytics")
        st.markdown("View stored resumes, job descriptions, match results, and system analytics")
        
        # Statistics Overview
        st.subheader("📈 System Statistics")
        stats = call_api("/statistics", "GET")
        if stats:
            display_system_statistics(stats)
        
        # Data tabs
        data_tab1, data_tab2, data_tab3, data_tab4 = st.tabs(["📄 Resumes", "💼 Jobs", "🎯 Matches", "📋 Audit Logs"])
        
        with data_tab1:
            st.subheader("📄 Stored Resumes")
            display_stored_resumes()
        
        with data_tab2:
            st.subheader("💼 Stored Job Descriptions")
            display_stored_jobs()
        
        with data_tab3:
            st.subheader("🎯 Match Results")
            display_stored_matches()
        
        with data_tab4:
            st.subheader("📋 Audit Logs")
            display_audit_logs()

def display_match_results(result: Dict):
    """Display comprehensive match results"""
    if not result:
        st.error("❌ No results to display")
        return
    
    st.success("🎉 Match Analysis Complete!")
    
    # Overall Score Card
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = result.get("score", 0)
        verdict = result.get("verdict", "Unknown")
        color = "green" if verdict == "High" else "orange" if verdict == "Medium" else "red"
        st.metric("Overall Score", f"{score}%", help="Combined hard + soft match score")
    
    with col2:
        hard_score = result.get("hard_score", 0)
        st.metric("Skills Match", f"{hard_score}%", help="Exact skill overlap percentage")
    
    with col3:
        soft_score = result.get("soft_score", 0)
        st.metric("Semantic Match", f"{soft_score}%", help="Overall text similarity")
    
    with col4:
        verdict_emoji = "🟢" if verdict == "High" else "🟡" if verdict == "Medium" else "🔴"
        st.metric("Verdict", f"{verdict_emoji} {verdict}", help="Overall match assessment")
    
    # Detailed Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Skills")
        matched = result.get("matched_skills", [])
        if matched:
            for skill in matched:
                st.success(f"✅ {skill}")
        else:
            st.info("No direct skill matches found")
        
        st.subheader("📊 Key Shared Terms")
        keywords = result.get("common_keywords", [])
        if keywords:
            st.write(", ".join(keywords[:10]))
        else:
            st.info("No significant shared keywords")
    
    with col2:
        st.subheader("❌ Missing Skills")
        missing = result.get("missing_skills", [])
        if missing:
            for skill in missing:
                st.error(f"❌ {skill}")
        else:
            st.success("All required skills are present!")
        
        st.subheader("🤖 Extracted Skills from Resume")
        extracted = result.get("extracted_resume_skills", [])
        if extracted:
            st.write(", ".join(extracted[:15]))
        else:
            st.info("No technical skills detected")
    
    # Feedback Section
    st.subheader("💡 Actionable Feedback")
    feedback = result.get("feedback", "No feedback available")
    st.info(feedback)
    
    # Technical Details (Expandable)
    with st.expander("🔧 Technical Details"):
        weights = result.get("scoring_weights", {})
        st.write(f"**Hard Skills Weight:** {weights.get('hard', 0):.1%}")
        st.write(f"**Soft Match Weight:** {weights.get('soft', 0):.1%}")
        
        st.json(result)

def display_comprehensive_resume_results(result: Dict):
    """Display results from comprehensive resume parsing"""
    
    # Personal Information
    personal_info = result.get("personal_info", {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Personal Information")
        name = personal_info.get("name")
        if name:
            st.write(f"**Name:** {name}")
        else:
            st.write("**Name:** Not detected")
        
        emails = personal_info.get("emails", [])
        if emails:
            st.write(f"**Emails:** {', '.join(emails)}")
        else:
            st.write("**Emails:** None found")
        
        phones = personal_info.get("phones", [])
        if phones:
            st.write(f"**Phones:** {', '.join(phones)}")
        else:
            st.write("**Phones:** None found")
    
    with col2:
        st.subheader("📊 Resume Statistics")
        stats = result.get("statistics", {})
        col2a, col2b, col2c = st.columns(3)
        
        with col2a:
            st.metric("Characters", stats.get("total_characters", 0))
            st.metric("Words", stats.get("total_words", 0))
        
        with col2b:
            st.metric("Skills Found", stats.get("skills_count", 0))
            st.metric("Education", stats.get("education_count", 0))
        
        with col2c:
            st.metric("Certifications", stats.get("certifications_count", 0))
            st.metric("Lines", stats.get("total_lines", 0))
    
    # Technical Profile
    technical = result.get("technical_profile", {})
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🛠️ Technical Skills")
        skills = technical.get("skills", [])
        if skills:
            # Display skills in a nice format
            skills_per_row = 3
            for i in range(0, len(skills), skills_per_row):
                skill_cols = st.columns(skills_per_row)
                for j, skill in enumerate(skills[i:i+skills_per_row]):
                    with skill_cols[j]:
                        st.success(f"✅ {skill}")
        else:
            st.info("No technical skills detected")
        
        st.subheader("🏆 Certifications")
        certifications = technical.get("certifications", [])
        if certifications:
            for cert in certifications[:5]:  # Show first 5
                st.write(f"🎓 {cert}")
        else:
            st.info("No certifications found")
    
    with col4:
        st.subheader("🎓 Education")
        education = result.get("education", [])
        if education:
            for edu in education:
                with st.expander(f"📚 {edu.get('degree', 'Unknown Degree')}"):
                    if edu.get('field'):
                        st.write(f"**Field:** {edu['field']}")
                    if edu.get('year'):
                        st.write(f"**Year:** {edu['year']}")
                    if edu.get('context'):
                        st.write(f"**Context:** {edu['context']}")
        else:
            st.info("No education information detected")
        
        exp_years = technical.get("experience_years")
        if exp_years:
            st.metric("Experience", f"{exp_years} years")
    
    # Sections
    st.subheader("📑 Detected Resume Sections")
    sections = result.get("sections", {})
    if sections:
        for section_name, content in sections.items():
            with st.expander(f"📂 {section_name.title()} ({len(content)} items)"):
                for item in content[:10]:  # Show first 10 items
                    if item.strip():
                        st.write(f"• {item[:100]}...")  # Truncate long items
    else:
        st.info("No distinct sections detected")
    
    # Raw text in expandable section
    with st.expander("📝 Full Resume Text"):
        st.text_area("Raw Text", result.get("raw_text", ""), height=400, disabled=True)

def display_basic_resume_results(result: Dict):
    """Display results from basic resume parsing"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📧 Contact Information")
        if result.get("emails"):
            st.write("**Emails:**", ", ".join(result["emails"]))
        else:
            st.write("**Emails:** None found")
        
        if result.get("phones"):
            st.write("**Phones:**", ", ".join(result["phones"]))
        else:
            st.write("**Phones:** None found")
    
    with col2:
        st.subheader("📊 Text Stats")
        text = result.get("text", "")
        st.metric("Characters", len(text))
        st.metric("Words", len(text.split()))
        st.metric("Lines", text.count('\n') + 1)
    
    # Full text
    st.subheader("📝 Extracted Text")
    st.text_area("Resume Content", result.get("text", ""), height=300, disabled=True)

def display_comprehensive_job_results(result: Dict):
    """Display results from comprehensive job description parsing"""
    
    # Job Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎯 Job Overview")
        role = result.get("role")
        if role:
            st.write(f"**Role:** {role}")
        else:
            st.write("**Role:** Not detected")
        
        location = result.get("location")
        if location:
            st.write(f"**📍 Location:** {location}")
        else:
            st.write("**📍 Location:** Not specified")
        
        experience = result.get("experience_required")
        if experience:
            st.write(f"**⏱️ Experience:** {experience}")
        else:
            st.write("**⏱️ Experience:** Not specified")
    
    with col2:
        st.subheader("📊 Job Statistics")
        stats = result.get("statistics", {})
        
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric("Must-Have Skills", stats.get("must_have_skills_count", 0))
            st.metric("Nice-to-Have Skills", stats.get("nice_to_have_skills_count", 0))
        
        with col2b:
            st.metric("Qualifications", stats.get("qualifications_count", 0))
            st.metric("Total Words", stats.get("total_words", 0))
    
    with col3:
        st.subheader("🎓 Qualifications")
        qualifications = result.get("qualifications", [])
        if qualifications:
            for qual in qualifications:
                st.write(f"🎓 {qual}")
        else:
            st.info("No specific qualifications mentioned")
    
    # Skills Analysis
    col4, col5 = st.columns(2)
    
    with col4:
        st.subheader("🚨 Must-Have Skills")
        must_have = result.get("must_have_skills", [])
        if must_have:
            # Display skills in a grid
            skills_per_row = 2
            for i in range(0, len(must_have), skills_per_row):
                skill_cols = st.columns(skills_per_row)
                for j, skill in enumerate(must_have[i:i+skills_per_row]):
                    with skill_cols[j]:
                        st.error(f"🔴 {skill}")
        else:
            st.info("No must-have skills detected")
    
    with col5:
        st.subheader("✨ Nice-to-Have Skills")
        nice_to_have = result.get("nice_to_have_skills", [])
        if nice_to_have:
            # Display skills in a grid
            skills_per_row = 2
            for i in range(0, len(nice_to_have), skills_per_row):
                skill_cols = st.columns(skills_per_row)
                for j, skill in enumerate(nice_to_have[i:i+skills_per_row]):
                    with skill_cols[j]:
                        st.warning(f"🟡 {skill}")
        else:
            st.info("No nice-to-have skills detected")
    
    # Section Analysis
    st.subheader("📑 Job Description Sections")
    sections = result.get("sections", {})
    
    if any(section.strip() for section in sections.values()):
        section_tabs = st.tabs(["📋 Requirements", "🎯 Responsibilities", "🎓 Qualifications", "🎁 Benefits"])
        
        with section_tabs[0]:
            requirements = sections.get("requirements", "").strip()
            if requirements:
                st.write(requirements)
            else:
                st.info("No requirements section detected")
        
        with section_tabs[1]:
            responsibilities = sections.get("responsibilities", "").strip()
            if responsibilities:
                st.write(responsibilities)
            else:
                st.info("No responsibilities section detected")
        
        with section_tabs[2]:
            qualifications_section = sections.get("qualifications", "").strip()
            if qualifications_section:
                st.write(qualifications_section)
            else:
                st.info("No qualifications section detected")
        
        with section_tabs[3]:
            benefits = sections.get("benefits", "").strip()
            if benefits:
                st.write(benefits)
            else:
                st.info("No benefits section detected")
    else:
        st.info("No distinct sections detected in the job description")
    
    # Raw text in expandable section
    with st.expander("📝 Full Job Description Text"):
        col_clean, col_raw = st.columns(2)
        
        with col_clean:
            st.subheader("🧹 Cleaned Text")
            st.text_area("Cleaned JD", result.get("cleaned_text", ""), height=300, disabled=True)
        
        with col_raw:
            st.subheader("📄 Original Text")
            st.text_area("Raw JD", result.get("raw_text", ""), height=300, disabled=True)

def display_basic_job_results(result: Dict):
    """Display results from basic job description parsing"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛠️ Extracted Skills")
        skills = result.get("skills", [])
        if skills:
            for i, skill in enumerate(skills, 1):
                st.write(f"{i}. **{skill}**")
        else:
            st.write("No skills detected")
        
        st.metric("Total Skills Found", len(skills))
    
    with col2:
        st.subheader("📊 Text Analysis")
        cleaned_text = result.get("cleaned_text", "")
        st.metric("Characters", len(cleaned_text))
        st.metric("Words", len(cleaned_text.split()))
    
    # Cleaned text
    st.subheader("🧹 Cleaned Job Description")
    st.text_area("Processed Text", cleaned_text, height=200, disabled=True)

def display_system_statistics(stats: Dict):
    """Display comprehensive system statistics"""
    if not stats:
        st.error("❌ No statistics available")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        resume_stats = stats.get("resumes", {})
        st.metric("Total Resumes", resume_stats.get("total_resumes", 0))
        st.metric("Processing Success Rate", f"{resume_stats.get('processing_success_rate', 0)}%")
    
    with col2:
        job_stats = stats.get("jobs", {})
        st.metric("Total Jobs", job_stats.get("total_jobs", 0))
        st.metric("Active Jobs", job_stats.get("active_jobs", 0))
    
    with col3:
        match_stats = stats.get("matches", {})
        st.metric("Total Matches", match_stats.get("total_matches", 0))
        st.metric("Recent Matches (7d)", match_stats.get("recent_matches_7_days", 0))
    
    with col4:
        audit_stats = stats.get("audit", {})
        st.metric("Total Events", audit_stats.get("total_events", 0))
        st.metric("Error Rate", f"{audit_stats.get('error_rate', 0)}%")
    
    # Detailed statistics
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("📊 Match Score Distribution")
        if "matches" in stats and "score_statistics" in stats["matches"]:
            score_stats = stats["matches"]["score_statistics"]
            st.metric("Average Score", f"{score_stats.get('average_overall_score', 0)}%")
            st.metric("Average Hard Score", f"{score_stats.get('average_hard_score', 0)}%")
            st.metric("Average Soft Score", f"{score_stats.get('average_soft_score', 0)}%")
        
        # Verdict distribution
        if "matches" in stats and "verdict_distribution" in stats["matches"]:
            verdict_dist = stats["matches"]["verdict_distribution"]
            st.write("**Verdict Distribution:**")
            for verdict, count in verdict_dist.items():
                st.write(f"- {verdict}: {count}")
    
    with col6:
        st.subheader("🏢 Top Companies & Locations")
        if "jobs" in stats:
            job_stats = stats["jobs"]
            
            # Top companies
            if "top_companies" in job_stats:
                st.write("**Top Companies:**")
                for company_data in job_stats["top_companies"][:5]:
                    st.write(f"- {company_data['company']}: {company_data['count']} jobs")
            
            # Top locations
            if "top_locations" in job_stats:
                st.write("**Top Locations:**")
                for location_data in job_stats["top_locations"][:5]:
                    st.write(f"- {location_data['location']}: {location_data['count']} jobs")

def display_stored_resumes():
    """Display stored resumes with pagination"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Browse all stored resume files and their processing status")
    
    with col2:
        page_size = st.selectbox("Items per page", [10, 25, 50, 100], index=1)
        page_num = st.number_input("Page", min_value=1, value=1) - 1
    
    # Fetch resumes
    skip = page_num * page_size
    resumes_data = call_api(f"/resumes?skip={skip}&limit={page_size}", "GET")
    
    if resumes_data and "resumes" in resumes_data:
        resumes = resumes_data["resumes"]
        total = resumes_data.get("total", 0)
        
        st.write(f"Showing {len(resumes)} of {total} resumes")
        
        # Display resumes in a table-like format
        for resume in resumes:
            # Helper function to safely get resume fields
            def get_resume_field(obj, field, default=None):
                if isinstance(obj, dict):
                    return obj.get(field, default)
                else:
                    return getattr(obj, field, default)
            
            # Handle both dict and object-like access patterns
            filename = get_resume_field(resume, 'filename', 'Unknown File')
            resume_id = get_resume_field(resume, 'id', 'N/A')
            
            with st.expander(f"📄 {filename} (ID: {resume_id})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Candidate:** {get_resume_field(resume, 'candidate_name', 'Unknown')}")
                    st.write(f"**File Type:** {get_resume_field(resume, 'file_type', 'Unknown')}")
                    st.write(f"**File Size:** {get_resume_field(resume, 'file_size', 0)} bytes")
                    st.write(f"**Processed:** {'✅' if get_resume_field(resume, 'is_processed') else '❌'}")
                
                with col2:
                    st.write(f"**Skills Count:** {get_resume_field(resume, 'skills_count', 0)}")
                    st.write(f"**Experience:** {get_resume_field(resume, 'experience_years', 'Unknown')} years")
                    st.write(f"**Education Count:** {get_resume_field(resume, 'education_count', 0)}")
                    st.write(f"**Certifications:** {get_resume_field(resume, 'certifications_count', 0)}")
                
                with col3:
                    st.write(f"**Total Words:** {get_resume_field(resume, 'total_words', 0)}")
                    st.write(f"**Created:** {get_resume_field(resume, 'created_at', 'Unknown')}")
                    processing_error = get_resume_field(resume, 'processing_error')
                    if processing_error:
                        st.error(f"Error: {processing_error}")
                
                # Show skills if available
                skills = get_resume_field(resume, 'skills')
                if skills:
                    st.write("**Skills:**")
                    skills_text = ", ".join(skills[:10])  # Show first 10 skills
                    if len(skills) > 10:
                        skills_text += f" ... (+{len(skills) - 10} more)"
                    st.write(skills_text)
    else:
        st.info("No resumes found in the database.")

def display_stored_jobs():
    """Display stored job descriptions with pagination"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write("Browse all stored job descriptions")
    
    with col2:
        active_only = st.checkbox("Active only", True)
        page_size = st.selectbox("Items per page", [10, 25, 50], index=1, key="jobs_page_size")
    
    with col3:
        page_num = st.number_input("Page", min_value=1, value=1, key="jobs_page") - 1
    
    # Fetch jobs
    skip = page_num * page_size
    jobs_data = call_api(f"/jobs?skip={skip}&limit={page_size}&active_only={active_only}", "GET")
    
    if jobs_data and "jobs" in jobs_data:
        jobs = jobs_data["jobs"]
        total = jobs_data.get("total", 0)
        
        st.write(f"Showing {len(jobs)} of {total} job descriptions")
        
        # Display jobs
        for job in jobs:
            with st.expander(f"💼 {job.get('title', 'Unknown Title')} - {job.get('company', 'Unknown Company')} (ID: {job['id']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Role:** {job.get('role', 'Unknown')}")
                    st.write(f"**Location:** {job.get('location', 'Unknown')}")
                    st.write(f"**Job Type:** {job.get('job_type', 'Unknown')}")
                    st.write(f"**Experience Required:** {job.get('experience_required', 'Unknown')}")
                
                with col2:
                    st.write(f"**Must-have Skills:** {job.get('must_have_skills_count', 0)}")
                    st.write(f"**Nice-to-have Skills:** {job.get('nice_to_have_skills_count', 0)}")
                    st.write(f"**Qualifications:** {job.get('qualifications_count', 0)}")
                    st.write(f"**Active:** {'✅' if job.get('is_active') else '❌'}")
                
                with col3:
                    st.write(f"**Total Words:** {job.get('total_words', 0)}")
                    st.write(f"**Industry:** {job.get('industry', 'Unknown')}")
                    st.write(f"**Created:** {job.get('created_at', 'Unknown')}")
                    if job.get('processing_error'):
                        st.error(f"Error: {job['processing_error']}")
                
                # Show skills if available
                if job.get('must_have_skills'):
                    st.write("**Must-have Skills:**")
                    skills_text = ", ".join(job['must_have_skills'][:8])
                    if len(job['must_have_skills']) > 8:
                        skills_text += f" ... (+{len(job['must_have_skills']) - 8} more)"
                    st.write(skills_text)
    else:
        st.info("No job descriptions found in the database.")

def display_stored_matches():
    """Display stored match results with pagination"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write("Browse all match results between resumes and jobs")
    
    with col2:
        min_score = st.slider("Min Score", 0.0, 100.0, 0.0, 5.0)
        page_size = st.selectbox("Items per page", [10, 25, 50], index=1, key="matches_page_size")
    
    with col3:
        page_num = st.number_input("Page", min_value=1, value=1, key="matches_page") - 1
    
    # Fetch matches
    skip = page_num * page_size
    matches_data = call_api(f"/matches?skip={skip}&limit={page_size}&min_score={min_score}", "GET")
    
    if matches_data and "matches" in matches_data:
        matches = matches_data["matches"]
        total = matches_data.get("total", 0)
        
        st.write(f"Showing {len(matches)} of {total} match results")
        
        # Display matches
        for match in matches:
            score = match.get('overall_score', 0)
            verdict = match.get('verdict', 'Unknown')
            verdict_emoji = "🟢" if verdict == "High" else "🟡" if verdict == "Medium" else "🔴"
            
            with st.expander(f"{verdict_emoji} Score: {score}% ({verdict}) - Match ID: {match['id']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Scores:**")
                    st.write(f"- Overall: {score}%")
                    st.write(f"- Hard Skills: {match.get('hard_score', 0)}%")
                    st.write(f"- Soft Match: {match.get('soft_score', 0)}%")
                    st.write(f"- Verdict: {verdict}")
                
                with col2:
                    st.write("**Skills Analysis:**")
                    matched_skills = match.get('matched_skills', [])
                    missing_skills = match.get('missing_skills', [])
                    st.write(f"- Matched: {len(matched_skills)}")
                    st.write(f"- Missing: {len(missing_skills)}")
                    st.write(f"- Processing Time: {match.get('processing_time_ms', 0)}ms")
                
                with col3:
                    st.write("**Metadata:**")
                    st.write(f"- Algorithm: {match.get('algorithm_version', 'Unknown')}")
                    st.write(f"- Context: {match.get('match_context', 'Unknown')}")
                    st.write(f"- Created: {match.get('created_at', 'Unknown')}")
                    if match.get('is_bookmarked'):
                        st.write("⭐ Bookmarked")
                
                # Show feedback if available
                if match.get('feedback'):
                    st.write("**Feedback:**")
                    st.info(match['feedback'])
                
                # Show matched skills
                if matched_skills:
                    st.write("**Matched Skills:**")
                    st.write(", ".join(matched_skills[:10]))
                    if len(matched_skills) > 10:
                        st.write(f"... and {len(matched_skills) - 10} more")
    else:
        st.info("No match results found in the database.")

def display_audit_logs():
    """Display audit logs with filtering"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write("System audit logs for monitoring and troubleshooting")
    
    with col2:
        event_types = ["All", "resume_parse", "job_parse", "resume_job_match", "statistics_view"]
        selected_event = st.selectbox("Event Type", event_types)
        page_size = st.selectbox("Items per page", [10, 25, 50], index=1, key="audit_page_size")
    
    with col3:
        page_num = st.number_input("Page", min_value=1, value=1, key="audit_page") - 1
    
    # Fetch audit logs
    skip = page_num * page_size
    endpoint = f"/audit-logs?skip={skip}&limit={page_size}"
    if selected_event != "All":
        endpoint += f"&event_type={selected_event}"
    
    logs_data = call_api(endpoint, "GET")
    
    if logs_data and "logs" in logs_data:
        logs = logs_data["logs"]
        total = logs_data.get("total", 0)
        
        st.write(f"Showing {len(logs)} of {total} audit log entries")
        
        # Display logs
        for log in logs:
            status_color = "🟢" if log.get('response_status', 200) < 400 else "🔴"
            
            with st.expander(f"{status_color} {log.get('event_type', 'Unknown')} - {log.get('event_timestamp', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Event:** {log.get('event_type', 'Unknown')} - {log.get('event_action', 'Unknown')}")
                    st.write(f"**Endpoint:** {log.get('endpoint', 'Unknown')}")
                    st.write(f"**Method:** {log.get('http_method', 'Unknown')}")
                    st.write(f"**Status:** {log.get('response_status', 'Unknown')}")
                    st.write(f"**Response Time:** {log.get('response_time_ms', 0)}ms")
                
                with col2:
                    st.write(f"**Resource:** {log.get('resource_type', 'Unknown')} ID: {log.get('resource_id', 'N/A')}")
                    st.write(f"**IP Address:** {log.get('ip_address', 'Unknown')}")
                    st.write(f"**Business Event:** {log.get('business_event', 'Unknown')}")
                    
                    if log.get('error_message'):
                        st.error(f"Error: {log['error_message']}")
    else:
        st.info("No audit logs found.")

def add_footer():
    """Add footer with developer information"""
    st.markdown("---")
    
    # Footer with centered content
    st.markdown("""
    <div style='text-align: center; padding: 20px; margin-top: 50px;'>
        <h4>🚀 Built by Mohammed Shaaz</h4>
        <p style='margin: 10px 0;'>
            📧 <a href='mailto:shaazney123@gmail.com' style='text-decoration: none;'>shaazney123@gmail.com</a> | 
            💻 <a href='https://github.com/SHXZ7/AuraHire-AI.git' target='_blank' style='text-decoration: none;'>GitHub Repository</a>
        </p>
        <p style='color: #666; font-size: 0.9em; margin-top: 15px;'>
            ⚡ Enhanced Resume-Job Matcher with PostgreSQL | FastAPI + Streamlit | AI-Powered Skill Matching
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    add_footer()