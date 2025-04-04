# document_generator.py - Generate structured document content
import logging
from typing import List, Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

from models import DocumentInput, DocumentContent, DocumentSection

class DocumentGenerator:
    """Generates structured document content using LLMs"""
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
    
    def generate_document_content(self, doc_input: DocumentInput, agent_content: str) -> DocumentContent:
        """Generate structured document content from agent output"""
        logging.info("Structuring document content...")
        
        # Parse the agent content into structured format
        parser = PydanticOutputParser(pydantic_object=DocumentContent)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document structuring assistant. Your task is to take content
            about a topic and structure it into a formal document with proper sections.
            
            The output should follow this structure:
            1. Title - A clear, descriptive title for the document
            2. Introduction - A brief introduction to the topic
            3. Sections - Multiple sections covering different aspects of the topic
            4. Conclusion - A summary of the key points
            5. References - List of sources (if applicable)
            
            Format the output as a valid JSON object matching the DocumentContent schema.
            """),
            ("human", """
            Please structure the following content into a formal document:
            
            Topic: {topic}
            Subtopic: {subtopic}
            
            Content:
            {content}
            
            {format_instructions}
            """)
        ])
        
        # Get format instructions from parser
        format_instructions = parser.get_format_instructions()
        
        # Fill the prompt template
        formatted_prompt = prompt.format_messages(
            topic=doc_input.topic,
            subtopic=doc_input.subtopic,
            content=agent_content,
            format_instructions=format_instructions
        )
        
        # Invoke the LLM
        response = self.llm.invoke(formatted_prompt)
        response_text = response.content
        
        try:
            # Parse the response to get structured content
            doc_content = parser.parse(response_text)
            return doc_content
        except Exception as e:
            logging.error(f"Error parsing structured document content: {str(e)}")
            # Fallback to manual creation of document content if parsing fails
            return self._create_fallback_document(doc_input, agent_content)
    
    def _create_fallback_document(self, doc_input: DocumentInput, agent_content: str) -> DocumentContent:
        """Create a fallback document structure if parsing fails"""
        logging.info("Using fallback document structure...")
        
        # Extract sections based on common headings
        sections = []
        current_section = None
        current_content = []
        
        lines = agent_content.split('\n')
        for line in lines:
            line = line.strip()
            # Check if line looks like a heading (simple heuristic)
            if line and (line.startswith('#') or (len(line) < 60 and line.upper() == line)):
                # Save previous section if it exists
                if current_section and current_content:
                    sections.append(DocumentSection(
                        title=current_section,
                        content='\n'.join(current_content)
                    ))
                    current_content = []
                current_section = line.lstrip('#').strip()
            elif current_section and line:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections.append(DocumentSection(
                title=current_section,
                content='\n'.join(current_content)
            ))
        
        # Create fallback document content
        title = f"{doc_input.topic}: {doc_input.subtopic}" if doc_input.subtopic else doc_input.topic
        
        # Extract introduction and conclusion if possible
        introduction = ""
        conclusion = ""
        references = []
        
        for section in sections:
            if "introduction" in section.title.lower():
                introduction = section.content
                sections.remove(section)
            elif "conclusion" in section.title.lower():
                conclusion = section.content
                sections.remove(section)
            elif "reference" in section.title.lower() or "bibliography" in section.title.lower():
                references = [line.strip() for line in section.content.split('\n') if line.strip()]
                sections.remove(section)
        
        # If no explicit introduction was found, use the first paragraph as introduction
        if not introduction and agent_content:
            paragraphs = agent_content.split('\n\n')
            if paragraphs:
                introduction = paragraphs[0]
        
        return DocumentContent(
            title=title,
            introduction=introduction,
            sections=sections,
            conclusion=conclusion,
            references=references
        )
