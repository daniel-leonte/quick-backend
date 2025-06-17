"""
Questions search service for retrieving and processing software interview questions.
"""
import os
import logging
import re
import json
from models import get_db
from app.services.ai_service import generate_llm_response
from app.services.exceptions import ServiceError

logger = logging.getLogger(__name__)

# Database configuration
QUESTIONS_DATABASE_NAME = 'software_questions_db'
QUESTIONS_COLLECTION_NAME = 'questions'


def search_questions(query: str, tech_skills: list = None, limit: int = 10):
  """
  Search for interview questions using a text search in MongoDB.

  NOTE: This function requires a text index on the 'questions' collection.
  Example: db.questions.createIndex({ "Question": "text", "Answer": "text", "Category": "text" })
  """
  try:
    db = get_db(QUESTIONS_DATABASE_NAME)
    collection = db[QUESTIONS_COLLECTION_NAME]

    search_phrase = query
    if tech_skills:
      search_phrase += " " + " ".join(tech_skills)

    mongodb_query = {'$text': {'$search': search_phrase}}
    projection = {'score': {'$meta': 'textScore'}}
    sort = [('score', {'$meta': 'textScore'})]

    cursor = collection.find(mongodb_query, projection).sort(sort).limit(limit)
    raw_questions = list(cursor)

    if not raw_questions:
      return {
          "questions": [],
          "total": 0,
          "message": f"No questions found for query: '{query}'"
      }

    questions = [
        {
            "question_number": q.get('Question Number', 'N/A'),
            "question": q.get('Question', 'N/A'),
            "answer": q.get('Answer', 'N/A'),
            "category": q.get('Category', 'N/A'),
            "difficulty": q.get('Difficulty', 'N/A')
        } for q in raw_questions
    ]

    logger.info(
        f"Found {len(questions)} questions from database for query: '{query}'")

    return {
        "questions": questions,
        "total": len(questions)
    }

  except Exception as e:
    logger.error(f"Error searching questions for query '{query}': {str(e)}")
    raise ServiceError("An error occurred while searching for questions.", 500)


def parse_tech_skills(skills_list: list) -> list:
  """Parse and validate tech skills list."""
  if not skills_list:
    return []

  cleaned_skills = [
      skill.strip() for skill in skills_list
      if isinstance(skill, str) and skill.strip() and len(skill.strip()) > 1
  ]

  return cleaned_skills[:10]


def generate_interview_questions(job: dict):
  """
  Generates interview questions based on a job profile using AI.
  """
  if not job or not isinstance(job, dict):
    raise ServiceError("Invalid job object provided.", 400)

  job_title = job.get('title', 'N/A')
  job_description = job.get('description', '')
  tech_skills = parse_tech_skills(job.get('skills', []))

  try:
    # Find relevant questions from the database to use as context
    search_terms = [job_title] + tech_skills
    search_query = ' '.join(filter(None, search_terms))

    db_questions = search_questions(
        search_query, tech_skills, limit=5).get(
        'questions', [])

    # Construct the prompt for the AI
    prompt = _create_question_generation_prompt(
        job_title, job_description, tech_skills, db_questions)

    # Generate questions using the AI service
    ai_response = generate_llm_response(prompt)
    if "Error:" in ai_response or "Unable to generate response" in ai_response:
      logger.error(f"AI service returned an error: {ai_response}")
      raise ServiceError("Failed to generate questions from AI service.", 502)

    # Parse the AI response to get the questions
    questions = _parse_ai_question_response(ai_response)

    return {
        "questions": questions,
        "total": len(questions),
        "job_title": job_title,
        "tech_skills": tech_skills
    }
  except ServiceError:
    raise
  except Exception as e:
    logger.error(
        f"Error generating interview questions for job '{job_title}': {str(e)}")
    raise ServiceError(
        "An unexpected error occurred while generating questions.", 500)


def _create_question_generation_prompt(
        job_title: str,
        job_description: str,
        tech_skills: list,
        context_questions: list) -> str:
  """Creates a detailed prompt for the AI to generate interview questions."""
  context_prompt = ""
  if context_questions:
    context_prompt = "For context, here are some existing questions and answers that might be relevant. Use them to understand the style, format, and difficulty, but generate NEW and UNIQUE questions:\n"
    for q in context_questions:
      context_prompt += f"- Question: {q['question']}\n- Answer: {q['answer']}\n\n"

  prompt = f"""
Based on the following job profile, please generate exactly 5 high-quality technical interview questions.
The questions should be suitable for a candidate applying for the role of "{job_title}".

**Job Details:**
- **Title:** {job_title}
- **Description:** {job_description}
- **Key Skills:** {', '.join(tech_skills)}

{context_prompt}

**Instructions:**
1.  Generate **exactly 5** technical questions.
2.  The questions must be directly relevant to the job's key skills and description.
3.  Return **ONLY** a valid JSON array of strings, where each string is a question.
4.  **DO NOT** include answers, numbering, or any other text outside of the JSON array.

Example format:
[
    "Can you explain the difference between a deep copy and a shallow copy in Python?",
    "Describe a time you had to optimize a slow database query."
]
"""
  return prompt


def _parse_ai_question_response(response: str) -> list:
  """Parses the AI's JSON response to extract a list of questions."""
  try:
    # Clean the response to ensure it's valid JSON
    start_index = response.find('[')
    end_index = response.rfind(']') + 1
    if start_index == -1 or end_index == 0:
      logger.warning(
          f"Could not find a JSON array in the AI response: {response}")
      # Fallback for non-JSON plain text lists
      return [line.strip() for line in response.split(
          '\n') if line.strip() and not line.startswith("```")]

    json_str = response[start_index:end_index]
    try:
      questions = json.loads(json_str)

      if isinstance(questions, list) and all(isinstance(q, str)
                                             for q in questions):
        return questions
      else:
        logger.warning(f"Parsed JSON is not a list of strings: {questions}")
        return []
    except json.JSONDecodeError:
      logger.error(f"Failed to decode JSON from AI response: {json_str}")
      # Fallback for non-JSON plain text lists
      return [line.strip() for line in response.split(
          '\n') if line.strip() and not line.startswith("```")]

  except Exception as e:
    logger.error(
        f"An unexpected error occurred while parsing AI response: {str(e)}")
    return []
