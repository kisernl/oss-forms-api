# Contributing to Mayfly Forms

Thank you for your interest in contributing to Mayfly Forms! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists in our [GitHub Issues](https://github.com/your-username/mayfly-forms/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, AWS region, etc.)

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with the "enhancement" label
3. Describe the feature and its use case
4. Be open to discussion and feedback

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**:
   - Test locally with your AWS environment
   - Ensure existing functionality still works
5. **Submit a pull request**:
   - Clear description of changes
   - Reference any related issues
   - Include screenshots if UI changes

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 14+ (for Serverless Framework)
- AWS CLI configured
- AWS account with SES access

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/mayfly-forms.git
cd mayfly-forms

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Set up environment variables
export VALID_API_KEYS="your-test-key"
export SES_DEFAULT_SENDER="test@example.com"

# Run locally (optional)
python app/main.py
```

### Testing

Before submitting a pull request:

1. Test your changes locally
2. Deploy to a test environment if possible
3. Verify no existing functionality is broken
4. Test with different API key configurations

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to new functions and classes
- Keep functions focused and small
- Comment complex logic

## Documentation

- Update README.md for significant changes
- Update deployment guides if needed
- Add code comments for complex functionality
- Update API documentation for endpoint changes

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation as needed
3. Add tests if applicable
4. Ensure CI passes (when available)
5. Request review from maintainers
6. Address feedback promptly

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Focus on constructive feedback
- Ask questions if you're unsure

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

Thank you for contributing to Mayfly Forms! 🚀