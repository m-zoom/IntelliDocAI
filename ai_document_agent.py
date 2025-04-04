# ai_document_agent.py - Core AI agent for document generation
import os
import logging
from typing import List, Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_core.tools import Tool

from models import DocumentInput, DocumentContent, DocumentSection
from document_generator import DocumentGenerator
from pdf_generator import PDFGenerator
from tools.search_tool import SearchTool
from tools.wiki_tool import WikiTool
from tools.save_tool import SaveTool

class AIDocumentAgent:
    """AI agent for generating well-structured documents"""
    
    def __init__(self, doc_input: DocumentInput):
        self.doc_input = doc_input
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.agent = self._create_agent()
        self.doc_generator = DocumentGenerator(self.llm)
    
    def _initialize_llm(self):
        """Initialize the LLM based on user selection"""
        if self.doc_input.model_provider == "openai":
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            return ChatOpenAI(
                model="gpt-4o",
                temperature=0.7,
                api_key=os.environ.get("OPENAI_API_KEY")
            )
        elif self.doc_input.model_provider == "anthropic":
            # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
            # do not change this unless explicitly requested by the user
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.7,
                anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.doc_input.model_provider}")
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize the tools for the agent"""
        tools = []
        
        if self.doc_input.enable_research:
            tools.extend([
                SearchTool().get_tool(),
                WikiTool().get_tool(),
            ])
        
        # Always include save tool
        tools.append(SaveTool().get_tool())
        
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent"""
        if self.doc_input.enable_research:
            # Create a research-capable agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an intelligent document creation assistant that helps users create 
                well-structured documents on various topics. When given a topic, subtopic, and key points,
                you'll research the topic and create detailed, factual content with proper citations.
                
                Follow these guidelines:
                1. When researching, be thorough but focus on reliable sources
                2. Create well-structured content with clear sections
                3. Ensure all information is accurate and properly cited
                4. Organize the content logically based on the key points provided
                5. Use the search and wiki tools to gather information when needed
                6. Use the save tool to save your final document content
                
                Your final output should be comprehensive, well-organized, and focused on the topic and subtopics.
                """),
                ("user", "{input}"),
                ("agent_scratchpad", "{agent_scratchpad}")
            ])
            
            if self.doc_input.model_provider == "openai":
                agent = create_openai_functions_agent(self.llm, self.tools, prompt)
            else:
                agent = create_react_agent(self.llm, self.tools, prompt)
                
            return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        else:
            # Create a simpler agent without research capabilities
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an intelligent document creation assistant that helps users create 
                well-structured documents on various topics. When given a topic, subtopic, and key points,
                you'll create detailed content based on your knowledge.
                
                Follow these guidelines:
                1. Create well-structured content with clear sections
                2. Organize the content logically based on the key points provided
                3. Ensure the content is comprehensive and informative
                4. Use the save tool to save your final document content
                
                Your final output should be comprehensive, well-organized, and focused on the topic and subtopics.
                """),
                ("user", "{input}"),
                ("agent_scratchpad", "{agent_scratchpad}")
            ])
            
            if self.doc_input.model_provider == "openai":
                agent = create_openai_functions_agent(self.llm, self.tools, prompt)
            else:
                agent = create_react_agent(self.llm, self.tools, prompt)
                
            return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def generate_document(self) -> None:
        """Generate the document using the AI agent"""
        try:
            # 1. Prepare the input for the agent
            input_text = self._prepare_agent_input()
            
            # 2. Run the agent to gather content
            logging.info("Running AI agent to generate document content...")
            agent_result = self.agent.invoke({"input": input_text})
            
            # 3. Generate document content using the document generator
            logging.info("Generating document content structure...")
            doc_content = self.doc_generator.generate_document_content(
                self.doc_input,
                agent_result.get("output", "")
            )
            
            # 4. Generate the PDF
            logging.info("Creating PDF document...")
            pdf_generator = PDFGenerator()
            pdf_generator.generate_pdf(doc_content, self.doc_input.output_file)
            
        except Exception as e:
            logging.error(f"Error in document generation process: {str(e)}")
            raise
    
    def _prepare_agent_input(self) -> str:
        """Prepare the input text for the agent"""
        key_points_text = "\n".join([f"- {point}" for point in self.doc_input.key_points])
        
        input_text = f"""
        Create a comprehensive document on the following topic:
        
        Topic: {self.doc_input.topic}
        Subtopic: {self.doc_input.subtopic}
        
        Key points to cover:
        {key_points_text}
        
        {"Please research this topic thoroughly using the available tools and provide detailed information." 
        if self.doc_input.enable_research else ""}
        
        Generate a well-structured document with:
        1. An informative introduction
        2. Detailed sections for each key point
        3. A conclusion that summarizes the main findings
        4. References/citations (if research is enabled)
        
        Organize the content logically and ensure it is comprehensive and easy to understand.
        """
        
        return input_text
