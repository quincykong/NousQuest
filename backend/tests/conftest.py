import os
import pytest
import subprocess
from app import create_app, db

@pytest.fixture(scope="module")
def app_instance():
    """Create the test Flask app."""
    app = create_app("testing")
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def test_client(app_instance):
    """Provide a test client for the app."""
    return app_instance.test_client()

@pytest.fixture(scope="function")
def init_database(app_instance):
    """Fixture to initialize the database (create and drop tables)."""
    # Create all tables before the test
    db.create_all()
    yield db
    # Drop all tables after the test
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope="function")
def reset_database(init_database, app_instance):
    """
    Fixture to reset and populate the database using the gendata.py program.
    Requires the database tables to be already created.
    """
    # Path to your `gendata.py` program
    # program_path = "backend/gendefaultdata.py"
    # Dynamically determine the absolute path to `gendefaultdata.py`
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of conftest.py
    program_path = os.path.normpath(os.path.join(current_dir, "../gendefaultdata.py"))


    # Execute `gendata.py` as a subprocess
    result = subprocess.run(["python", program_path, "testing"], capture_output=True, text=True)

    # Check for errors during execution
    if result.returncode != 0:
        print(f"Error in database reset program:\n{result.stderr}")
        raise RuntimeError("Database reset failed.")
    else:
        print(f"Database reset successfully:\n{result.stdout}")

    yield  # The database is now reset and populated for the test

    # Optional teardown logic (e.g., clear the database after the test)
    db.session.remove()
