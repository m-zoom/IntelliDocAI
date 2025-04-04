# models.py - Data models for the application
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentInput(BaseModel):
    """Input model for document generation"""
    topic: str = Field(description="Main topic of the document")
    subtopic: str = Field(default="", description="Subtopic or focus area within the main topic")
    key_points: List[str] = Field(default_factory=list, description="Key points to cover in the document")
    model_provider: str = Field(default="openai", description="AI model provider (openai or anthropic)")
    output_file: str = Field(default="output.pdf", description="Output PDF filename")
    enable_research: bool = Field(default=False, description="Whether to enable autonomous research")

class DocumentSection(BaseModel):
    """Model for a document section"""
    title: str = Field(description="Title of the section")
    content: str = Field(description="Content of the section")

class DocumentContent(BaseModel):
    """Model for the structured document content"""
    title: str = Field(description="Title of the document")
    introduction: str = Field(description="Introduction section of the document")
    sections: List[DocumentSection] = Field(description="Main content sections of the document")
    conclusion: str = Field(description="Conclusion section of the document")
    references: List[str] = Field(default_factory=list, description="References or sources cited")
