# wiki_tool.py - Wikipedia research tool
import logging
import requests
from typing import Dict, Any, Optional
from langchain_core.tools import tool

class WikiTool:
    """Tool for retrieving information from Wikipedia"""
    
    def __init__(self):
        self.wiki_api_endpoint = "https://en.wikipedia.org/w/api.php"
    
    @tool
    def wiki_search(self, query: str) -> str:
        """
        Search Wikipedia for information about a topic.
        
        Args:
            query: The search query or topic
            
        Returns:
            str: Wikipedia article content as a string
        """
        logging.info(f"Searching Wikipedia for: {query}")
        
        try:
            # First, search for the article
            article_title = self._find_article(query)
            
            if not article_title:
                return f"No Wikipedia article found for '{query}'."
            
            # Then, get the article content
            article_content = self._get_article_content(article_title)
            
            return article_content
            
        except Exception as e:
            logging.error(f"Error during Wikipedia search: {str(e)}")
            return f"Error retrieving Wikipedia information: {str(e)}"
    
    def _find_article(self, query: str) -> Optional[str]:
        """Find the most relevant Wikipedia article for the query"""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1  # Get only the top result
        }
        
        try:
            response = requests.get(self.wiki_api_endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            
            if not search_results:
                return None
            
            # Return the title of the top result
            return search_results[0].get("title")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Wikipedia API search error: {str(e)}")
            raise
    
    def _get_article_content(self, title: str) -> str:
        """Get the content of a Wikipedia article by title"""
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": 1,  # Get only the introduction
            "explaintext": 1,  # Get plain text content
            "titles": title,
            "format": "json"
        }
        
        try:
            response = requests.get(self.wiki_api_endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            # Get the first page (there should only be one)
            page_id = next(iter(pages))
            extract = pages[page_id].get("extract", "No content available.")
            
            # Format the output
            formatted_content = f"Wikipedia: {title}\n\n{extract}\n\n"
            formatted_content += f"For more information: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            
            return formatted_content
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Wikipedia API content error: {str(e)}")
            raise
    
    def get_tool(self):
        """Get the tool function for the agent"""
        return self.wiki_search
