import os
import sys

# Ensure project root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Ensure database is initialized on cold start
try:
    import database
    database.ensure_db_initialized()
except Exception as e:
    app.logger.error(f"Database initialization error on startup: {e}")
