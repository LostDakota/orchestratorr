# 🤝 Contributing to Orchestratorr

Thank you for your interest in contributing to Orchestratorr! This document provides guidelines and instructions for contributing to the project.

## 📋 Issue Reporting

We use GitHub Issues to track bugs and feature requests. Before creating a new issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the appropriate template** when creating a new issue
3. **Provide as much detail as possible** to help us understand and reproduce the issue

### 🐛 Bug Reports
Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) when reporting bugs. Include:
- Clear steps to reproduce the issue
- Expected vs actual behavior
- Environment information (OS, browser, Orchestratorr version)
- Screenshots or logs if applicable

### ✨ Feature Requests  
Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) when suggesting new features. Include:
- Clear description of the proposed feature
- Problem it solves or improvement it provides
- Use cases and expected benefits
- Any technical considerations

## 🔧 Development Setup

### Prerequisites
- Python 3.10+ and pip
- Node.js 18+ and npm
- Git

### Getting Started
1. Fork the repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/orchestratorr.git
   cd orchestratorr
   ```
3. Set up the development environment:
   ```bash
   # Backend setup
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd ../frontend
   npm install
   ```

### Running the Project
```bash
# Backend (from backend/ directory)
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (from frontend/ directory)
npm run dev
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
pytest
```

## 🔀 Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit with clear messages:
   ```bash
   git commit -m "feat: add new feature" -m "Detailed description of changes"
   ```

3. **Ensure tests pass** and code follows project conventions

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** against the `main` branch of the main repository

### Pull Request Guidelines
- **Keep PRs focused** on a single feature or bug fix
- **Include tests** for new functionality
- **Update documentation** if needed
- **Follow commit message conventions** (see below)

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, missing semi-colons, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks, dependencies, etc.

Example: `feat: add universal search functionality`

## 🏗️ Code Style

### Frontend (Svelte/JavaScript)
- Use ES6+ features where appropriate
- Follow Svelte best practices
- Use meaningful variable and function names
- Add comments for complex logic

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and single-purpose

## 🚀 Release Process

Releases are managed by the maintainers. Version numbers follow [Semantic Versioning](https://semver.org/).

## ❓ Questions or Need Help?

- **Check the [README](README.md)** for setup and usage instructions
- **Browse existing issues** to see if your question has been answered
- **Open a discussion** (if enabled) for general questions
- **Open an issue** for specific problems or feature requests

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) (if present).

---

Thank you for contributing to Orchestratorr! 🎉