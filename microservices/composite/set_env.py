import os
from dotenv import load_dotenv

# Get the path to the current directory's .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load environment variables from .env file
load_dotenv(dotenv_path)

# Optional: print a success message for confirmation
print(f"Environment variables loaded from {dotenv_path}")