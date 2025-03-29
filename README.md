# DavinciMCP

Python interface for controlling DaVinci Resolve with AI integration via the Model Context Protocol (MCP)

## Features

- Natural language control of DaVinci Resolve editing operations
- AI-powered editing suggestions and automation
- Media analysis and metadata extraction
- Advanced timeline manipulation
- Model Context Protocol (MCP) integration for enhanced AI capabilities

## Installation

```bash
# Clone the repository
git clone https://github.com/coltonbatts/DavinciMCP.git
cd DavinciMCP

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install the package
pip install -e .
```

## Configuration

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` to add your API keys:
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://ai.google.dev/)
- `ANTHROPIC_API_KEY`: Get from [Anthropic Console](https://console.anthropic.com/) (for Model Context Protocol)

## Usage

### Basic CLI

```bash
# Start the interactive CLI
davincimcp interactive

# Or use the GUI
davincimcp gui
```

### Model Context Protocol (MCP)

The application supports the Model Context Protocol for advanced AI integration:

```bash
# Start MCP interactive mode with Claude integration
davincimcp mcp

# Use custom MCP server script
davincimcp mcp --server-script ./path/to/server.py

# Run interactive mode with MCP enabled
davincimcp interactive --use-mcp

# Start an MCP server
davincimcp server
```

### Interactive Mode

DavinciMCP provides an interactive CLI for natural language control:

1. Start interactive mode:
   ```bash
   davincimcp interactive
   ```

2. Example NLP commands:
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
- `ANTHROPIC_API_KEY`: Your Anthropic Claude API key (for MCP)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `GEMINI_TEMPERATURE`: Controls randomness in AI responses (0.0-1.0)
- `GEMINI_MAX_TOKENS`: Maximum length of AI responses
- `FEEDBACK_ENABLED`: Enable/disable operation feedback
- `MCP_ENABLED`: Enable/disable Model Context Protocol
- `MCP_SERVER_SCRIPT`: Path to MCP server script
- `MCP_SERVER_CAPABILITIES`: Server capabilities (resources,tools,prompts,sampling)

See `.env.example` for all available configuration options.

## Project Structure
```
DavinciMCP/
├── davincimcp/           # Main package
│   ├── core/             # Core functionality and Resolve connection
│   │   ├── mcp/          # Model Context Protocol implementation
│   │   └── media/        # Media control operations
│   ├── commands/         # Command pattern implementation
│   ├── media/            # Media analysis tools
│   ├── utils/            # Utility functions and configuration
│   ├── ui/               # GUI components and visualization
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
├── examples/             # Example scripts
│   └── mcp/              # MCP examples
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

