# Contributing to Data Preprocessing Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues
1. Check if the issue already exists
2. Use the issue template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots (if applicable)

### Suggesting Features
1. Open an issue with [Feature Request] prefix
2. Describe the feature and use case
3. Explain expected behavior
4. Add mockups or examples if possible

### Code Contributions

#### Setup Development Environment
1. Fork the repository
2. Clone your fork
3. Follow QUICKSTART.md for setup
4. Create a new branch: `git checkout -b feature/your-feature-name`

#### Coding Standards

**Backend (Python)**
- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions/classes
- Write unit tests for new features
- Use meaningful variable names

**Frontend (TypeScript/React)**
- Follow ESLint configuration
- Use TypeScript for type safety
- Create reusable components
- Follow existing component patterns
- Use meaningful component/variable names

#### Commit Messages
Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Example: `feat: add support for JSON file upload`

#### Pull Request Process
1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with clear description:
   - What changes were made
   - Why the changes were needed
   - How to test the changes
6. Link related issues
7. Wait for review

### Testing

**Backend Tests**
```bash
cd backend
pytest tests/ -v
```

**Frontend Tests**
```bash
cd frontend
npm test
```

### Code Review
- Be respectful and constructive
- Address all review comments
- Update PR based on feedback
- Squash commits before merge

## Development Guidelines

### Adding New Issue Detection
1. Add detection logic in `backend/app/services/data_analyzer.py`
2. Add issue type to `IssueType` enum in `schemas.py`
3. Add recommended actions
4. Update frontend `IssueList.tsx` for display
5. Add tests

### Adding New Preprocessing Methods
1. Add method in `backend/app/services/data_preprocessor.py`
2. Update `_apply_action` method
3. Add to recommended actions
4. Update frontend UI for selection
5. Add tests

### Adding UI Components
1. Create component in `src/components/`
2. Use TypeScript interfaces
3. Follow existing styling patterns
4. Make it reusable
5. Add JSDoc comments

## Questions?
Open an issue with [Question] prefix or reach out to maintainers.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
