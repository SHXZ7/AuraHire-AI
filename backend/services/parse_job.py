import re
from typing import Dict, List, Optional, Tuple

# Comprehensive skills dictionary (same as in parse_resume.py for consistency)
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust', 'swift', 
    'kotlin', 'php', 'ruby', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'sass', 'less',
    
    # Frameworks & Libraries
    'react', 'angular', 'vue', 'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi',
    'spring', 'spring boot', 'laravel', 'rails', 'asp.net', 'tensorflow', 'pytorch', 
    'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'opencv', 'keras',
    
    # Databases
    'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'cassandra', 'oracle', 
    'sqlite', 'dynamodb', 'neo4j', 'firebase', 'supabase',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'git', 
    'github', 'gitlab', 'terraform', 'ansible', 'linux', 'ubuntu', 'bash', 'ci/cd',
    'nginx', 'apache', 'helm', 'prometheus', 'grafana',
    
    # Data & Analytics
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
    'big data', 'hadoop', 'spark', 'kafka', 'airflow', 'etl', 'data mining', 'statistics',
    
    # Mobile & Frontend
    'react native', 'flutter', 'ionic', 'xamarin', 'android', 'ios', 'swift ui',
    
    # Other Technologies
    'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira', 'confluence',
    'elasticsearch', 'solr', 'rabbitmq', 'redis', 'memcached'
}

# Education/qualification keywords
QUALIFICATION_KEYWORDS = [
    'b.tech', 'btech', 'b.e', 'be', 'bachelor', 'b.sc', 'bsc', 'b.com', 'bcom',
    'm.tech', 'mtech', 'm.e', 'me', 'master', 'm.sc', 'msc', 'm.com', 'mcom',
    'mba', 'mca', 'phd', 'doctorate', 'diploma', 'associate'
]

# Role/title detection patterns
ROLE_PATTERNS = [
    r'(?:hiring|looking for|seeking|position|role|job title):\s*([^\n\r]+)',
    r'job title:\s*([^\n\r]+)',
    r'position:\s*([^\n\r]+)',
    r'^([A-Z][A-Za-z\s]+(?:Developer|Engineer|Manager|Analyst|Specialist|Lead|Architect))',
    r'we are hiring\s+([^\n\r]+)',
]

# Skill priority indicators
MUST_HAVE_INDICATORS = [
    'required', 'must have', 'mandatory', 'essential', 'necessary', 'minimum requirements',
    'requirements', 'must be', 'should have', 'need to have', 'expertise in'
]

NICE_TO_HAVE_INDICATORS = [
    'preferred', 'nice to have', 'good to have', 'plus', 'bonus', 'additional',
    'desirable', 'advantage', 'would be great', 'ideal candidate'
]

# Boilerplate removal patterns
BOILERPLATE_PATTERNS = [
    r'about\s+(?:the\s+)?company.*?(?=\n\n|\n[A-Z]|requirements|responsibilities)',
    r'company\s+overview.*?(?=\n\n|\n[A-Z]|requirements|responsibilities)',
    r'why\s+join\s+us.*?(?=\n\n|\n[A-Z]|requirements|responsibilities)',
    r'our\s+culture.*?(?=\n\n|\n[A-Z]|requirements|responsibilities)',
    r'benefits.*?(?=\n\n|\n[A-Z]|requirements|responsibilities)',
    r'equal\s+opportunity.*',
    r'we\s+offer.*?(?=\n\n|\n[A-Z]|requirements|responsibilities)',
]

def clean_job_description(text: str) -> str:
    """Remove boilerplate content and normalize the JD text"""
    if not text:
        return ""
    
    # Normalize whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove common boilerplate sections
    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove excessive whitespace again
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extract_role_title(text: str) -> Optional[str]:
    """Extract job role/title from JD text"""
    lines = text.split('\n')[:10]  # Check first 10 lines
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
            
        for pattern in ROLE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                role = match.group(1).strip()
                # Clean up the role
                role = re.sub(r'^[-:\s]+', '', role)
                role = re.sub(r'[-:\s]+$', '', role)
                if 5 <= len(role) <= 100:  # Reasonable length
                    return role
    
    # Fallback: look for lines that might be job titles
    for line in lines:
        line = line.strip()
        if (any(keyword in line.lower() for keyword in 
               ['developer', 'engineer', 'manager', 'analyst', 'lead', 'architect', 'specialist']) 
            and len(line.split()) <= 6):
            return line
    
    return None

def extract_skills_by_priority(text: str) -> Tuple[List[str], List[str]]:
    """Extract must-have vs nice-to-have skills based on context"""
    text_lower = text.lower()
    paragraphs = text.split('\n\n')
    
    must_have_skills = []
    nice_to_have_skills = []
    
    for paragraph in paragraphs:
        paragraph_lower = paragraph.lower()
        
        # Check if paragraph indicates must-have requirements
        is_must_have = any(indicator in paragraph_lower for indicator in MUST_HAVE_INDICATORS)
        is_nice_to_have = any(indicator in paragraph_lower for indicator in NICE_TO_HAVE_INDICATORS)
        
        # Extract skills from this paragraph
        paragraph_skills = []
        for skill in TECHNICAL_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, paragraph_lower):
                paragraph_skills.append(skill)
        
        # Categorize skills based on context
        if is_must_have and not is_nice_to_have:
            must_have_skills.extend(paragraph_skills)
        elif is_nice_to_have and not is_must_have:
            nice_to_have_skills.extend(paragraph_skills)
        else:
            # Default to must-have if unclear
            must_have_skills.extend(paragraph_skills)
    
    # Remove duplicates and sort
    must_have_skills = sorted(list(set(must_have_skills)))
    nice_to_have_skills = sorted(list(set(nice_to_have_skills)))
    
    # Remove nice-to-have skills that are already in must-have
    nice_to_have_skills = [skill for skill in nice_to_have_skills if skill not in must_have_skills]
    
    return must_have_skills, nice_to_have_skills

def extract_qualifications(text: str) -> List[str]:
    """Extract education qualifications from JD"""
    qualifications = []
    text_lower = text.lower()
    
    for qualification in QUALIFICATION_KEYWORDS:
        pattern = r'\b' + re.escape(qualification) + r'\b'
        if re.search(pattern, text_lower):
            qualifications.append(qualification.upper())
    
    return sorted(list(set(qualifications)))

def extract_experience_required(text: str) -> Optional[str]:
    """Extract required experience from JD"""
    experience_patterns = [
        r'(\d+)[-\s]*(?:to|-)[-\s]*(\d+)\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'minimum\s*(\d+)\s*years?\s*experience',
        r'at\s*least\s*(\d+)\s*years?\s*experience',
        r'(\d+)\s*years?\s*minimum\s*experience',
        r'experience:\s*(\d+)[-\s]*(?:to|-)[-\s]*(\d+)\s*years?',
        r'experience:\s*(\d+)\+?\s*years?'
    ]
    
    text_lower = text.lower()
    for pattern in experience_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if len(match.groups()) == 2 and match.group(2):
                # Range pattern
                return f"{match.group(1)}-{match.group(2)} years"
            else:
                # Single number pattern
                years = match.group(1)
                return f"{years}+ years"
    
    return None

def extract_location(text: str) -> Optional[str]:
    """Extract job location from JD"""
    location_patterns = [
        r'location:\s*([^\n\r]+)',
        r'based in:\s*([^\n\r]+)',
        r'office location:\s*([^\n\r]+)',
        r'work location:\s*([^\n\r]+)',
        r'(?:bangalore|mumbai|delhi|pune|hyderabad|chennai|kolkata|gurgaon|noida)',
        r'(?:remote|work from home|wfh)',
        r'(?:san francisco|new york|london|toronto|sydney)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if match.groups():
                location = match.group(1).strip()
                # Clean up location
                location = re.sub(r'^[-:\s]+', '', location)
                location = re.sub(r'[-:\s]+$', '', location)
                return location
            else:
                return match.group(0)
    
    return None

def segment_jd_sections(text: str) -> Dict[str, str]:
    """Segment JD into different sections"""
    sections = {
        'requirements': '',
        'responsibilities': '',
        'qualifications': '',
        'benefits': ''
    }
    
    # Common section headers
    section_patterns = {
        'requirements': [
            r'(?:requirements|required skills|must have|what we need)',
            r'(?:technical requirements|skill requirements)'
        ],
        'responsibilities': [
            r'(?:responsibilities|job description|what you\'ll do|duties)',
            r'(?:role & responsibilities|key responsibilities)'
        ],
        'qualifications': [
            r'(?:qualifications|education|educational background)',
            r'(?:minimum qualifications|preferred qualifications)'
        ],
        'benefits': [
            r'(?:benefits|what we offer|compensation|perks)',
            r'(?:employee benefits|package)'
        ]
    }
    
    paragraphs = text.split('\n\n')
    current_section = None
    
    for paragraph in paragraphs:
        paragraph_lower = paragraph.lower()
        
        # Check if this paragraph starts a new section
        section_found = False
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, paragraph_lower):
                    current_section = section_name
                    sections[section_name] = paragraph
                    section_found = True
                    break
            if section_found:
                break
        
        # If no new section found, append to current section
        if not section_found and current_section:
            sections[current_section] += '\n\n' + paragraph
    
    return sections

def parse_job_description_comprehensive(text: str) -> Dict:
    """
    Comprehensive job description parsing with structured output
    """
    if not text or not text.strip():
        return {"error": "Empty job description"}
    
    # Clean the JD text
    cleaned_text = clean_job_description(text)
    
    # Extract all entities
    role = extract_role_title(text)
    must_have_skills, nice_to_have_skills = extract_skills_by_priority(cleaned_text)
    qualifications = extract_qualifications(cleaned_text)
    experience_required = extract_experience_required(cleaned_text)
    location = extract_location(text)
    sections = segment_jd_sections(cleaned_text)
    
    # Calculate statistics
    stats = {
        'total_characters': len(text),
        'total_words': len(text.split()),
        'total_lines': text.count('\n') + 1,
        'must_have_skills_count': len(must_have_skills),
        'nice_to_have_skills_count': len(nice_to_have_skills),
        'qualifications_count': len(qualifications)
    }
    
    return {
        'role': role,
        'must_have_skills': must_have_skills,
        'nice_to_have_skills': nice_to_have_skills,
        'qualifications': qualifications,
        'experience_required': experience_required,
        'location': location,
        'sections': sections,
        'statistics': stats,
        'cleaned_text': cleaned_text,
        'raw_text': text
    }

def parse_job_description(text: str) -> dict:
    """
    Legacy function for backward compatibility
    Extract basic skills from job description text
    """
    # Clean text
    cleaned_text = re.sub(r"[\n\r\t]+", " ", text).strip()

    # Extract all technical skills
    found_skills = []
    text_lower = cleaned_text.lower()
    
    for skill in TECHNICAL_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return {
        "cleaned_text": cleaned_text,
        "skills": sorted(found_skills)
    }

def parse_job_description(text: str) -> dict:
    """Extract must-have skills from job description text"""
    # Clean text
    cleaned_text = re.sub(r"[\n\r\t]+", " ", text).strip()

    # Simple hardcoded skills (later we’ll connect ML/LLM here)
    predefined_skills = [
        "python", "java", "sql", "aws", "docker",
        "fastapi", "react", "mongodb", "nlp", "machine learning"
    ]

    found_skills = [skill for skill in predefined_skills if skill.lower() in cleaned_text.lower()]

    return {
        "cleaned_text": cleaned_text,
        "skills": found_skills
    }
