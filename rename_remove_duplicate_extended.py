import os
import hashlib
import re
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

    # Remove redundant parts until it ends with a valid extension
    while not any(filename.endswith(ext) for ext in SUPPORTED_FILE_TYPES):
        filename = filename.rsplit('.', 1)[0]

    return filename

def rename_files_in_directory(directory, conflict_action):
    total_files = 0
    renamed_files = 0

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

                    if os.path.exists(new_file_path) and new_file_path != old_file_path:
                        if conflict_action == 3:  # Ask every time
                            action = input(f"The file {new_file_path} already exists. Do you want to overwrite it? (yes/no): ").strip().lower()
                            if action == 'yes':
                                os.rename(old_file_path, new_file_path)
                                print(f'Overwritten: {old_file_path} -> {new_file_path}')
                                renamed_files += 1
                            else:
                                print(f'Skipped renaming: {old_file_path}')
                        elif conflict_action == 2:  # Overwrite
                            os.rename(old_file_path, new_file_path)
                            print(f'Overwritten: {old_file_path} -> {new_file_path}')
                            renamed_files += 1
                        elif conflict_action == 1:  # Skip renaming
                            print(f'Skipped renaming: {old_file_path}')
                    elif new_file_path != old_file_path:
                        os.rename(old_file_path, new_file_path)
                        print(f'Renamed: {old_file_path} -> {new_file_path}')
                        renamed_files += 1
                    
                    pbar.update(1)

    return total_files, renamed_files

def main():
    backup_dir = input("Please enter the path to the directory with the files to rename: ")
    if not os.path.exists(backup_dir):
        print(f"The path {backup_dir} does not exist. Please check and try again.")
        return

    print("If a file with the new name already exists, what do you want to do?")
    print("1) Just Delete the bad name file")
    print("2) Overwrite existing file")
    print("3) Ask every time")
    conflict_action = int(input("Enter the number of your choice: ").strip())
    if conflict_action not in [1, 2, 3]:
        print("Invalid choice. Please enter 1, 2, or 3.")
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

    total_initial_files, total_renamed_files = rename_files_in_directory(analysis_dir, conflict_action)

    total_deleted_files = 0
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
            total_deleted_files += num_deleted
            print(f"Total number of duplicate files deleted so far: {total_deleted_files}")
        elif action == 'list':
            print("Find and List mode: No files were deleted.")
            break

    total_remaining_files = sum([len(files) for _, _, files in os.walk(analysis_dir)])

    print(f"\nSummary:")
    print(f"Total initial files: {total_initial_files}")
    print(f"Total files renamed: {total_renamed_files}")
    print(f"Total files deleted: {total_deleted_files}")
    print(f"Total remaining files: {total_remaining_files}")

if __name__ == "__main__":
    main()
