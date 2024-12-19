from app import create_app  # Import the create_app function
import os

app = create_app()  # Instantiate the application

if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST", "localhost"), port=5000)
