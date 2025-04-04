#!/usr/bin/env python3
# main.py - Entry point for AI Document Generator
import os
import sys
import logging
from flask import Flask, request, render_template_string, send_file, jsonify
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

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Document Generator</title>
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <style>
        .container { max-width: 800px; margin-top: 30px; }
        textarea { min-height: 120px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4 text-center">AI Document Generator</h1>
                
                {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                {% if success %}
                    <div class="alert alert-success">{{ success }}</div>
                {% endif %}
                
                <div class="card mb-4">
                    <div class="card-body">
                        <form action="/generate" method="post">
                            <div class="mb-3">
                                <label for="topic" class="form-label">Topic *</label>
                                <input type="text" class="form-control" id="topic" name="topic" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="subtopic" class="form-label">Subtopic (Optional)</label>
                                <input type="text" class="form-control" id="subtopic" name="subtopic">
                            </div>
                            
                            <div class="mb-3">
                                <label for="key_points" class="form-label">Key Points (One per line)</label>
                                <textarea class="form-control" id="key_points" name="key_points" rows="4" placeholder="Enter key points, one per line"></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">AI Model Provider</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="model_provider" id="openai" value="openai" checked>
                                    <label class="form-check-label" for="openai">
                                        OpenAI (GPT-4o)
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="model_provider" id="anthropic" value="anthropic">
                                    <label class="form-check-label" for="anthropic">
                                        Anthropic (Claude 3.5 Sonnet)
                                    </label>
                                </div>
                            </div>
                            
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="enable_research" name="enable_research">
                                <label class="form-check-label" for="enable_research">Enable autonomous research</label>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Generate Document</button>
                        </form>
                    </div>
                </div>
                
                {% if result %}
                    <div class="card mb-4">
                        <div class="card-body">
                            <h5 class="card-title">Document Generation Result</h5>
                            <p>{{ result.message }}</p>
                            {% if result.file_path %}
                                <a href="/download/{{ result.file_path }}" class="btn btn-success">Download PDF</a>
                            {% endif %}
                        </div>
                    </div>
                {% endif %}
                
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">How It Works</h5>
                        <p>This tool uses advanced AI models to generate well-structured PDF documents on any topic you provide:</p>
                        <ol>
                            <li>Enter a main topic and optional subtopic</li>
                            <li>Add key points you want covered (optional)</li>
                            <li>Choose between OpenAI or Anthropic models</li>
                            <li>Enable research if you want the AI to gather information autonomously</li>
                            <li>Click "Generate Document" to create your PDF</li>
                        </ol>
                        <p class="mb-0 text-secondary"><small>Note: Document generation may take a few minutes, especially with research enabled.</small></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page with document generation form"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_document():
    """Generate document from form submission"""
    # Get form data
    topic = request.form.get('topic', '').strip()
    subtopic = request.form.get('subtopic', '').strip()
    key_points_text = request.form.get('key_points', '')
    key_points = [point.strip() for point in key_points_text.split('\n') if point.strip()]
    model_provider = request.form.get('model_provider', 'openai')
    enable_research = request.form.get('enable_research') == 'on'
    
    # Validate input
    if not topic:
        return render_template_string(HTML_TEMPLATE, error="Topic is required")
    
    # Create output filename
    output_file = f"{topic.lower().replace(' ', '_')}.pdf"
    
    # Create document input
    doc_input = DocumentInput(
        topic=topic,
        subtopic=subtopic,
        key_points=key_points,
        model_provider=model_provider,
        output_file=output_file,
        enable_research=enable_research
    )
    
    try:
        # Create AI document agent
        agent = AIDocumentAgent(doc_input)
        
        # Generate the document
        logging.info(f"Generating document about '{doc_input.topic}' using {doc_input.model_provider}...")
        agent.generate_document()
        
        result = {
            "status": "success", 
            "message": f"Document successfully generated!",
            "file_path": output_file
        }
        
        logging.info(f"Document successfully generated: {output_file}")
        return render_template_string(HTML_TEMPLATE, result=result, success="Document generation completed successfully!")
        
    except Exception as e:
        error_message = f"Error generating document: {str(e)}"
        logging.error(error_message)
        return render_template_string(HTML_TEMPLATE, error=error_message)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download the generated PDF file"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"Error downloading file: {str(e)}")

@app.route('/cli')
def cli_instructions():
    """Instructions for CLI usage"""
    instructions = """
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">CLI Usage Instructions</h5>
            <p>You can also use this tool directly from the command line:</p>
            <pre class="bg-dark text-light p-3 rounded">
python main.py --topic "Your Topic" --subtopic "Your Subtopic" --key-points "Point 1" "Point 2" --model openai --output output.pdf --research
            </pre>
            <p>Parameters:</p>
            <ul>
                <li><strong>--topic</strong>: Main topic for the document (required)</li>
                <li><strong>--subtopic</strong>: Subtopic for the document (optional)</li>
                <li><strong>--key-points</strong>: Key points to include (space-separated)</li>
                <li><strong>--model</strong>: AI model provider to use (openai or anthropic, default: openai)</li>
                <li><strong>--output</strong>: Output PDF filename (default: output.pdf)</li>
                <li><strong>--research</strong>: Enable autonomous research on the topic</li>
            </ul>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE + instructions)

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