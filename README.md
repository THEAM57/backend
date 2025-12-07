In order to run the backend:
1. Install **uv** on your system
2. cd into the backend repository, run `uv sync` - the project dependencies will be installed in a virtual environment
3.  source .venv/bin/activate
4. `uv run main.py` or  `uvicorn main:app --host 0.0.0.0 --reload` will run the server, it will be available at *localhost:8000*
