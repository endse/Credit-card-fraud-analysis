# Contributing to FraudGuard AI

Thank you for contributing to FraudGuard AI! This guide outlines our engineering standards, pull request protocol, and local testing expectations.

---

## 1. Code of Conduct & Standards

### Python (Backend & ML)
- Follow **PEP 8** formatting and style conventions.
- Maintain strict type annotations using Python standard `typing` and Pydantic models.
- Avoid global mutable state. Database interactions must pass through `backend/app/database.py`.
- ML models must remain reproducible (`random_state=42`).

### JavaScript & React (Frontend)
- Use functional React components with standard React Hooks (`useState`, `useEffect`).
- Follow the design system rules defined in `frontend/src/index.css`. Use predefined custom CSS variables (`var(--accent-cyan)`, `var(--bg-card)`) rather than ad-hoc inline styles.
- Ensure all interactive controls have semantic labels, hover feedback, and accessibility attributes.

---

## 2. Development Workflow

1. **Fork or create feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Set up local environment**:
   ```powershell
   # Backend virtualenv:
   uv venv .venv --python 3.11
   uv pip install -r backend/requirements.txt
   
   # Frontend dependencies:
   cd frontend
   npm install
   ```
3. **Execute test suites before committing**:
   ```powershell
   # 1. Run backend verification suite
   .\.venv\Scripts\python.exe backend/test_backend.py

   # 2. Run frontend production build check
   cd frontend
   npm run build
   ```
4. **Commit using Conventional Commits**:
   - `feat: ...` for new capabilities
   - `fix: ...` for bug fixes
   - `docs: ...` for documentation
   - `refactor: ...` for code quality enhancements without changing behavior

---

## 3. Pull Request Checklist

Before submitting a Pull Request:
- [ ] Automated backend test suite passes with 0 failures (`backend/test_backend.py`).
- [ ] Frontend build succeeds without compile or lint errors (`npm run build`).
- [ ] Any modified environment variables are reflected in `.env.example`, `backend/.env.example`, and `frontend/.env.example`.
- [ ] Documentation updated in `README.md` or `docs/` if modifying public APIs or ML features.
