# Contributing to PRISM

First off, thank you for considering contributing to PRISM! It's people like you that make PRISM such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if relevant
* Include your environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful
* List some other tools or applications where this enhancement exists

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Update the documentation

## Development Process

1. **Setup Development Environment**
   ```bash
   git clone https://github.com/YOUR_USERNAME/P.R.I.S.M.git
   cd P.R.I.S.M
   pip install -r requirements.txt
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the coding style
   - Add/update tests
   - Update documentation

4. **Test Your Changes**
   - Run the test suite
   - Test the UI/UX flows
   - Verify all features still work

5. **Submit a Pull Request**
   - Use a clear PR title
   - Include a comprehensive description
   - Reference any related issues

## Style Guide

### Python Style Guide

- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
feat: Add image size selection to Flux generator

- Add ImageSize enum for standard sizes
- Implement user selection menu
- Update documentation
- Add tests for size selection

Closes #123
```

## Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update the wiki if applicable
- Include examples for new features

## Questions?

Feel free to contact the project maintainers if you have any questions. 