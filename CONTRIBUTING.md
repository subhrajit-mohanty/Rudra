# Contributing to Rudra

Thank you for your interest in contributing to Rudra! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/rudra.git`
3. Create a branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Test locally: `docker compose up --build`
6. Commit: `git commit -m "feat: add my feature"`
7. Push: `git push origin feature/my-feature`
8. Open a Pull Request

## Development Setup

```bash
# Start all services
docker compose up --build

# Backend only (for faster iteration)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend only
cd frontend
npm install
npm run dev
```

## Project Structure

```
rudra/
├── backend/            # FastAPI application
│   ├── main.py         # API endpoints (50+)
│   ├── database.py     # MongoDB operations
│   ├── keycloak_client.py  # Keycloak Admin API wrapper
│   ├── auth.py         # JWT + password hashing
│   └── config.py       # Plans, settings, env vars
├── frontend/           # React + Vite dashboard
│   └── src/
│       ├── pages/      # Dashboard pages (8 tabs)
│       ├── components/ # Layout, Modal
│       ├── contexts/   # Auth context
│       └── utils/      # API client
├── sdk/                # Python & JavaScript SDKs
│   ├── python/         # rudra Python package
│   └── javascript/     # @rudra/sdk npm package
├── docker-compose.yml
├── docs.html           # Full documentation
└── LICENSE             # MIT
```

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `refactor:` — Code refactoring
- `test:` — Adding tests
- `chore:` — Maintenance

## Areas to Contribute

- **Backend**: New API endpoints, Keycloak integrations, plan features
- **Frontend**: UI improvements, new dashboard pages, accessibility
- **SDK**: Language SDKs (Go, Java, Ruby, PHP)
- **Docs**: Tutorials, examples, API docs
- **Tests**: Unit tests, integration tests, E2E tests
- **DevOps**: Helm charts, Terraform modules, CI/CD

## Code Style

- **Python**: Follow PEP 8, use type hints
- **JavaScript/React**: Functional components, hooks
- **CSS**: CSS variables, BEM-ish naming

## Reporting Issues

Use GitHub Issues with one of these labels:
- `bug` — Something isn't working
- `feature` — New feature request
- `docs` — Documentation improvement
- `question` — General question

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
