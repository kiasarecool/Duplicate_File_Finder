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

# Supported image and video file types
SUPPORTED_FILE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif', '.ico', '.svg', '.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.webm'}

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
                # Skip hidden files and unsupported file types
                if file.startswith('.') or not os.path.splitext(file)[1].lower() in SUPPORTED_FILE_TYPES:
                    continue
                file_hash = hash_file(file_path)
                if file_hash in files_by_hash:
                    duplicates.append((file_path, files_by_hash[file_hash]))
                else:
                    files_by_hash[file_hash] = file_path
                pbar.update(1)  # Update the progress bar

    return duplicates

def clean_filename(filename):
    """Clean the filename by removing redundant parts."""
    # Remove _ssl=1 and ?ssl=1
    filename = filename.replace('_ssl=1', '').replace('?ssl=1', '')

    # Remove duplicate extensions
    parts = filename.split('.')
    unique_parts = []
    for part in parts:
        if part not in unique_parts:
            unique_parts.append(part)
    filename = '.'.join(unique_parts)

    # Ensure the last part is the correct extension
    if 'webp' in unique_parts:
        unique_parts = [part for part in unique_parts if part not in ['jpg', 'jpeg', 'png', 'gif']]
        unique_parts.append('webp')
        filename = '.'.join(unique_parts)

    return filename

def rename_files_in_directory(directory, conflict_action):
    total_files = 0
    interacted_files = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if '_ssl=1' in file or '?ssl=1' in file or any(ext in file for ext in SUPPORTED_FILE_TYPES):
                total_files += 1

    with tqdm(total=total_files, desc="Renaming files", unit="file") as pbar:
        for root, _, files in os.walk(directory):
            for file in files:
                if '_ssl=1' in file or '?ssl=1' in file or any(ext in file for ext in SUPPORTED_FILE_TYPES):
                    old_file_path = os.path.join(root, file)
                    new_file_name = clean_filename(file)
                    new_file_path = os.path.join(root, new_file_name)

                    if os.path.exists(new_file_path):
                        if conflict_action == 3:  # Ask every time
                            action = input(f"The file {new_file_path} already exists. Do you want to overwrite it? (yes/no): ").strip().lower()
                            if action == 'yes':
                                os.rename(old_file_path, new_file_path)
                                print(f'Overwritten: {old_file_path} -> {new_file_path}')
                            else:
                                os.remove(old_file_path)
                                print(f'Skipped and deleted: {old_file_path}')
                        elif conflict_action == 2:  # Overwrite
                            os.rename(old_file_path, new_file_path)
                            print(f'Overwritten: {old_file_path} -> {new_file_path}')
                        elif conflict_action == 1:  # Skip + Delete
                            os.remove(old_file_path)
                            print(f'Skipped and deleted: {old_file_path}')
                    else:
                        os.rename(old_file_path, new_file_path)
                        print(f'Renamed: {old_file_path} -> {new_file_path}')
                    
                    interacted_files += 1
                    pbar.update(1)

    return interacted_files

def main():
    backup_dir = os.getenv('backup_dir')
    if not backup_dir:
        backup_dir = input("Please enter the path to your extracted files: ")
    if not os.path.exists(backup_dir):
        print(f"The path {backup_dir} does not exist. Please check and try again.")
        return

    # Ask the user if they want to analyze everything or just the wp-content/uploads folder
    analysis_choice = input("Would you like to analyze everything or just the 'wp-content/uploads' folder? (everything/uploads): ").strip().lower()

    if analysis_choice == 'uploads':
        analysis_dir = os.path.join(backup_dir, 'wp-content', 'uploads')
    else:
        analysis_dir = backup_dir

    if not os.path.exists(analysis_dir):
        print(f"The path {analysis_dir} does not exist. Please check and try again.")
        return

    action = input("Do you want to 'Find and List' (no actual deletion) or 'Find and Remove' (delete duplicates)? (list/remove): ").strip().lower()
    if action not in ['list', 'remove']:
        print("Invalid option. Please enter 'list' or 'remove'.")
        return

    while True:
        duplicates = find_duplicates(analysis_dir)
        if not duplicates:
            print("No duplicates found.")
            break

        print("Duplicate files found:")
        for original, duplicate in duplicates:
            print(f"Original: {original}")
            print(f"Duplicate: {duplicate}")
            print("-" * 50)

        print(f"Total number of duplicate files found: {len(duplicates)}")

        if action == 'remove':
            # Use a set to track deleted files and avoid multiple deletions
            deleted_files = set()
            num_deleted = 0
            for _, duplicate in duplicates:
                if duplicate not in deleted_files:
                    print(f"Deleting duplicate: {duplicate}")
                    os.remove(duplicate)
                    deleted_files.add(duplicate)
                    num_deleted += 1
                    print("-" * 50)
                else:
                    print(f"Skipping deletion of: {duplicate}")
            print(f"Total number of duplicate files deleted: {num_deleted}")
        elif action == 'list':
            print("Find and List mode: No files were deleted.")
            break

if __name__ == "__main__":
    main()
