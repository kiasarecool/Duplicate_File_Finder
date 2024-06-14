# Duplicate Media File Finder

This script is designed to find and optionally remove duplicate media files in a specified directory. It uses the SHA-256 hash to identify duplicates based on file content, ensuring that even files with different names but the same content are detected.

## Prerequisites

- Python 3.x installed on your machine.

## Installation

1. **Clone the Repository:**
Install Required Packages:
• Python

## Usage
Set the Backup Directory:
You can set the backup_dir environment variable or enter the path manually when prompted.

## Set the Environment Variable:

export backup_dir=/path/to/extracted/files  # For Unix-based systems
set backup_dir=C:\\path\\to\\extracted\\files  # For Windows
Or Enter the Path Manually when asked:
If you do not set the environment variable, the script will prompt you to enter the path when you run it.

## Run the Duplicate Finder Script:


python find_duplicates.py
or
python find_duplicates_advanced.py
The script will:

It will ask if you want to analyze everything or just the wp-content/uploads folder.
Scan the specified directory for duplicate files.
Print out the original and duplicate files found.
Print the total number of duplicates found.
asks if you would like to delete them