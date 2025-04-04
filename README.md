# IntelliDocAI

IntelliDocAI is an intelligent document generation system that leverages AI capabilities to create, process, and manage documents efficiently. This system combines document generation with AI-powered content creation and web interface accessibility.

## Features

- AI-powered document generation
- PDF document creation and management
- Web-based user interface
- Template-based document processing
- Wiki and search tool integration
- Real-time document status tracking

## Project Structure

```
IntelliDocAI/
├── ai_document_agent.py    # AI document processing core
├── document_generator.py   # Document generation logic
├── pdf_generator.py       # PDF creation utilities
├── web_interface.py      # Web UI implementation
├── models.py            # Data models and structures
├── templates/          # HTML templates for web interface
└── tools/             # Utility tools (search, wiki, save)
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv v
   ```
3. Activate the virtual environment:
   - Windows: `v\Scripts\activate`
   - Unix/MacOS: `source v/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and configure your environment variables

## Usage

1. Start the web interface:
   ```bash
   python web_interface.py
   ```

2. Access the application through your web browser at `http://localhost:5000`

3. Use the web interface to:
   - Generate new documents
   - Track document status
   - View and download generated PDFs

## Environment Configuration

Configure the following environment variables in your `.env` file:

```env
# Required API keys and configurations
API_KEY=your_api_key
OTHER_CONFIG=value
```

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository.
