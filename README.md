Overview
This script is designed to process image and video files within a specified directory. It can:

Clean up filenames by removing specific redundant parts.
Detect and handle filename conflicts.
Identify and list or remove duplicate files based on their hash values.
Supported File Types
The script supports the following file types:

Images: .jpg, .jpeg, .png, .gif, .webp, .bmp, .tiff, .tif, .ico, .svg
Videos: .mp4, .mov, .avi, .wmv, .flv, .mkv, .webm
Prerequisites
The script requires Python and the tqdm package for displaying progress bars. If tqdm is not installed, the script will automatically attempt to install it.

How to Use
Run the Script:
    Open a terminal and navigate to the directory containing the script.
    Run the script using 
        $ python rename_remove_duplicate.py

    When prompted, enter the path to the directory containing the files you want to process.

Rename Conflict Handling:

    Choose how to handle filename conflicts if a cleaned filename already exists:
    1: Delete the bad name file.
    2: Overwrite the existing file.
    3: Ask every time a conflict is detected.
Choose Analysis Scope:

    Choose whether to analyze the entire directory ran in or just the wp-content/uploads folder.
Choose Action for Duplicates:

    Choose whether to list duplicates or remove them:
        list: Find and list duplicates without deletion.
        remove: Find and delete duplicates.
Functions
    install_tqdm()
    Ensures that tqdm is installed. If not, it installs the package.

    hash_file(file_path)
    Generates a SHA-256 hash for a given file.

    find_duplicates(directory)
    Finds and returns a list of duplicate files in the specified directory based on file hashes.

    clean_filename(filename)
    Cleans a filename by removing specific redundant parts (_ssl=1 and ?ssl=1).

    rename_files_in_directory(directory, conflict_action)
    Renames files in the specified directory based on the cleaning criteria. Handles filename conflicts according to the chosen conflict action.

    main()
    The main function that orchestrates the renaming and duplicate detection processes.


Example Usage

Starting the Script:

        $ python script_name.py

    Please enter the path to the directory with the files to rename: /path/to/directory


    If a file with the new name already exists, what do you want to do?
    1) Just Delete the bad name file
    2) Overwrite existing file
    3) Ask every time
    Enter the number of your choice: 2

    Would you like to analyze everything or just the 'wp-content/uploads' folder? (everything/uploads): uploads

    Do you want to 'Find and List' (no actual deletion) or 'Find and Remove' (delete duplicates)? (list/remove): remove

        * Verbose output during run and will re run until 0 duplicates are found *
    Summary
        After processing, the script provides a summary including:

        Total initial files:   126058
        Total files renamed:   15269
        Total files deleted:   36095
        Total remaining files: 74667



Notes
Ensure you have a backup of your files before running the script or run the script on a backup and delete/replace uploads on live server to avoid accidental data loss. 

The script assumes that the directory structure and files are accessible and that there are no permission issues.

License
This project is licensed under the MIT License - see the LICENSE file for details.