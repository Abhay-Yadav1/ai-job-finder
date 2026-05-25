from pydantic import BaseModel, Field # type: ignore
from typing import List

class ExtractedProfile(BaseModel):
    skills:List[str]=Field(description="List of technical and soft skills extracted from the resume.")
    experience_level: str=Field(description="E.g., Entry-level, Mid-level, Senior")
    preferred_roles: List[str] = Field(description="Job titles the candidate is suited for.")


class JobCard(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: str = Field(description="Job location or 'Remote'")
    job_type: str = Field(description="Full-time, Part-time, Internship, or Contract")
    salary: str = Field(description="Salary if mentioned, otherwise 'Not Disclosed'")
    apply_url: str = Field(description="URL to apply for the job")


class JobResults(BaseModel):
    jobs: List[JobCard] = Field(description="List of structured job postings.")