import os
import hashlib
import subprocess
import sys

def install_tqdm():
    """Ensure that tqdm is installed."""
    try:
        import tqdm
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
        import tqdm

install_tqdm()
from tqdm import tqdm

def hash_file(file_path):
    """Generate a hash for a given file."""
    hash_algo = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def find_duplicates(directory):
    """Find duplicate files in the given directory."""
    files_by_hash = {}
    duplicates = []

    # Get the total number of files for the progress bar
    total_files = sum([len(files) for _, _, files in os.walk(directory)])

    with tqdm(total=total_files, desc="Processing files", unit="file") as pbar:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                if file_hash in files_by_hash:
                    duplicates.append((file_path, files_by_hash[file_hash]))
                else:
                    files_by_hash[file_hash] = file_path
                pbar.update(1)  # Update the progress bar

    return duplicates

def is_safe_to_delete(file_path, safe_directories):
    """Check if a file is in a directory that is safe for deletion."""
    for safe_dir in safe_directories:
        if file_path.startswith(safe_dir):
            return True
    return False

def main():
    backup_dir = os.getenv('backup_dir')
    if not backup_dir:
        backup_dir = input("Please enter the path to your extracted files: ")
    if not os.path.exists(backup_dir):
        print(f"The path {backup_dir} does not exist. Please check and try again.")
        return

    # Define directories where deletions are safe
    safe_directories = [
        os.path.join(backup_dir, 'uploads/'),
        os.path.join(backup_dir, 'images/'),
        # Add more directories as needed
    ]

    duplicates = find_duplicates(backup_dir)
    if duplicates:
        print("Duplicate files found:")
        for original, duplicate in duplicates:
            print(f"Original: {original}")
            print(f"Duplicate: {duplicate}")
            print("-" * 50)

        action = input("Do you want to delete duplicates from folders named 'uploads' and 'images'? (yes/no): ").strip().lower()
        if action == 'yes':
            # Use a set to track deleted files and avoid multiple deletions
            deleted_files = set()
            for _, duplicate in duplicates:
                if duplicate not in deleted_files and is_safe_to_delete(duplicate, safe_directories):
                    print(f"Deleting duplicate: {duplicate}")
                    os.remove(duplicate)
                    deleted_files.add(duplicate)
                    print("-" * 50)
                else:
                    print(f"Skipping deletion of: {duplicate}")
        elif action == 'list':
            print("Find and List mode: No files were deleted.")
        else:
            print("Invalid option. No files were deleted.")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    main()
