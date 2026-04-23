# Contributing to Rudra

Thank you for your interest in contributing to Rudra! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/rudra.git`
3. Copy the environment template: `cp .env.example .env` and fill in real values
4. Create a branch: `git checkout -b feature/my-feature`
5. Make your changes
6. Run the test suite locally (see "Running Tests" below). Every pull request must keep unit and integration tests green.
7. Test the full stack: `docker compose up --build`
8. Commit: `git commit -m "feat: add my feature"`
9. Push: `git push origin feature/my-feature`
10. Open a Pull Request against `main`. CI will run lint, unit tests, integration tests, a dependency security audit and Docker image builds. All of these must pass before a PR can be merged.

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
npm ci
npm run dev
```

## Running Tests

Rudra ships with a pytest suite split into unit tests (pure functions, no
services) and integration tests (real MongoDB, mocked Keycloak).

```bash
# Install test dependencies
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio

# Unit tests only. Fast, no external services required.
pytest tests/unit/ -v

# Integration tests. Require a MongoDB instance on localhost:27017.
# The easiest way to get one is:
docker run -d --rm --name rudra-test-mongo -p 27017:27017 mongo:7

# Export the env vars the backend expects, then run the suite.
export KEYCLOAK_ADMIN_USER=test-admin
export KEYCLOAK_ADMIN_PASSWORD=test-admin-password
export MONGODB_URL=mongodb://localhost:27017
export MONGODB_DB=rudra_test
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=local-test-secret

pytest tests/ -v
```

Pull requests must add tests alongside any non trivial change. New
endpoints need at least one integration test; new pure helpers need at
least one unit test.

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
├── tests/              # pytest suite
│   ├── unit/           # pure function tests, no services required
│   └── integration/    # FastAPI TestClient + real MongoDB
├── docker-compose.yml
├── CHANGELOG.md        # user facing release history
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
