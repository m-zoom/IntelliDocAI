# search_tool.py - Web search tool for research
import os
import json
import logging
import requests
from typing import Dict, Any, Optional

class SearchTool:
    """Tool for performing web searches to gather information"""
    
    def __init__(self):
        # We can use various search APIs, but for simplicity, we'll use 
        # a hypothetical search API in this example
        self.search_api_key = os.environ.get("SEARCH_API_KEY", "")
        self.search_endpoint = "https://api.search.example.com/search"  # Example endpoint
    
    def search(self, query: str) -> str:
        """
        Search the web for information about a topic.
        
        Args:
            query: The search query string
            
        Returns:
            str: Search results as a string
        """
        logging.info(f"Searching for: {query}")
        
        try:
            # If search API key is available, use it
            if self.search_api_key:
                return self._api_search(query)
            
            # Fallback to a simpler search mechanism
            return self._fallback_search(query)
            
        except Exception as e:
            logging.error(f"Error during search: {str(e)}")
            return f"Error performing search: {str(e)}"
    
    def _api_search(self, query: str) -> str:
        """Perform search using a search API"""
        headers = {
            "Authorization": f"Bearer {self.search_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "limit": 5
        }
        
        try:
            response = requests.post(self.search_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            results = response.json()
            
            # Format the results
            formatted_results = self._format_search_results(results)
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Search API error: {str(e)}")
            raise
    
    def _fallback_search(self, query: str) -> str:
        """Fallback search method when API is not available"""
        # This is a simulated search response for demonstration
        # In a real implementation, you might use a library like 'googlesearch-python'
        # or another search API that doesn't require authentication
        
        logging.warning("Using fallback search method. For better results, provide a SEARCH_API_KEY.")
        return """
        No search API key provided. In a real implementation, this would use an actual search API or library.
        
        To enable real search functionality:
        1. Obtain an API key for a search service
        2. Add it to your .env file as SEARCH_API_KEY
        3. Restart the application
        
        For now, I'll rely on my existing knowledge to provide information about this topic.
        """
    
    def _format_search_results(self, results: Dict[str, Any]) -> str:
        """Format search results into a readable string"""
        if not results.get("items"):
            return "No results found."
        
        formatted = "Search Results:\n\n"
        
        for i, item in enumerate(results.get("items", []), 1):
            title = item.get("title", "No title")
            snippet = item.get("snippet", "No description")
            url = item.get("link", "No URL")
            
            formatted += f"{i}. {title}\n"
            formatted += f"   {snippet}\n"
            formatted += f"   URL: {url}\n\n"
        
        return formatted
    
    def get_tool(self):
        """Get the tool function for the agent"""
        return self.search
