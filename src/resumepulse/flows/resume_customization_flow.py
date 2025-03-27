# src/resumepulse/flows/resume_customization_flow.py

from crewai.flow.flow import Flow, listen, start, FlowState
from crewai import Agent, Crew, Process
from pydantic import BaseModel
from typing import Dict, Any, Optional, AsyncGenerator, List
import json
import asyncio
import logging
import re
from ..clean_json import clean_and_parse_json
from ..crew import ResumeCustomizationCrew
from ..utils.stream_utils import create_stream_event, process_task_result

class ResumeCustomizationState(FlowState):
    resume_data: Dict[str, Any]
    job_description: str
    company_name: str
    parsed_resume: Optional[Dict[str, Any]] = None
    profile_questions: Optional[Dict[str, Any]] = None
    company_analysis: Optional[Dict[str, Any]] = None
    enhanced_profile: Optional[Dict[str, Any]] = None
    customized_resume: Optional[Dict[str, Any]] = None

class ResumeCustomizationFlow(Flow[ResumeCustomizationState]):
    def __init__(self, resume_data: Dict[str, Any], job_description: str, company_name: str):
        self.initial_state = ResumeCustomizationState(
            resume_data=resume_data,
            job_description=job_description,
            company_name=company_name
        )
        super().__init__()
        self._initialize_crew()

    def _initialize_crew(self):
        """Initialize crew instance with separate crews for each task"""
        self.crew_instance = ResumeCustomizationCrew()
        
        self.resume_parser_crew = Crew(
            agents=[self.crew_instance.resume_parser_agent()],
            tasks=[self.crew_instance.parse_resume_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.profile_builder_crew = Crew(
            agents=[self.crew_instance.profile_builder_agent()],
            tasks=[self.crew_instance.generate_profile_questions_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.company_research_crew = Crew(
            agents=[self.crew_instance.company_research_agent()],
            tasks=[self.crew_instance.analyze_company_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.resume_customizer_crew = Crew(
            agents=[self.crew_instance.resume_customizer_agent()],
            tasks=[self.crew_instance.generate_tailored_resume_task()],
            process=Process.sequential,
            verbose=True
        )

    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """Extract and clean JSON from agent response"""
        try:
            # First try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                # Find content between first { and last }
                start_idx = text.find('{')
                end_idx = text.rfind('}')
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = text[start_idx:end_idx + 1]
                    # Remove escaped quotes that might be causing issues
                    json_str = re.sub(r'\\+"', '"', json_str)
                    return json.loads(json_str)
            except Exception:
                try:
                    # Last resort: try clean_and_parse_json
                    return clean_and_parse_json(text)
                except Exception as e:
                    logging.error(f"Failed to parse JSON: {str(e)}\nRaw text: {text[:200]}...")
                    return None

    def _format_resume_for_task(self) -> str:
        """Format resume data for task input"""
        return json.dumps(self.state.resume_data)
    
    def _format_enhanced_profile(self, parsed_resume: Dict[str, Any], answers: Dict[str, str]) -> Dict[str, Any]:
        """Enhance the parsed resume with additional information from answers"""
        # Start with the parsed resume
        enhanced = parsed_resume.copy()
        
        # Add or enhance sections based on answers
        # This would be more sophisticated in a real implementation
        if "additional_achievements" in answers:
            # Add achievements to existing experience entries
            if "experience" in enhanced and enhanced["experience"]:
                for exp in enhanced["experience"]:
                    if "achievements" in exp:
                        exp["achievements"].append(answers["additional_achievements"])
        
        # Add any new skills mentioned
        if "additional_skills" in answers and "skills" in enhanced:
            new_skills = answers["additional_skills"].split(",")
            for skill_group in enhanced["skills"]:
                if skill_group["category"] == "General Skills":
                    skill_group["items"].extend([s.strip() for s in new_skills])
        
        return enhanced

    @start()
    async def parse_resume(self):
        """Start the process by parsing the resume"""
        try:
            result = self.resume_parser_crew.kickoff(inputs={
                "resume_json": self._format_resume_for_task()
            })
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.parsed_resume = data
                    return data
        except Exception as e:
            logging.error(f"Error in parse_resume: {str(e)}")
        return None

    @listen(parse_resume)
    async def generate_profile_questions(self, parsed_resume_result):
        """Generate questions to enhance the candidate's profile"""
        try:
            result = self.profile_builder_crew.kickoff(inputs={
                "resume_data": json.dumps(self.state.parsed_resume),
                "job_description": self.state.job_description
            })
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.profile_questions = data
                    return data
        except Exception as e:
            logging.error(f"Error in generate_profile_questions: {str(e)}")
        return None

    @listen(parse_resume)
    async def analyze_company(self, parsed_resume_result):
        """Analyze the company and job description"""
        try:
            result = self.company_research_crew.kickoff(inputs={
                "company_name": self.state.company_name,
                "job_description": self.state.job_description
            })
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.company_analysis = data
                    return data
        except Exception as e:
            logging.error(f"Error in analyze_company: {str(e)}")
        return None

    @listen(generate_profile_questions, analyze_company)
    async def create_customized_resume(self, profile_questions_result, company_analysis_result):
        """Create a customized resume based on all collected information"""
        try:
            # For this demo, we'll simulate a user answering the questions
            # In a real application, this would wait for actual user input
            simulated_answers = {
                "additional_achievements": "Led cross-functional team that increased conversion rates by 25%",
                "additional_skills": "Project management, stakeholder communication, agile methodologies"
            }
            
            # Enhance the profile with answers
            enhanced_profile = self._format_enhanced_profile(
                self.state.parsed_resume, simulated_answers
            )
            self.state.enhanced_profile = enhanced_profile
            
            # Generate the customized resume
            result = self.resume_customizer_crew.kickoff(inputs={
                "profile": json.dumps(enhanced_profile),
                "job_description": self.state.job_description,
                "company_analysis": json.dumps(self.state.company_analysis)
            })
            
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.customized_resume = data
                    return data
        except Exception as e:
            logging.error(f"Error in create_customized_resume: {str(e)}")
        return None

    async def stream_process(self) -> AsyncGenerator[str, None]:
        """Stream the resume customization process"""
        try:
            yield await create_stream_event("status", "Starting resume parsing...")
            await asyncio.sleep(0.1)

            parsed_resume = await self.parse_resume()
            if parsed_resume:
                yield await create_stream_event("task_complete", task="parsed_resume", data=parsed_resume)
                yield await create_stream_event("status", "Generating profile enhancement questions...")
                
                # Start company analysis in parallel
                company_task = asyncio.create_task(self.analyze_company(parsed_resume))
                
                profile_questions = await self.generate_profile_questions(parsed_resume)
                if profile_questions:
                    yield await create_stream_event("task_complete", task="profile_questions", data=profile_questions)
                    yield await create_stream_event("status", "Analyzing company and job description...")
                    
                    # Wait for company analysis to complete
                    company_analysis = await company_task
                    if company_analysis:
                        yield await create_stream_event("task_complete", task="company_analysis", data=company_analysis)
                        yield await create_stream_event("status", "Creating customized resume...")
                        
                        # In a real application, we would wait for user answers here
                        # For demo purposes, we're simulating user responses
                        yield await create_stream_event("status", "Simulating user responses to profile questions...")
                        await asyncio.sleep(1)  # Simulate waiting for responses
                        
                        customized_resume = await self.create_customized_resume(profile_questions, company_analysis)
                        if customized_resume:
                            yield await create_stream_event("task_complete", task="customized_resume", data=customized_resume)
                            yield await create_stream_event("complete", "Resume customization complete")
                        else:
                            yield await create_stream_event("error", "Failed to create customized resume")
                    else:
                        yield await create_stream_event("error", "Failed to analyze company and job description")
                else:
                    yield await create_stream_event("error", "Failed to generate profile questions")
            else:
                yield await create_stream_event("error", "Failed to parse resume")
                    
        except Exception as e:
            logging.error(f"Error in stream_process: {str(e)}")
            yield await create_stream_event("error", f"Error during processing: {str(e)}")