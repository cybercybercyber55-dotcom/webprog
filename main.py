import sys
import os

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from website import create_app
from website import db   # <-- IMPORTANT: import db from your package

# Create Flask app
app = create_app()

# Run database creation safely
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
