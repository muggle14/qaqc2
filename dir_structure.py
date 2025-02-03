import os

# Define the root folder name
root_folder = "my_python_backend"

# Create the root folder (if it doesn't exist)
os.makedirs(root_folder, exist_ok=True)

# List of files to create inside the root folder
files_to_create = [
    "main.py",
    "models.py",
    "schemas.py",       # Optional: for Pydantic models
    "requirements.txt",
    "README.md"
]

# Create each file (if it doesn't already exist)
for filename in files_to_create:
    file_path = os.path.join(root_folder, filename)
    # Open the file in append mode ('a') which creates the file if it doesn't exist
    with open(file_path, "a") as f:
        pass  # Just create an empty file

print(f"Folder structure '{root_folder}/' has been created with files: {', '.join(files_to_create)}")
