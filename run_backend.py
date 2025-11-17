"""
Helper script to run the FastAPI app with correct PYTHONPATH.
Use this when `uvicorn backend.main:app` raises ModuleNotFoundError.

Run:
  python run_backend.py

It will add the repository root to sys.path and start uvicorn using the project's virtualenv python.
"""
import sys
from pathlib import Path

# Add repository root to sys.path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Now import uvicorn and the app
try:
    from backend.main import app
except Exception as e:
    raise RuntimeError(f"Failed to import app from backend.main: {e}")

if __name__ == "__main__":
    import uvicorn
    # Use import string so reload/watchers work correctly in subprocess mode.
    # Passing the app object to uvicorn.run disables reload/workers warnings.
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
