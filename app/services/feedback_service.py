"""
Feedback service for providing feedback on interview answers.
"""
import logging
import json
from app.services.ai_service import generate_llm_response
from app.services.exceptions import ServiceError

logger = logging.getLogger(__name__)


def generate_feedback_for_answers(job: dict, qa_pairs: list):
  """
  Generates feedback on a list of questions and answers using AI.
  """
  if not job or not isinstance(job, dict):
    raise ServiceError("Invalid job object provided.", 400)

  if not qa_pairs or not isinstance(qa_pairs, list):
    raise ServiceError("Invalid questions and answers provided.", 400)

  job_title = job.get('title', 'N/A')

  try:
    # Construct the prompt for the AI
    prompt = _create_feedback_generation_prompt(job, qa_pairs)

    # Generate feedback using the AI service
    ai_response = generate_llm_response(prompt)
    if "Error:" in ai_response or "Unable to generate response" in ai_response:
      logger.error(f"AI service returned an error: {ai_response}")
      raise ServiceError("Failed to generate feedback from AI service.", 502)

    # Parse the AI response to get the feedback
    parsed_response = _parse_ai_feedback_response(ai_response)

    result = {
        "feedback": parsed_response["feedback"],
        "job_title": job_title,
    }

    return result
  except ServiceError:
    raise
  except Exception as e:
    logger.error(f"Error generating feedback for job '{job_title}': {str(e)}")
    raise ServiceError(
        "An unexpected error occurred while generating feedback.", 500)


def _create_feedback_generation_prompt(job: dict, qa_pairs: list) -> str:
  """Creates a detailed prompt for the AI to generate feedback."""

  job_title = job.get('title', 'N/A')
  job_description = job.get('description', '')
  job_skills = ", ".join(job.get('skills', []))
  num_questions = len(qa_pairs)

  questions_and_answers = ""
  for i, qa in enumerate(qa_pairs):
    questions_and_answers += f"Question {i + 1}: {qa['question']}\n"
    questions_and_answers += f"Answer {i + 1}: {qa['answer']}\n\n"

  if num_questions == 1:
    # Single question feedback
    prompt = f"""
As a highly 10x expert experienced interviewer evaluating a candidate for the role of "{job_title}", review the following interview answer in depth.

Job Overview:

    Title: {job_title}

    Summary: {job_description}

    Key Skills Required: {job_skills}

Interview Response:
{questions_and_answers}

Provide a detailed, structured critique of the candidate's response, reflecting the expectations for this role. Begin with a brief overall impression, then naturally elaborate on what the candidate did well, what was lacking, and how the answer could be improved—all embedded smoothly in a single narrative.

Focus your evaluation on relevance, clarity, technical depth, alignment with the role, and best practices in the field. Do not label sections (e.g., no "Strengths" or "Weaknesses")—just write a flowing, constructive analysis with clear reasoning and specific, actionable insights.
"""
  else:
    # 5 questions - feedback for each question + overall interview feedback
    prompt = f"""
You are a 10x expert experienced interviewer assessing a candidate for the role of "{job_title}".

Role Overview:

    Title: {job_title}

    Description: {job_description}

    Key Skills: {job_skills}

Candidate’s Responses to 5 Interview Questions:
{questions_and_answers}

Based on the full interview, write a detailed, thoughtful evaluation of the candidate's overall performance. Assess their strengths, weaknesses, and fit for the role, weaving all insights into a single, flowing narrative. Avoid listing or labeling sections—deliver clear, specific, and actionable feedback as a unified analysis.

Consider depth of experience, clarity of communication, alignment with job expectations, and industry standards. Finish with a brief, reasoned hiring recommendation embedded naturally in the summary.
"""
  
  return prompt


def _parse_ai_feedback_response(response: str) -> dict:
  """Parses the AI's plain text response - simply returns the response as feedback."""
  # try:
  #   # Clean up the response
  #   cleaned_response = response.strip() if response else "No feedback available"
    
  #   # The response is just plain text feedback, no parsing needed
  #   return {"feedback": cleaned_response}
  return {"feedback": response}
    
  # except Exception as e:
  #   logger.error(f"An unexpected error occurred while parsing AI response: {str(e)}")
  #   return {"feedback": "No feedback available"}
