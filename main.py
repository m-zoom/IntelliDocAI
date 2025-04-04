#!/usr/bin/env python3
# main.py - Entry point for AI Document Generator
import os
import sys
import logging
import threading
from datetime import datetime
from flask import Flask, request, render_template, send_file, redirect, flash, jsonify
from dotenv import load_dotenv

from ai_document_agent import AIDocumentAgent
from models import DocumentInput

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Check for required API keys
required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
missing_keys = [key for key in required_keys if not os.environ.get(key)]

if missing_keys:
    logging.error(f"Missing required environment variables: {', '.join(missing_keys)}")
    logging.info("Please create a .env file with the required API keys. See .env.example for reference.")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Global variables
current_generation_thread = None
last_generation_result = {"status": None, "message": None, "file_path": None}

@app.route('/')
def index():
    """Home page with document generation form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_document():
    """Generate document from form submission"""
    global current_generation_thread, last_generation_result
    
    # Check if a generation is already in progress
    if current_generation_thread and current_generation_thread.is_alive():
        flash("A document generation is already in progress. Please wait for it to complete.", "warning")
        return redirect('/')
    
    # Reset last result
    last_generation_result = {"status": "processing", "message": "Document generation in progress...", "file_path": None}
    
    # Get form data
    topic = request.form.get('topic', '').strip()
    subtopic = request.form.get('subtopic', '').strip()
    key_points_text = request.form.get('key_points', '')
    key_points = [point.strip() for point in key_points_text.split('\n') if point.strip()]
    model_provider = request.form.get('model_provider', 'openai')
    enable_research = request.form.get('enable_research') == 'on'
    
    # Validate input
    if not topic:
        flash("Topic is required", "danger")
        return redirect('/')
    
    # Create unique output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"document_{timestamp}.pdf"
    
    # Create document input
    doc_input = DocumentInput(
        topic=topic,
        subtopic=subtopic,
        key_points=key_points,
        model_provider=model_provider,
        output_file=output_file,
        enable_research=enable_research
    )
    
    # Start document generation in a separate thread
    def generate_doc_thread():
        global last_generation_result
        try:
            # Create AI document agent
            agent = AIDocumentAgent(doc_input)
            
            # Generate the document
            logging.info(f"Generating document about '{doc_input.topic}' using {doc_input.model_provider}...")
            agent.generate_document()
            
            # Update result
            last_generation_result = {
                "status": "success", 
                "message": f"Document successfully generated", 
                "file_path": output_file
            }
            logging.info(f"Document successfully generated: {output_file}")
            
        except Exception as e:
            error_message = f"Error generating document: {str(e)}"
            logging.error(error_message)
            last_generation_result = {"status": "error", "message": error_message, "file_path": None}
    
    # Start the thread
    current_generation_thread = threading.Thread(target=generate_doc_thread)
    current_generation_thread.start()
    
    # Redirect to status page
    return redirect('/status')

@app.route('/status')
def check_status():
    """Check the status of document generation"""
    return render_template('status.html', result=last_generation_result)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download the generated PDF file"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "danger")
        return redirect('/')

@app.route('/cli')
def cli_instructions():
    """Instructions for CLI usage"""
    return render_template('index.html', show_cli=True)

if __name__ == "__main__":
    # If script is run directly without arguments, start the web server
    if len(sys.argv) == 1:
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        # Otherwise, use CLI mode
        import argparse
        
        parser = argparse.ArgumentParser(description="AI Document Generator - Create structured PDF documents from topics")
        
        # Add arguments
        parser.add_argument("--topic", type=str, help="Main topic for the document")
        parser.add_argument("--subtopic", type=str, help="Subtopic for the document")
        parser.add_argument("--key-points", type=str, nargs="+", help="Key points to include (space-separated)")
        parser.add_argument("--model", type=str, choices=["openai", "anthropic"], default="openai", 
                            help="AI model provider to use (default: openai)")
        parser.add_argument("--output", type=str, default="output.pdf", help="Output PDF filename (default: output.pdf)")
        parser.add_argument("--research", action="store_true", help="Enable autonomous research on the topic")
        
        args = parser.parse_args()
        
        # If required arguments are missing, show help
        if not args.topic:
            parser.print_help()
            sys.exit(1)
        
        # Create document input
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
            print(f"Generating document about '{doc_input.topic}' using {doc_input.model_provider}...")
            agent.generate_document()
            print(f"Document successfully generated: {doc_input.output_file}")
        except Exception as e:
            print(f"Error generating document: {str(e)}")
            sys.exit(1)