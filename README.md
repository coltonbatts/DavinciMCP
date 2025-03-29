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
- Modern GUI interface with timeline visualization

## Requirements
- DaVinci Resolve installed with Developer/Scripting/Modules available
- Python 3.8+ 
- Virtual environment (recommended)
- Google Gemini API key (for AI features)
- PySide6 and Pillow (for GUI features)

## Installation

### From PyPI
```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install the package
pip install DavinciMCP
```

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/coltonbatts/DavinciMCP.git
   cd DavinciMCP
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Set up configuration:
   ```bash
   cp .env.example .env
   # Edit .env file to add your Gemini API key
   ```

## Usage

### Quick Start
After installation, use the `davincimcp` command:

```bash
# Start GUI mode
davincimcp gui

# Start interactive CLI mode
davincimcp interactive

# Execute a command
davincimcp cmd "Add a cross dissolve transition that's 1.5 seconds"
```

### GUI Mode
Run the application with the graphical user interface:
```bash
davincimcp gui
```

The GUI provides:
- Timeline visualization with tracks and clips
- Command panel for natural language input
- Media browser for organizing assets
- Visual feedback on AI operations

### Command Line Mode
1. Make sure DaVinci Resolve is running
2. Run the interactive CLI:
   ```bash
   davincimcp interactive
   ```

3. Example NLP commands:
   ```
   "Add a cross dissolve transition that's 1.5 seconds"
   "Cut the clip at the current position"
   "Analyze this long take and suggest cuts"
   ```

### Single Command Mode
Execute a single command:
```bash
davincimcp cmd "Add a cross dissolve transition that's 1.5 seconds"
```

### Analysis Mode
Analyze media for editing suggestions:
```bash
davincimcp analyze --target current
```

## Configuration
The application uses environment variables for configuration:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `GEMINI_TEMPERATURE`: Controls randomness in AI responses (0.0-1.0)
- `GEMINI_MAX_TOKENS`: Maximum length of AI responses
- `FEEDBACK_ENABLED`: Enable/disable operation feedback

See `.env.example` for all available configuration options.

## Project Structure
```
DavinciMCP/
├── davincimcp/           # Main package
│   ├── core/             # Core functionality and Resolve connection
│   ├── commands/         # Command pattern implementation
│   ├── media/            # Media analysis tools
│   ├── utils/            # Utility functions and configuration
│   ├── ui/               # GUI components and visualization
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
├── examples/             # Example scripts
├── docs/                 # Documentation
├── README.md
├── requirements.txt
├── setup.py
└── CHANGELOG.md
```

## Testing
Run the test suite:
```bash
pytest -v
```

## Development

### Setting up development environment
```bash
# Clone the repository
git clone https://github.com/coltonbatts/DavinciMCP.git
cd DavinciMCP

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or 
.venv\Scripts\activate  # On Windows

# Install dev dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install
```

## Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

