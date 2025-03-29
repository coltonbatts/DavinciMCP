# DavinciMCP

A Python interface for controlling DaVinci Resolve with support for Media Control Protocol (MCP) and Gemini AI integration.

## Features
- Direct control of DaVinci Resolve through its Python API
- Integration with Google's Gemini AI for intelligent video editing assistance
- Future support for Media Control Protocol (MCP)
- Error handling and logging
- Virtual environment support

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
   .esolve_env\Scriptsctivate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install google-generativeai
   ```

## Usage
1. Make sure DaVinci Resolve is running
2. Set your Gemini API key in the script
3. Run the script:
   ```python
   python resolve_control.py
   ```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

