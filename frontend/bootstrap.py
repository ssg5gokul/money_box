import sys
from pathlib import Path

def get_project_root():
    # 1. Get the absolute path of the current file
    current = Path(__file__).resolve()

    # 2. Climb up the directory tree
    # This checks the current folder and every parent above it
    for path in [current] + list(current.parents):
        # 3. Stop when we find the folder containing both projects
        if (path / "backend").is_dir() and (path / "frontend").is_dir():
            return path

    return None

def setup_project_root():
# Use it
    root = get_project_root()

    if root:
        # print(f"Detected Root: {root}")
        # Add to sys.path so you can import from backend
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    else:
        print("Could not find project root.")