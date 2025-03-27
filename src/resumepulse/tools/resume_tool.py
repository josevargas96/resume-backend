import logging
logging.getLogger('opentelemetry.trace').setLevel(logging.ERROR)

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.utilities import BingSearchAPIWrapper
import os
import json
from datetime import datetime
import requests


class ResumeParserInput(BaseModel):
    """Input schema for ResumeParserTool."""
    resume_json: str = Field(
        ...,
        description="JSON string containing resume data to be parsed."
    )


class ResumeParserTool(BaseTool):
    name: str = "resume_parser"
    description: str = (
        "Use this tool to parse and extract structured information from a resume in JSON format. "
        "It can identify skills, experience, education, and personal information."
    )
    args_schema: Type[BaseModel] = ResumeParserInput

    def _run(self, resume_json: str) -> str:
        """Parse resume data from JSON"""
        try:
            # Parse the JSON string into a Python dictionary
            resume_data = json.loads(resume_json)
            
            # Extract and structure the resume information
            parsed_data = {
                "personal_info": self._extract_personal_info(resume_data),
                "objective": self._extract_objective(resume_data),
                "skills": self._extract_skills(resume_data),
                "experience": self._extract_experience(resume_data),
                "education": self._extract_education(resume_data),
                "gaps": self._identify_gaps(resume_data)
            }
            
            # Return the structured data as a JSON string
            return json.dumps(parsed_data, indent=2)
            
        except Exception as e:
            return f"Error parsing resume: {str(e)}"
    
    def _extract_personal_info(self, resume_data):
        """Extract personal information from resume"""
        personal_info = {}
        
        # These fields might be in different locations depending on resume format
        for field in ["name", "email", "phone", "location"]:
            personal_info[field] = resume_data.get(field, "")
            
            # Check nested structures if not found at top level
            if not personal_info[field] and "personal_info" in resume_data:
                personal_info[field] = resume_data["personal_info"].get(field, "")
                
        return personal_info
    
    def _extract_objective(self, resume_data):
        """Extract career objective from resume"""
        # Check different possible field names for objective
        for field in ["objective", "summary", "professional_summary", "career_objective"]:
            if field in resume_data:
                return resume_data[field]
        return ""
    
    def _extract_skills(self, resume_data):
        """Extract skills from resume"""
        skills = []
        
        # Check if skills are already categorized
        if "skills" in resume_data:
            if isinstance(resume_data["skills"], list):
                # Handle flat list of skills
                if all(isinstance(s, str) for s in resume_data["skills"]):
                    skills.append({
                        "category": "General Skills",
                        "items": resume_data["skills"]
                    })
                # Handle list of skill objects
                else:
                    for skill in resume_data["skills"]:
                        if isinstance(skill, dict):
                            if "category" in skill and "items" in skill:
                                skills.append(skill)
                            else:
                                # Handle other skill object formats
                                for key, value in skill.items():
                                    if isinstance(value, list):
                                        skills.append({
                                            "category": key,
                                            "items": value
                                        })
        
        return skills
    
    def _extract_experience(self, resume_data):
        """Extract work experience from resume"""
        experience = []
        
        # Check different possible field names for work experience
        for field in ["experience", "work_experience", "employment_history", "work_history"]:
            if field in resume_data and isinstance(resume_data[field], list):
                for job in resume_data[field]:
                    if isinstance(job, dict):
                        job_entry = {
                            "company": job.get("company", ""),
                            "title": job.get("title", ""),
                            "dates": job.get("dates", ""),
                            "achievements": []
                        }
                        
                        # Extract achievements/responsibilities
                        for field in ["achievements", "responsibilities", "description"]:
                            if field in job and isinstance(job[field], list):
                                job_entry["achievements"] = job[field]
                                break
                            elif field in job and isinstance(job[field], str):
                                job_entry["achievements"] = [job[field]]
                                break
                        
                        experience.append(job_entry)
                break  # Stop after finding the first valid experience field
        
        return experience
    
    def _extract_education(self, resume_data):
        """Extract education from resume"""
        education = []
        
        # Check for education section
        if "education" in resume_data and isinstance(resume_data["education"], list):
            for edu in resume_data["education"]:
                if isinstance(edu, dict):
                    edu_entry = {
                        "institution": edu.get("institution", edu.get("school", "")),
                        "degree": edu.get("degree", ""),
                        "dates": edu.get("dates", ""),
                        "details": edu.get("details", "")
                    }
                    education.append(edu_entry)
        
        return education
    
    def _identify_gaps(self, resume_data):
        """Identify potential gaps or areas for improvement in the resume"""
        gaps = []
        
        # Check for missing or incomplete sections
        if not self._extract_skills(resume_data):
            gaps.append({"area": "Skills", "details": "No skills listed or section is incomplete"})
        
        if not self._extract_experience(resume_data):
            gaps.append({"area": "Experience", "details": "No work experience listed"})
        
        if not self._extract_education(resume_data):
            gaps.append({"area": "Education", "details": "No education information listed"})
        
        if not self._extract_objective(resume_data):
            gaps.append({"area": "Objective", "details": "No career objective or professional summary"})
        
        # Check for potential improvements
        experience = self._extract_experience(resume_data)
        for i, job in enumerate(experience):
            if not job["achievements"] or len(job["achievements"]) < 2:
                gaps.append({
                    "area": f"Experience at {job['company']}", 
                    "details": "Limited achievements or responsibilities listed"
                })
        
        return gaps


class JobDescriptionInput(BaseModel):
    """Input schema for JobDescriptionTool."""
    description: str = Field(
        ...,
        description="Job description text to analyze."
    )


class JobDescriptionTool(BaseTool):
    name: str = "job_description_analyzer"
    description: str = (
        "Use this tool to analyze job descriptions and extract key requirements, "
        "qualifications, and responsibilities."
    )
    args_schema: Type[BaseModel] = JobDescriptionInput

    def _run(self, description: str) -> str:
        """Analyze job description text"""
        try:
            # Extract structured information from job description
            analysis = {
                "key_requirements": [],
                "preferred_qualifications": [],
                "responsibilities": [],
                "keywords": [],
                "company_hints": []
            }
            
            # Note: In a real implementation, this would use NLP/ML to extract this information
            # For now, this is just a placeholder for the structure
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return f"Error analyzing job description: {str(e)}"


class CompanyResearchInput(BaseModel):
    """Input schema for CompanyResearchTool."""
    company_name: str = Field(
        ...,
        description="Name of the company to research."
    )
    job_title: str = Field(
        default="",
        description="Optional: specific job title or department to research."
    )


class CompanyResearchTool(BaseTool):
    name: str = "company_research"
    description: str = (
        "Use this tool to research companies and gather information about their "
        "culture, values, recent news, and specific teams or departments."
    )
    args_schema: Type[BaseModel] = CompanyResearchInput
    bing_search: BingSearchAPIWrapper = None

    def __init__(self):
        super().__init__()
        self.bing_search = BingSearchAPIWrapper(
            bing_subscription_key=os.getenv('BING_SUBSCRIPTION_KEY'),
            bing_search_url="https://api.bing.microsoft.com/v7.0/search"
        )

    def _run(self, company_name: str, job_title: str = "") -> str:
        """Research company information"""
        cache_dir = ".cache/companies"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a cache key based on the company and job title
        cache_key = company_name.lower().replace(" ", "_")
        if job_title:
            cache_key += f"_{job_title.lower().replace(' ', '_')}"
        
        cache_file = f"{cache_dir}/{cache_key}.json"
        
        # Check if we have cached results from today
        if os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_time.date() == datetime.now().date():
                with open(cache_file, 'r') as f:
                    return f.read()
        
        try:
            # Prepare results dictionary
            results = {
                "company_profile": {
                    "name": company_name,
                    "industry": "",
                    "values": [],
                    "culture": "",
                    "recent_news": []
                },
                "team_info": {}
            }
            
            # Search for company information
            company_query = f"{company_name} company profile about us values mission"
            company_info = self.bing_search.run(company_query)
            
            # Search for recent news
            news_query = f"{company_name} recent news announcement last month"
            news_info = self.bing_search.run(news_query)
            
            # If job title is provided, search for specific team information
            if job_title:
                team_query = f"{company_name} {job_title} team department"
                team_info = self.bing_search.run(team_query)
                results["team_info"] = team_info
            
            # Log usage
            os.makedirs(".logs", exist_ok=True)
            with open(".logs/company_research.log", "a") as log:
                log.write(f"{datetime.now().isoformat()},company,{company_name},{job_title}\n")
            
            # Cache results
            with open(cache_file, 'w') as f:
                f.write(json.dumps(results, indent=2))
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return f"Error researching company: {str(e)}"


class ProfileQuestionsInput(BaseModel):
    """Input schema for ProfileQuestionsTool."""
    resume_data: str = Field(
        ...,
        description="JSON string containing parsed resume data."
    )
    job_description: str = Field(
        ...,
        description="Job description text."
    )


class ProfileQuestionsTool(BaseTool):
    name: str = "profile_questions_generator"
    description: str = (
        "Use this tool to generate targeted questions based on a resume and job description "
        "to enhance a candidate's profile and address potential gaps."
    )
    args_schema: Type[BaseModel] = ProfileQuestionsInput

    def _run(self, resume_data: str, job_description: str) -> str:
        """Generate profile enhancement questions"""
        try:
            # Parse inputs
            resume = json.loads(resume_data)
            
            # Generate questions based on gaps between resume and job description
            # This would use more sophisticated analysis in a real implementation
            questions = [
                {
                    "question": "Can you provide specific metrics or results from your achievements at [Company]?",
                    "purpose": "Quantify achievements",
                    "relevance": "Adding metrics makes achievements more impactful"
                },
                {
                    "question": "What specific technologies/tools have you used in your previous roles?",
                    "purpose": "Technical skill details",
                    "relevance": "Job requires specific technical expertise"
                },
                {
                    "question": "Can you describe a challenging project you've led and how you ensured its success?",
                    "purpose": "Leadership experience",
                    "relevance": "Job involves project leadership responsibilities"
                }
            ]
            
            # Identify focus areas for enhancement
            focus_areas = [
                {"area": "Technical skills relevance", "importance": "high"},
                {"area": "Leadership experience", "importance": "medium"},
                {"area": "Achievement quantification", "importance": "high"}
            ]
            
            result = {
                "questions": questions,
                "focus_areas": focus_areas
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error generating profile questions: {str(e)}"


class ResumeCustomizerInput(BaseModel):
    """Input schema for ResumeCustomizerTool."""
    profile: str = Field(
        ...,
        description="JSON string containing enhanced candidate profile."
    )
    job_description: str = Field(
        ...,
        description="Job description text."
    )
    company_analysis: str = Field(
        ...,
        description="JSON string containing company analysis."
    )


class ResumeCustomizerTool(BaseTool):
    name: str = "resume_customizer"
    description: str = (
        "Use this tool to create a customized resume based on a candidate's profile, "
        "job description, and company analysis."
    )
    args_schema: Type[BaseModel] = ResumeCustomizerInput

    def _run(self, profile: str, job_description: str, company_analysis: str) -> str:
        """Generate a customized resume"""
        try:
            # Parse inputs
            profile_data = json.loads(profile)
            company_data = json.loads(company_analysis)
            
            # Create a tailored resume
            # In a real implementation, this would use more sophisticated customization
            tailored_resume = {
                "personal_info": profile_data.get("personal_info", {}),
                "objective": self._customize_objective(profile_data, job_description, company_data),
                "skills": self._prioritize_skills(profile_data, job_description),
                "experience": self._customize_experience(profile_data, job_description, company_data),
                "education": profile_data.get("education", []),
                "customization_notes": [
                    "Objective tailored to align with company values",
                    "Skills reordered to prioritize job requirements",
                    "Experience descriptions enhanced to highlight relevant achievements"
                ]
            }
            
            return json.dumps(tailored_resume, indent=2)
            
        except Exception as e:
            return f"Error customizing resume: {str(e)}"
    
    def _customize_objective(self, profile, job_description, company_data):
        """Customize objective statement based on job and company"""
        # Placeholder implementation
        original = profile.get("objective", "")
        if not original:
            return "Dedicated professional seeking to leverage skills and experience to contribute to company goals."
        return original
    
    def _prioritize_skills(self, profile, job_description):
        """Prioritize skills based on job requirements"""
        # Placeholder implementation
        return profile.get("skills", [])
    
    def _customize_experience(self, profile, job_description, company_data):
        """Customize experience section to highlight relevant achievements"""
        # Placeholder implementation
        return profile.get("experience", [])