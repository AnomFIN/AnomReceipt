# Contributing to AnomReceipt

Thank you for your interest in contributing to AnomReceipt! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant log output from `anomreceipt.log`

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- Clear description of the feature
- Use case and benefits
- Any implementation ideas

### Submitting Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.7+
- PyQt5
- Linux environment (for testing with actual printers)

### Installation

```bash
git clone https://github.com/AnomFIN/AnomReceipt.git
cd AnomReceipt
pip install -r requirements.txt
```

### Running Tests

```bash
python3 test_app.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Comment complex logic

## Project Structure

```
anomreceipt/
├── gui/          # Qt GUI components
├── printer/      # Printer interface
├── templates/    # Template management
└── locale/       # Translation system
```

## Adding New Features

### New Language Support

1. Add translations to `anomreceipt/locale/translator.py`
2. Update the `TRANSLATIONS` dictionary
3. Test UI and receipt generation

### New Template Format

1. Extend `TemplateManager` in `anomreceipt/templates/template_manager.py`
2. Add file format detection
3. Update documentation

### New Printer Support

1. Extend `ESCPOSPrinter` in `anomreceipt/printer/escpos_printer.py`
2. Add connection method
3. Test with hardware

## Testing

When adding features:
- Test manually with the GUI
- Add test cases to `test_app.py` if applicable
- Test with actual printer hardware when possible
- Verify backwards compatibility

## Documentation

Update documentation when:
- Adding new features
- Changing existing behavior
- Adding new configuration options

Files to update:
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- Code comments and docstrings

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG if present
5. Submit PR with clear description

## Code Review

Pull requests will be reviewed for:
- Code quality and style
- Test coverage
- Documentation completeness
- Backwards compatibility
- Security considerations

## Questions?

Feel free to open an issue for questions or clarifications.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
