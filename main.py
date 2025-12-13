# main.py
from website import create_app

app = create_app()

if __name__ == "__main__":
    # In Docker we’ll not use debug=True, but it’s okay locally.
    app.run(host="0.0.0.0", port=5000, debug=True)
