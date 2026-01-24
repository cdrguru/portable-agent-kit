# Contributing to Portable Agent Collaboration Kit

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Philosophy

1. **Simplicity First** - Every change should be as simple as possible
2. **No Dependencies** - Python standard library only
3. **ASCII-Only** - All content must be ASCII for maximum compatibility
4. **Clear Documentation** - If it's not documented, it doesn't exist

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Provide a clear description and steps to reproduce
- Include Python version and OS information

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run validation:

   ```bash
   python3 -m py_compile deploy_agent_kit.py
   python3 -m py_compile .agent/tools/utilities/update_agent_conversation_log.py
   ```

5. Commit with a clear message: `git commit -m "Add feature: description"`
6. Push to your fork: `git push origin feature/your-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Keep functions focused and small
- Add docstrings to public functions

### Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Keep the first line under 72 characters
- Reference issues when applicable: "Fix #123"

## What to Contribute

### Good First Issues

- Documentation improvements
- Additional examples in README
- Bug fixes with clear reproduction steps

### Larger Contributions

Please open an issue first to discuss:

- New features or tools
- Changes to the core protocol
- Restructuring of the kit

## Testing

Before submitting:

1. Verify Python syntax compiles
2. Test deployment with `--dry-run`
3. Ensure all files are ASCII-only

```bash
# Check ASCII compliance
file .agent/**/*.md .agent/**/*.py | grep -v ASCII
```

## Questions?

Open an issue with the "question" label.

---

Thank you for helping make multi-agent collaboration easier!
