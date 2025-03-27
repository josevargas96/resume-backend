# ResumePulse: AI-Powered Resume Customization System

An intelligent system that analyzes resumes and job descriptions to generate tailored, optimized resumes for specific job applications.

## Features

- **Multi-Agent Architecture**: Leverages crewAI to orchestrate specialized agents for different aspects of resume analysis and customization
- **Resume Parsing**: Extracts structured information from resumes to identify skills, experience, education, and gaps
- **Job Description Analysis**: Analyzes job descriptions to identify key requirements and qualifications
- **Company Research**: Gathers information about company culture, values, and recent news
- **Profile Enhancement**: Generates targeted questions to improve candidate profiles
- **Resume Customization**: Creates tailored resumes optimized for specific job applications
- **Caching System**: Efficiently reuses API responses to minimize costs
- **API Interface**: Access via RESTful API for integration with other applications

## Setup Instructions

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-backend.git
cd resume-backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the environment template
cp .env.template .env

# Edit .env and add your API keys
# You'll need:
# - OpenAI API key
# - Bing Search API key (for company research)
```

### 3. Running the Application

```bash
# Start the API server
python -m src.resumepulse.main

# The API will be available at:
# http://localhost:8000/api/resume/analyze (POST)
# http://localhost:8000/api/resume/demo (GET)
```

## API Usage

### Customize a Resume

```bash
curl -X POST http://localhost:8000/api/resume/customize \
  -H "Content-Type: application/json" \
  -d @examples/resume_request.json
```

Where `resume_request.json` contains:

```json
{
  "resume_data": {
    "personal_info": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "555-123-4567",
      "location": "San Francisco, CA"
    },
    "objective": "Experienced software engineer seeking challenging role...",
    "skills": [
      {
        "category": "Programming Languages",
        "items": ["Python", "JavaScript", "Java"]
      }
    ],
    "experience": [
      {
        "company": "Tech Corp",
        "title": "Senior Developer",
        "dates": "2020-2023",
        "achievements": [
          "Led development team of 5 engineers",
          "Improved system performance by 40%"
        ]
      }
    ],
    "education": [
      {
        "institution": "University of Technology",
        "degree": "BS Computer Science",
        "dates": "2012-2016"
      }
    ]
  },
  "job_description": "We are looking for a Senior Developer with experience...",
  "company_name": "Innovation Inc."
}
```

## System Architecture

ResumePulse uses a multi-agent architecture with specialized AI agents:

1. **Resume Parser Agent**: Analyzes and extracts structured information from resumes
2. **Profile Builder Agent**: Generates questions to enhance candidate profiles
3. **Company Research Agent**: Researches company information and job requirements
4. **Resume Customizer Agent**: Creates tailored resumes based on all collected information

The system follows a sequential workflow:
1. Parse the resume to extract structured information
2. Generate profile enhancement questions
3. Analyze the company and job description
4. Create a customized resume optimized for the specific job

## Deployment

The application is designed to be deployed on Railway or similar platforms:

```bash
# Deploy to Railway
railway up
```

## Cost Optimization

The system uses several cost-optimization strategies:

1. **Intelligent Caching**: API responses are cached to avoid redundant calls
2. **GPT-4o-mini**: Uses efficient LLM to minimize token costs

## Future Enhancements

- Integration with popular job boards for automatic application
- PDF parsing and generation capabilities
- User dashboard for tracking job applications
- Feedback system to improve customization quality
- Email delivery of customized resumes
