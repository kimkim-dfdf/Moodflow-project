# ==============================================
# MoodFlow - Application Entry Point
# ==============================================
# Run this file to start the Flask server
# Command: python run.py
# ==============================================

from app import create_app

# Create the Flask application
app = create_app()

# Run the server
if __name__ == "__main__":
    print("Starting MoodFlow Backend Server...")
    print("Server running at: http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
