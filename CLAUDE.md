# LRT Live TV Server

Flask-based live TV streaming server for LRT (Lithuanian National Broadcaster).

# Stack
- Python 3 with Flask
- Live TV stream proxying/serving

# Code Style
- Follow PEP 8
- Use snake_case for variables and functions, PascalCase for classes
- Type hints on function signatures
- Descriptive variable names; avoid abbreviations
- Keep functions focused and small

# Commands
- Run dev server: `flask run` or `python app.py`
- Install dependencies: `pip install -r requirements.txt`

# Project Conventions
- Route handlers in `routes/` or blueprints, business logic in separate modules
- Configuration via environment variables, never hardcoded secrets
- Use `.env` for local dev (never commit it)
