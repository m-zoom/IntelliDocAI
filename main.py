#!/usr/bin/env python3
# main.py - Entry point for AI Document Generator
import os
import sys
import logging
import argparse
from dotenv import load_dotenv

from ai_document_agent import AIDocumentAgent
from models import DocumentInput

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    
    if missing_keys:
        logging.error(f"Missing required environment variables: {', '.join(missing_keys)}")
        logging.info("Please create a .env file with the required API keys. See .env.example for reference.")
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="AI Document Generator - Create structured PDF documents from topics")
    
    # Add arguments
    parser.add_argument("--topic", type=str, help="Main topic for the document")
    parser.add_argument("--subtopic", type=str, help="Subtopic for the document")
    parser.add_argument("--key-points", type=str, nargs="+", help="Key points to include (space-separated)")
    parser.add_argument("--model", type=str, choices=["openai", "anthropic"], default="openai", 
                        help="AI model provider to use (default: openai)")
    parser.add_argument("--output", type=str, default="output.pdf", help="Output PDF filename (default: output.pdf)")
    parser.add_argument("--research", action="store_true", help="Enable autonomous research on the topic")
    
    return parser.parse_args()

def interactive_input():
    """Get document input through interactive prompts if not provided as arguments"""
    print("AI Document Generator - Interactive Mode")
    print("=======================================")
    
    topic = input("Enter the main topic: ")
    subtopic = input("Enter the subtopic: ")
    
    key_points = []
    print("Enter key points (one per line, leave empty to finish):")
    while True:
        point = input("> ")
        if not point:
            break
        key_points.append(point)
    
    model_provider = input("Choose AI provider [openai/anthropic] (default: openai): ").lower() or "openai"
    if model_provider not in ["openai", "anthropic"]:
        print(f"Invalid provider '{model_provider}'. Using 'openai' instead.")
        model_provider = "openai"
    
    output_file = input("Output filename (default: output.pdf): ") or "output.pdf"
    if not output_file.endswith(".pdf"):
        output_file += ".pdf"
    
    research = input("Enable autonomous research? [y/N]: ").lower() in ["y", "yes"]
    
    return DocumentInput(
        topic=topic,
        subtopic=subtopic,
        key_points=key_points,
        model_provider=model_provider,
        output_file=output_file,
        enable_research=research
    )

def main():
    """Main entry point for the application"""
    load_environment()
    args = parse_arguments()
    
    # If required arguments are missing, use interactive mode
    if not args.topic:
        doc_input = interactive_input()
    else:
        doc_input = DocumentInput(
            topic=args.topic,
            subtopic=args.subtopic or "",
            key_points=args.key_points or [],
            model_provider=args.model,
            output_file=args.output,
            enable_research=args.research
        )
    
    # Create AI document agent
    agent = AIDocumentAgent(doc_input)
    
    try:
        # Generate the document
        logging.info(f"Generating document about '{doc_input.topic}' using {doc_input.model_provider}...")
        agent.generate_document()
        logging.info(f"Document successfully generated: {doc_input.output_file}")
    except Exception as e:
        logging.error(f"Error generating document: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
