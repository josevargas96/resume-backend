from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.resume_tool import (
    ResumeParserTool, 
    JobDescriptionTool, 
    CompanyResearchTool, 
    ProfileQuestionsTool,
    ResumeCustomizerTool
)
from dotenv import load_dotenv

@CrewBase
class ResumeCustomizationCrew:
    """Resume customization crew for tailoring resumes to specific job descriptions"""

    def __init__(self):
        load_dotenv()
        self.resume_parser_tool = ResumeParserTool()
        self.job_description_tool = JobDescriptionTool()
        self.company_research_tool = CompanyResearchTool()
        self.profile_questions_tool = ProfileQuestionsTool()
        self.resume_customizer_tool = ResumeCustomizerTool()

    @agent
    def resume_parser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_parser_agent'],
            tools=[self.resume_parser_tool],
            llm_config={"temperature": 0.2, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def profile_builder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['profile_builder_agent'],
            tools=[self.profile_questions_tool],
            llm_config={"temperature": 0.7, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def company_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['company_research_agent'],
            tools=[self.job_description_tool, self.company_research_tool],
            llm_config={"temperature": 0.3, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def resume_customizer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_customizer_agent'],
            tools=[self.resume_customizer_tool],
            llm_config={"temperature": 0.5, "model": "gpt-4o-mini"},
            verbose=True
        )

    @task
    def parse_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['parse_resume_task']
        )

    @task
    def generate_profile_questions_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_profile_questions_task']
        )

    @task
    def analyze_company_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_company_task']
        )

    @task
    def generate_tailored_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_tailored_resume_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )