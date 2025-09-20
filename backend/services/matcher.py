# backend/services/matcher.py

from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Set

# Initialize embedding model lazily
embedding_model = None

def get_embedding_model():
    """Lazy loading of sentence transformer model"""
    global embedding_model
    if embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load sentence transformer model: {e}")
            embedding_model = False  # Mark as failed
    return embedding_model

# Extended stopwords for better keyword filtering
EXTENDED_STOPWORDS = set(ENGLISH_STOP_WORDS).union({
    'experience', 'years', 'work', 'working', 'job', 'position', 'role', 'responsibilities',
    'requirements', 'skills', 'knowledge', 'ability', 'strong', 'good', 'excellent',
    'looking', 'seeking', 'candidate', 'must', 'should', 'preferred', 'plus'
})

def extract_skills_from_text(text: str, skills_dictionary: List[str] = None) -> List[str]:
    """
    Enhanced skill extraction with case-insensitive matching and multi-word skills.
    """
    if not skills_dictionary:
        # Comprehensive skills list with common variations
        skills_dictionary = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'csharp', 'go', 'golang', 'rust', 'swift', 'kotlin',
            'php', 'ruby', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'shell', 'powershell',
            
            # Frameworks & Libraries  
            'react', 'reactjs', 'angular', 'angularjs', 'vue', 'vuejs', 'node.js', 'nodejs', 'express', 'expressjs',
            'django', 'flask', 'fastapi', 'spring', 'springboot', 'laravel', 'rails', 'rubyonrails',
            'tensorflow', 'pytorch', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'opencv',
            'jquery', 'bootstrap', 'tailwind', 'sass', 'less',
            
            # Databases
            'mongodb', 'mongo', 'postgresql', 'postgres', 'mysql', 'redis', 'elasticsearch', 'cassandra',
            'oracle', 'sqlite', 'dynamodb', 'neo4j', 'mariadb',
            
            # Cloud & DevOps
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud', 'google cloud platform',
            'docker', 'kubernetes', 'k8s', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
            'terraform', 'ansible', 'puppet', 'chef', 'linux', 'ubuntu', 'centos', 'redhat',
            'ci/cd', 'cicd', 'devops', 'nginx', 'apache', 'tomcat',
            
            # Data & Analytics
            'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'ml', 'nlp', 
            'natural language processing', 'computer vision', 'data science', 'data analytics',
            'big data', 'hadoop', 'spark', 'kafka', 'airflow', 'etl', 'data mining', 'statistics',
            'tableau', 'power bi', 'powerbi', 'looker', 'qlikview',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova', 'phonegap',
            
            # Web Technologies
            'rest api', 'restful', 'graphql', 'soap', 'json', 'xml', 'ajax', 'websockets',
            'microservices', 'api', 'web services', 'http', 'https',
            
            # Testing & Quality
            'testing', 'unit testing', 'integration testing', 'selenium', 'jest', 'mocha', 'chai',
            'pytest', 'junit', 'testng', 'cucumber',
            
            # Methodologies & Tools
            'agile', 'scrum', 'kanban', 'jira', 'confluence', 'slack', 'trello', 'asana',
            'project management', 'product management'
        ]
    
    text_lower = text.lower()
    found_skills = []
    
    # Sort skills by length (longest first) to catch multi-word skills first
    sorted_skills = sorted(skills_dictionary, key=len, reverse=True)
    
    for skill in sorted_skills:
        skill_lower = skill.lower()
        # Use word boundaries for exact matching, but also check for partial matches
        patterns = [
            r'\b' + re.escape(skill_lower) + r'\b',  # Exact word boundary match
            r'\b' + re.escape(skill_lower.replace(' ', r'[-\s]')) + r'\b',  # Handle spaces/hyphens
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found_skills.append(skill)
                break  # Found this skill, move to next
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in found_skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            seen.add(skill_lower)
            unique_skills.append(skill)
    
    return unique_skills

def filter_meaningful_keywords(keywords: Set[str], min_length: int = 3) -> List[str]:
    """
    Filter out stopwords and short/meaningless words from keywords.
    """
    meaningful = []
    for word in keywords:
        if (len(word) >= min_length and 
            word.lower() not in EXTENDED_STOPWORDS and 
            word.isalpha() and 
            not word.isdigit()):
            meaningful.append(word.lower())
    
    return sorted(list(set(meaningful)))

def compute_hard_match(resume_skills: List[str], jd_skills: List[str]) -> float:
    """
    Enhanced hard match using skill overlap percentage with fuzzy matching.
    """
    if not jd_skills:
        return 0.0
    
    resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
    jd_skills_lower = [skill.lower().strip() for skill in jd_skills]
    
    matched_count = 0
    
    print(f"DEBUG MATCHING:")
    print(f"  Resume skills: {resume_skills_lower}")
    print(f"  JD skills: {jd_skills_lower}")
    
    for i, jd_skill in enumerate(jd_skills_lower):
        is_matched = False
        match_type = "none"
        
        # Exact match
        if jd_skill in resume_skills_lower:
            matched_count += 1
            is_matched = True
            match_type = "exact"
        else:
            # Fuzzy matching for variations
            for resume_skill in resume_skills_lower:
                # Check if one skill contains the other (for variations like "react" vs "reactjs")
                if (jd_skill in resume_skill or resume_skill in jd_skill) and len(jd_skill) > 2:
                    matched_count += 1
                    is_matched = True
                    match_type = f"fuzzy ({resume_skill})"
                    break
        
        print(f"  {i+1}. '{jd_skill}' -> {match_type} {'✓' if is_matched else '✗'}")
    
    skill_match_percentage = (matched_count / len(jd_skills)) * 100
    print(f"  Final: {matched_count}/{len(jd_skills)} = {skill_match_percentage}%")
    
    return round(skill_match_percentage, 2)

def compute_soft_match(resume_text: str, jd_text: str) -> float:
    """
    Soft match using sentence embeddings + cosine similarity.
    """
    try:
        model = get_embedding_model()
        if model:
            embeddings = model.encode([resume_text, jd_text])
            sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return round(sim * 100, 2)
        else:
            # Fallback to TF-IDF if embedding model fails
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(sim * 100, 2)
    except Exception:
        # Fallback to TF-IDF if embedding fails
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(sim * 100, 2)

def generate_gap_focused_feedback(missing_skills: List[str], matched_skills: List[str]) -> str:
    """
    Generate actionable feedback based on skill gaps.
    """
    feedback_parts = []
    
    if missing_skills:
        # Categorize missing skills
        programming_langs = [s for s in missing_skills if s.lower() in 
                           ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust']]
        cloud_skills = [s for s in missing_skills if s.lower() in 
                       ['aws', 'azure', 'gcp', 'docker', 'kubernetes']]
        data_skills = [s for s in missing_skills if s.lower() in 
                      ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas']]
        
        if programming_langs:
            feedback_parts.append(f"📚 Programming: Consider learning {', '.join(programming_langs[:3])}")
        
        if cloud_skills:
            feedback_parts.append(f"☁️ Cloud: Add projects showcasing {', '.join(cloud_skills[:2])} deployment")
        
        if data_skills:
            feedback_parts.append(f"🤖 Data Science: Build portfolio projects with {', '.join(data_skills[:2])}")
        
        # General advice for other missing skills
        other_skills = [s for s in missing_skills if s not in programming_langs + cloud_skills + data_skills]
        if other_skills:
            feedback_parts.append(f"🛠️ Technical: Gain experience with {', '.join(other_skills[:3])}")
    
    if matched_skills:
        feedback_parts.append(f"✅ Strong match in: {', '.join(matched_skills[:5])}")
    
    if not feedback_parts:
        feedback_parts.append("🎉 Excellent skill alignment! No major gaps detected.")
    
    return " | ".join(feedback_parts)

def match_resume_to_job(resume_text: str, jd_text: str, jd_skills: List[str], 
                       hard_weight: float = 0.7, soft_weight: float = 0.3) -> Dict:
    """
    Enhanced main matching function with improved skill extraction and feedback.
    
    Args:
        resume_text: Raw resume text
        jd_text: Raw job description text  
        jd_skills: Required skills from job description
        hard_weight: Weight for hard skill matching (default 0.7)
        soft_weight: Weight for soft semantic matching (default 0.3)
    """
    
    # Extract skills from resume using enhanced method
    resume_skills = extract_skills_from_text(resume_text)
    
    # Compute matching scores
    hard_score = compute_hard_match(resume_skills, jd_skills)
    soft_score = compute_soft_match(resume_text, jd_text)
    
    # Weighted final score (adjustable)
    final_score = round(hard_weight * hard_score + soft_weight * soft_score, 2)
    
    # Verdict with adjusted thresholds
    if final_score >= 75:
        verdict = "High"
    elif final_score >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"
    
    # Skill analysis with improved matching - use same logic as compute_hard_match
    resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
    jd_skills_lower = [skill.lower().strip() for skill in jd_skills]
    
    matched_skills = []
    missing_skills = []
    
    # Define variations once
    variations = {
        'javascript': ['js', 'node.js', 'nodejs'],
        'typescript': ['ts'],
        'python': ['py'],
        'postgresql': ['postgres'],
        'mongodb': ['mongo'],
        'kubernetes': ['k8s'],
        'amazon web services': ['aws'],
        'google cloud platform': ['gcp', 'google cloud'],
        'microsoft azure': ['azure'],
        'machine learning': ['ml'],
        'artificial intelligence': ['ai'],
        'natural language processing': ['nlp'],
        'react': ['reactjs'],
        'angular': ['angularjs'],
        'vue': ['vuejs'],
        'node.js': ['nodejs', 'node'],
        'express': ['expressjs'],
        'scikit-learn': ['sklearn']
    }
    
    for jd_skill in jd_skills:
        jd_skill_lower = jd_skill.lower().strip()
        is_matched = False
        
        # Exact match
        if jd_skill_lower in resume_skills_lower:
            matched_skills.append(jd_skill)
            is_matched = True
        else:
            # Fuzzy matching
            for resume_skill in resume_skills:
                resume_skill_lower = resume_skill.lower().strip()
                
                # Partial match
                if (jd_skill_lower in resume_skill_lower or resume_skill_lower in jd_skill_lower) and len(jd_skill_lower) > 2:
                    matched_skills.append(jd_skill)
                    is_matched = True
                    break
            
            # Variation matching
            if not is_matched:
                for main_skill, variants in variations.items():
                    if ((jd_skill_lower == main_skill and any(v in resume_skills_lower for v in variants)) or 
                        (jd_skill_lower in variants and main_skill in resume_skills_lower)):
                        matched_skills.append(jd_skill)
                        is_matched = True
                        break
        
        if not is_matched:
            missing_skills.append(jd_skill)
    
    # Enhanced keyword extraction with stopword filtering
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    common_keywords_raw = resume_words & jd_words
    common_keywords = filter_meaningful_keywords(common_keywords_raw)
    
    # Generate actionable feedback
    feedback = generate_gap_focused_feedback(missing_skills, matched_skills)
    
    return {
        "score": final_score,
        "hard_score": hard_score,
        "soft_score": soft_score,
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extracted_resume_skills": resume_skills,
        "common_keywords": common_keywords[:15],  # Top 15 meaningful keywords
        "feedback": feedback,
        "scoring_weights": {"hard": hard_weight, "soft": soft_weight}
    }
