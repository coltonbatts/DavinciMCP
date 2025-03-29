# Contributing to DavinciMCP

Thank you for considering contributing to DavinciMCP! This document outlines the process for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. Any form of harassment or disrespectful behavior will not be tolerated.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the [Issues](https://github.com/coltonbatts/DavinciMCP/issues).
2. If not, create a new issue with a descriptive title and clear description.
3. Include steps to reproduce the bug, expected behavior, and actual behavior.
4. Include your environment details (OS, Python version, DaVinci Resolve version).

### Suggesting Enhancements

1. Check if the enhancement has already been suggested in the [Issues](https://github.com/coltonbatts/DavinciMCP/issues).
2. If not, create a new issue with a descriptive title and clear description.
3. Include a rationale for the enhancement and how it would benefit the project.

### Pull Requests

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes in the branch.
4. Run tests to ensure your changes don't break existing functionality.
5. Submit a pull request with a clear description of the changes.

## Development Setup

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

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black isort
   ```

4. Set up pre-commit hooks (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Coding Guidelines

- Follow PEP 8 style guidelines.
- Write docstrings for all functions, classes, and modules.
- Use type hints where appropriate.
- Keep functions small and focused on a single task.
- Write tests for new functionality.

## Testing

Run tests using pytest:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=.
```

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 