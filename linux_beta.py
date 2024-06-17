import os
import hashlib
import re
import sys

try:
    import tqdm
except ImportError:
    print("tqdm module is not installed. Please install it manually using 'pip install tqdm'.")
    sys.exit(1)

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
                            action = input("The file {} already exists. Do you want to overwrite it? (yes/no): ".format(new_file_path)).strip().lower()
                            if action == 'yes':
                                os.rename(old_file_path, new_file_path)
                                print('Overwritten: {} -> {}'.format(old_file_path, new_file_path))
                                renamed_files += 1
                            else:
                                print('Skipped renaming: {}'.format(old_file_path))
                        elif conflict_action == 2:  # Overwrite
                            os.rename(old_file_path, new_file_path)
                            print('Overwritten: {} -> {}'.format(old_file_path, new_file_path))
                            renamed_files += 1
                        elif conflict_action == 1:  # Skip renaming
                            print('Skipped renaming: {}'.format(old_file_path))
                    elif new_file_path != old_file_path:
                        os.rename(old_file_path, new_file_path)
                        print('Renamed: {} -> {}'.format(old_file_path, new_file_path))
                        renamed_files += 1
                    
                    pbar.update(1)

    return total_files, renamed_files

def main():
    backup_dir = input("Please enter the path to the directory with the files to rename: ")
    if not os.path.exists(backup_dir):
        print("The path {} does not exist. Please check and try again.".format(backup_dir))
       
