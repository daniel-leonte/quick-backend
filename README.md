<div align="center">

# QuickQ API

**AI-Powered Job Search & Interview Preparation**

</div>

A Flask-based backend for the QuickQ mobile app, providing AI-enhanced tech job searching and simulated interview preparation. This API leverages Google Cloud's Vertex AI and MongoDB to deliver intelligent job matching, personalized interview questions, and insightful feedback.

## Features

- **AI-Enhanced Job Search**: Search over 9,300 tech job postings with natural language. The API uses Vertex AI to analyze queries and return the most relevant job listings from our LinkedIn dataset.
- **Dynamic Interview Questions**: Generate tailored technical interview questions based on job roles and required tech skills from a curated collection of 200+ questions.
- **AI-Powered Feedback**: Receive AI-driven feedback on interview answers to help users improve their skills and prepare for real interviews.
- **Health Monitoring**: Endpoints for system health checks and configuration viewing.

## API Endpoints

| Method | Endpoint      | Description                               |
|--------|---------------|-------------------------------------------|
| `GET`  | `/health`     | System health check                       |
| `GET`  | `/config`     | View service configuration                |
| `GET`  | `/models`     | List available AI models                  |
| `POST` | `/jobs`       | Perform an AI-powered job search          |
| `POST` | `/questions`  | Get tailored interview questions          |
| `POST` | `/feedback`   | Get AI-powered feedback on interview answers |


### Job Search

Search for jobs using a query, technical skills and job level.

**Request:** `POST /jobs`
```json
{
  "query": "mobile developer",
  "tech_skills": ["Swift", "iOS"],
  "job_level": "Mid-Senior",
  "limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "query": "mobile developer",
  "jobs": [
    {
      "title": "iOS Mobile Developer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "We are looking for an experienced iOS developer...",
      "skills": ["Swift", "iOS", "Xcode", "REST APIs"],
      "job_level": "Mid-Senior",
      "job_type": "Hybrid"
    }
  ],
  "total": 1,
  "ai_generated": false
}
```

### Interview Questions

Get interview questions for a specific job profile.

**Request:** `POST /questions`
```json
{
  "job": {
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer to join our backend team...",
    "skills": ["Python", "Django", "PostgreSQL", "AWS"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "questions": [
      "Can you explain the difference between a deep copy and a shallow copy in Python?",
      "Describe a time you had to optimize a slow database query."
  ],
  "total": 2,
  "job_title": "Senior Python Developer",
  "tech_skills": [
      "Python",
      "Django",
      "PostgreSQL",
      "AWS"
  ]
}
```

### Interview Feedback

Get AI-powered feedback on interview answers for a specific job.

**Request:** `POST /feedback`
```json
{
  "job": {
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer to join our backend team...",
    "skills": ["Python", "Django", "PostgreSQL", "AWS"]
  },
  "questions": [
    {
      "question": "Explain the difference between a list and a tuple in Python",
      "answer": "Lists are mutable while tuples are immutable. You can change list elements but not tuple elements."
    },
    {
      "question": "How would you optimize a slow database query?",
      "answer": "I would first analyze the query execution plan, add appropriate indexes, and consider query restructuring."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "job_title": "Senior Python Developer",
  "feedback": [
    "Your answer about lists vs tuples is correct and concise. You could enhance it by mentioning performance implications and use cases for each.",
    "Good approach to database optimization. Consider also mentioning query caching, connection pooling, and database-specific optimization techniques for a more comprehensive answer."
  ]
}
```

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Application factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py            # Health & monitoring routes
│   │   ├── jobs.py              # Job search routes
│   │   ├── questions.py         # Interview questions routes
│   │   └── feedback.py          # Interview feedback routes
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py        # Vertex AI integration
│       ├── exceptions.py        # Custom exception handlers
│       ├── job_service.py       # Job search logic
│       ├── questions_service.py # Interview questions logic
│       └── feedback_service.py  # Interview feedback logic
├── main.py                      # Application entry point
├── models.py                    # Database models and connection
├── requirements.txt             # Project dependencies
├── test_api.py                  # API tests
├── Dockerfile                   # Container configuration
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Google Cloud SDK authenticated
- MongoDB Atlas account or local instance

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd quickq-api
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    _On Windows, use `venv\Scripts\activate`_

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**

    Create a `.env` file in the root directory and add the following:
    ```
    # Flask
    FLASK_APP=main.py
    FLASK_DEBUG=True
    SECRET_KEY=your-secret-key

    # MongoDB
    MONGO_URI=your-mongodb-connection-string

    # Google Cloud
    GCP_PROJECT_ID=your-gcp-project-id
    GCP_REGION=your-gcp-region
    ```

5.  **Run the application:**
    ```bash
    python main.py
    ```
    The API will be available at `http://localhost:8080`.

## Usage Examples

```bash
# Health check
curl http://localhost:8080/health

# Search for Python jobs
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer", "limit": 5}'

# Get interview questions for a backend developer
curl -X POST http://localhost:8080/questions \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "Python Developer",
      "description": "Backend development role",
      "skills": ["Python", "Django"]
    }
  }'

# Get feedback on interview answers
curl -X POST http://localhost:8080/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "Python Developer",
      "description": "Backend development role",
      "skills": ["Python", "Django"]
    },
    "questions": [
      {
        "question": "What is a decorator in Python?",
        "answer": "A decorator is a function that modifies another function"
      }
    ]
  }'
```

## Dependencies

- Flask
- pymongo
- google-cloud-aiplatform
- vertexai
- Werkzeug
- gunicorn
- requests
- python-dotenv
- pandas

## Next Steps

- [x] **Enhanced Search**: Implemented text search indexes in MongoDB for better performance.
- [x] **Interview Feedback**: Implemented the feedback endpoint with AI analysis.
- [ ] **Advanced Filtering**: Add location and other filters. Current filters include `job_level` and `tech_skills`.
- [ ] **Semantic Search**: Improve ranking algorithms for jobs and questions.
- [ ] **User Profiles**: Add user preferences and personalized recommendations.
- [ ] **Analytics**: Add question tracking and performance analytics.
- [ ] **Containerization**: Full Docker and Kubernetes support for deployment. 