# save_tool.py - Tool for saving document content
import os
import json
import logging
from typing import Dict, Any

from langchain_core.tools import tool

class SaveTool:
    """Tool for saving document content for later processing"""
    
    def __init__(self):
        self.temp_dir = "tmp"
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    @tool
    def save_content(self, content: str) -> str:
        """
        Save document content for later processing into a PDF.
        
        Args:
            content: Document content to save
            
        Returns:
            str: Confirmation message
        """
        logging.info("Saving document content")
        
        try:
            # Save content to a temporary file
            temp_file = os.path.join(self.temp_dir, "document_content.txt")
            
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            logging.info(f"Content saved to {temp_file}")
            return f"Content saved successfully. It will be formatted into a PDF document."
            
        except Exception as e:
            logging.error(f"Error saving content: {str(e)}")
            return f"Error saving content: {str(e)}"
    
    def get_content(self) -> str:
        """Retrieve saved content"""
        temp_file = os.path.join(self.temp_dir, "document_content.txt")
        
        if not os.path.exists(temp_file):
            return ""
        
        try:
            with open(temp_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading saved content: {str(e)}")
            return ""
    
    def get_tool(self):
        """Get the tool function for the agent"""
        return self.save_content
