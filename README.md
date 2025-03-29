# DavinciMCP

A Python interface for controlling DaVinci Resolve with support for Media Control Protocol (MCP) and Gemini AI integration.

## Features
- Direct control of DaVinci Resolve through its Python API
- Integration with Google's Gemini AI for intelligent video editing assistance
- Cross-platform support (macOS, Windows, Linux)
- Natural Language Processing (NLP) to translate text commands into editing operations
- Media analysis capabilities for shot detection and optimizing long takes
- Command pattern implementation for extensible operations
- Feedback mechanism to explain editing decisions
- Error handling and logging
- Virtual environment support
- Test framework with mocks for Resolve API

## Requirements
- DaVinci Resolve installed with Developer/Scripting/Modules available
- Python 3.x
- Virtual environment (recommended)
- Google Gemini API key (for AI features)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/coltonbatts/DavinciMCP.git
   cd DavinciMCP
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv resolve_env
   source resolve_env/bin/activate  # On Unix/macOS
   # or
   resolve_env\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up configuration:
   ```bash
   cp .env.example .env
   # Edit .env file to add your Gemini API key
   ```

## Usage
1. Make sure DaVinci Resolve is running
2. Run the control script:
   ```bash
   python resolve_control.py
   ```

3. Example NLP commands:
   ```
   "Add a cross dissolve transition that's 1.5 seconds"
   "Cut the clip at the current position"
   "Analyze this long take and suggest cuts"
   ```

## Configuration
The application uses environment variables for configuration:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `GEMINI_TEMPERATURE`: Controls randomness in AI responses (0.0-1.0)
- `GEMINI_MAX_TOKENS`: Maximum length of AI responses
- `FEEDBACK_ENABLED`: Enable/disable operation feedback

## Project Structure
- `resolve_control.py`: Main control script and Resolve connection handler
- `config.py`: Configuration management with platform detection
- `command_pattern.py`: Implementation of command pattern for NLP control
- `media_analysis.py`: Media analysis tools for intelligent editing
- `test_resolve_control.py`: Test suite for key functionality

## Testing
Run the test suite:
```bash
pytest -v
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

