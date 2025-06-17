"""
Job search service for retrieving and processing job data.
"""
import os
import logging
import re
import json
from datetime import datetime
from models import get_db
from app.services.ai_service import generate_llm_response

logger = logging.getLogger(__name__)

# Database configuration
MONGODB_URI = os.environ.get('MONGODB_URI')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'job_postings_db')
COLLECTION_NAME = 'linkedin_jobs'


def _build_search_query(
        query: str,
        tech_skills: list = None,
        job_level: str = None) -> dict:
  """Builds the MongoDB search query."""
  search_conditions = [{"$text": {"$search": f'"{query}"'}}]
  if job_level:
    search_conditions.append(
        {"job level": {"$regex": job_level, "$options": "i"}})

  if tech_skills:
    skills_regex = "|".join(re.escape(skill) for skill in tech_skills)
    search_conditions.append(
        {"job_skills": {"$regex": skills_regex, "$options": "i"}})

  return {"$and": search_conditions} if len(
      search_conditions) > 1 else search_conditions[0]


def generate_job_description(job_title: str, company: str, skills: list, job_level: str, job_type: str, location: str) -> str:
  """Generate a markdown job description using AI based on job details."""
  skills_str = ", ".join(skills) if skills else "Not specified"
  
  prompt = f"""Generate a job description for {job_title} at {company} ({job_level}, {job_type}, {location}).

Required skills: {skills_str}

Use ONLY these sections in markdown format:
## About Us
## Job Summary  
## Responsibilities
## Qualifications
## Preferred Qualifications
## What We Offer

Return only the formatted description. DO NOT INLCUDE markdown backticks."""

  try:
    logger.info(f"Generating job description for {job_title} at {company}")
    response = generate_llm_response(prompt)
    return response.strip()
  except Exception as e:
    logger.error(f"Failed to generate job description: {str(e)}")
    return f"## {job_title}\n\n**Company:** {company}\n\n**Location:** {location}\n\nWe are looking for a talented {job_title} to join our team."


def _format_job_results(raw_jobs: list) -> list:
  """Formats raw job data from the database."""
  formatted_jobs = []
  
  for job in raw_jobs:
    job_title = job.get('job_title', 'N/A')
    company = job.get('company', 'N/A')
    location = job.get('job_location', 'N/A')
    skills = parse_skills(job.get('job_skills', ''))
    job_level = job.get('job level', 'N/A')
    job_type = job.get('job_type', 'N/A')
    
    # Generate AI-powered markdown description
    description = generate_job_description(job_title, company, skills, job_level, job_type, location)
    
    formatted_job = {
        "title": job_title,
        "company": company,
        "location": location,
        "description": description,
        "skills": skills,
        "job_level": job_level,
        "job_type": job_type,
        "job_link": job.get('job_link', "https://www.linkedin.com/jobs/search"),
        "first_seen": job.get('first_seen', datetime.now().strftime('%Y-%m-%d'))
    }
    formatted_jobs.append(formatted_job)
  
  return formatted_jobs


def search_jobs(
        query: str,
        tech_skills: list = None,
        job_level: str = None,
        limit: int = 10):
  """
  Search for jobs from MongoDB, with an AI-powered fallback.
  """
  try:
    db = get_db()
    collection = db[COLLECTION_NAME]

    mongodb_query = _build_search_query(query, tech_skills, job_level)

    projection = {
        "job_title": 1, "company": 1, "job_location": 1,
        "job_summary": 1, "job_skills": 1, "job level": 1,
        "job_type": 1, "job_link": 1, "first_seen": 1, "_id": 0,
    }
    sort = [("score", {"$meta": "textScore"})]

    cursor = collection.find(mongodb_query, projection).sort(sort).limit(limit)
    raw_jobs = list(cursor)

    if raw_jobs:
      formatted_jobs = _format_job_results(raw_jobs)
      return {
          "jobs": formatted_jobs,
          "total": len(formatted_jobs),
          "query": query,
          "ai_generated": False
      }

    logger.info(
        f"No jobs found for query '{query}'. Generating fallback jobs with AI.")
    ai_jobs = generate_enhanced_job_listings(query, tech_skills, job_level, limit)

    return {
        "jobs": ai_jobs,
        "total": len(ai_jobs),
        "query": query,
        "ai_generated": True
    }

  except Exception as e:
    logger.error(f"Error searching jobs: {str(e)}")
    return {"jobs": [], "total": 0, "error": str(e), "query": query}


def parse_skills(skills_string: str) -> list:
  """Parse skills string into a clean list."""
  if not skills_string:
    return []
  skills = re.split(r'[,;|]', skills_string)
  cleaned_skills = [skill.strip()
                    for skill in skills if skill and len(skill.strip()) > 1]
  return cleaned_skills[:10]


def generate_enhanced_job_listings(
        query: str,
        tech_skills: list = None,
        job_level: str = None,
        limit: int = 3) -> list:
  """Generate {limit} AI-powered job listings based on a query."""

  if tech_skills:
    skills_instruction = f"Array of 5-8 relevant technical skills. Must include: {tech_skills}."
    tech_skills_criteria = f"'{', '.join(tech_skills)}'"
  else:
    skills_instruction = "Generate an array of 5-8 relevant technical skills."
    tech_skills_criteria = "'Not specified (please generate)'"

  prompt = f"""Generate {limit} realistic technicaljob listings for "{query}" query.
Skills: {tech_skills_criteria}
Level: "{job_level if job_level else 'Not specified'}"

JSON array with {limit} jobs. Each job:
- title: Job title for "{query}"
- company: Tech company name
- location: City, state format
- description: Use ONLY these markdown sections: ## About Us, ## Job Summary, ## Responsibilities, ## Qualifications, ## Preferred Qualifications, ## What We Offer
- skills: {skills_instruction}
- job_level: "Entry", "Associate", "Mid-Senior", "Senior", or "Executive"
- job_type: "Remote", "Onsite", or "Hybrid"
- job_link: "https://www.linkedin.com/jobs/generated"
- first_seen: Today's date YYYY-MM-DD

Return only the JSON array."""

  try:
    logger.info(f"Generating {limit} AI job listings for query: {query}")
    response = generate_llm_response(prompt)

    start_idx = response.find('[')
    end_idx = response.rfind(']') + 1
    if start_idx != -1 and end_idx > start_idx:
      json_str = response[start_idx:end_idx]
      jobs = json.loads(json_str)
      logger.info(f"Successfully parsed {len(jobs)} jobs from AI response.")

      # Basic validation and cleanup
      cleaned_jobs = []
      for job in jobs[:limit]:
        if isinstance(job, dict):
          cleaned_job = {
              "title": job.get(
                  'title',
                  f'{query} Developer'),
              "company": job.get(
                  'company',
                  'Generated Tech Company'),
              "location": job.get(
                  'location',
                  'Remote'),
              "description": job.get(
                  'description',
                  f'## {query} Developer\n\n**Company:** Generated Tech Company\n\nAn exciting opportunity for a {query} professional.'),
              "skills": job.get(
                  'skills',
                  [query] if tech_skills is None else tech_skills),
              "job_level": job.get(
                  'job_level',
                  job_level or 'Mid-Senior'),
              "job_type": job.get(
                  'job_type',
                  'Hybrid'),
              "job_link": "https://www.linkedin.com/jobs/generated",
              "first_seen": job.get(
                  'first_seen',
                  datetime.now().strftime('%Y-%m-%d'))}
          cleaned_jobs.append(cleaned_job)
      return cleaned_jobs
  except Exception as e:
    logger.error(f"Failed to generate or parse AI response: {str(e)}")

  # Fallback to creating a single default job if AI fails
  logger.warning(
      f"AI generation failed for '{query}'. Returning a default fallback job.")
  return [{
      "title": f"Fallback: {query} position",
      "company": "Tech Company",
      "location": "Remote",
      "description": f"## {query} Position\n\n**Company:** Tech Company\n\n**Location:** Remote\n\nThis is a fallback entry because the AI service failed to generate jobs.",
      "skills": [query] if tech_skills is None else tech_skills,
      "job_level": job_level or "N/A",
      "job_type": "Hybrid",
      "job_link": "https://www.linkedin.com/jobs/generated",
      "first_seen": datetime.now().strftime('%Y-%m-%d')
  }]
