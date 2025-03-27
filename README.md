# ResumePulse

An automated system that helps tailor resumes to specific job descriptions and companies using AI-powered analysis and customization.

## Features

- **Multi-Agent Architecture**: Leverages crewAI to orchestrate specialized agents for different aspects of resume customization
- **Resume Parsing**: Automatically extracts structured information from resumes
- **Job Description Analysis**: Identifies key requirements and qualifications from job postings
- **Company Research**: Gathers information about company culture, values, and expectations
- **Profile Enhancement**: Generates targeted questions to help fill gaps in experience and qualifications
- **Resume Customization**: Creates tailored resumes optimized for specific job applications
- **API & CLI Interfaces**: Access via RESTful API or command line

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

#### Via CLI:

```bash
# Run a one-time resume customization
python -m src.resumepulse.cli --resume examples/resume.json --job-description examples/job_description.txt --company "Example Corp"
```

#### As a Web Service:

```bash
# Start the API server
python app.py

# The API will be available at:
# http://localhost:8000/api/resume/analyze (POST)
# http://localhost:8000/api/resume/demo (GET)
```

## API Usage

### Customize Resume

```bash
curl -X POST http://localhost:8000/api/resume/customize \
  -H "Content-Type: application/json" \
  -d @examples/request.json
```

Where `request.json` contains:

```json
{
  "resume": {
    "personal_info": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "555-123-4567",
      "location": "San Francisco, CA"
    },
    "objective": "Experienced software engineer seeking challenging roles in AI development",
    "experience": [
      {
        "company": "Tech Solutions Inc.",
        "title": "Senior Developer",
        "dates": "2018-2023",
        "achievements": [
          "Led team of 5 developers on major client project",
          "Increased system performance by 35% through code optimization"
        ]
      }
    ],
    "education": [
      {
        "institution": "University of California",
        "degree": "B.S. Computer Science",
        "dates": "2014-2018"
      }
    ],
    "skills": [
      {
        "category": "Programming Languages",
        "items": ["Python", "JavaScript", "Java"]
      },
      {
        "category": "Frameworks",
        "items": ["React", "Django", "TensorFlow"]
      }
    ]
  },
  "job_description": "Looking for a skilled Python developer with experience in AI/ML frameworks...",
  "company_name": "AI Innovations Ltd."
}
```

## Deployment

The application is designed to be deployed on Railway or similar platforms:

```bash
# Deploy to Railway
railway up
```

## Future Enhancements

- Integration with applicant tracking systems
- PDF resume parsing
- Cover letter generation
- Interview preparation assistance
- Resume version management and tracking
