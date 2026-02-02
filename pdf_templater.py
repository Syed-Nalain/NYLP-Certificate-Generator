"""
Thin launcher for the refactored NYLP Certificate generator application.
NYLP Certificate generator
Made by Nalain-e-Muhammad

This file delegates to app.main().
"""
import sys

try:
    import app
except Exception as e:
    sys.stderr.write("Failed to import app module. Ensure app.py exists in the workspace and is importable.\n")
    raise

if __name__ == "__main__":
    app.main()