import os
import shutil
import zipfile
import json
import hashlib
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Basically for defining paths and allowed file types
downloads_folder = config['downloads_folder']
backup_folder = config['backup_folder']
folders = config['folders']
allowed_extensions = config['allowed_extensions']

# This is to ensure destination folders and backup folder exist
for folder in folders.values():
    os.makedirs(folder, exist_ok=True)
os.makedirs(backup_folder, exist_ok=True)

# Setting up logging system
logging.basicConfig(filename='file_manager.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Helper function to compute hash of a file
def get_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Renames a file if it already exists in the destination
def handle_existing_file(dest, filename, src_path):
    file_root, file_ext = os.path.splitext(filename)
    dest_path = os.path.join(dest, filename)
    
    if os.path.exists(dest_path):
        # Checks if files are identical using hashes
        if get_file_hash(dest_path) == get_file_hash(src_path):
            logging.info(f"Identical file already exists at {dest_path}, skipping move.")
            return None  # No need to move the file
        else:
            counter = 1
            new_filename = f"{file_root}({counter}){file_ext}"
            while os.path.exists(os.path.join(dest, new_filename)):
                counter += 1
                new_filename = f"{file_root}({counter}){file_ext}"
            logging.info(f"File renamed to {new_filename} due to conflict.")
            return new_filename
    return filename

# Function to move files
def move_file(src, dest):
    try:
        filename = os.path.basename(src)
        new_filename = handle_existing_file(dest, filename, src)
        if new_filename:
            # Backs up the file before moving it. Can also be removed. This is for security purposes
            shutil.copy2(src, backup_folder)
            logging.info(f"Backed up {filename} to {backup_folder}")
            
            # Move the file
            shutil.move(src, os.path.join(dest, new_filename))
            logging.info(f"Moved {new_filename} to {dest}")
        else:
            logging.info(f"File {filename} skipped due to identical content.")
    except Exception as e:
        logging.error(f"Error moving file {src}: {e}")

# Checks if the file is valid
def is_valid_file(filename):
    return os.path.splitext(filename)[1].lower() in allowed_extensions

# Define file processing logic
def process_new_file(file_path):
    filename = os.path.basename(file_path)

    if not is_valid_file(filename):
        logging.warning(f"Invalid file type detected: {filename}, skipping...")
        return

    # Rule 1: Study Guide (CMSC 122, CMSC 154, CMSC 13). 
    if "Study Guide" in filename:
        if filename.endswith(".docx"):
            move_file(file_path, folders['cmsc_122_study_guide'])
        elif "for" in filename:
            if "CMSC 154" in filename:
                move_file(file_path, folders['cmsc_154_study_guide'])
            elif "CMSC 13" in filename:
                move_file(file_path, folders['cmsc_13_study_guide'])
    
    # Rule 2: Lecture Notes (CMSC 122 Readings)
    elif "Lecture Notes" in filename and filename.endswith(".pdf"):
        move_file(file_path, folders['cmsc_122_readings'])

    # Rule 3: Lab Files (CMSC 154 Lab files)
    elif "lab" in filename and filename.endswith(".zip"):
        move_file(file_path, folders['cmsc_154_lab_files'])
        
        # Extract zip file
        try:
            with zipfile.ZipFile(os.path.join(folders['cmsc_154_lab_files'], filename), 'r') as zip_ref:
                zip_ref.extractall(folders['cmsc_154_lab_files'])
                logging.info(f"Extracted {filename} to {folders['cmsc_154_lab_files']}")
            
            # Delete the zip file after extraction
            os.remove(os.path.join(folders['cmsc_154_lab_files'], filename))
            logging.info(f"Deleted zip file {filename}")
        except zipfile.BadZipFile:
            logging.error(f"Failed to extract {filename}: Bad Zip File")
        except Exception as e:
            logging.error(f"Error extracting {filename}: {e}")

# Handles new files
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")
            process_new_file(event.src_path)

# This sets up the observer
if __name__ == "__main__":
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=downloads_folder, recursive=False)
    
    logging.info("Monitoring Downloads folder for new files...")
    observer.start()
    
    try:
        while True:
            time.sleep(1)  # Keeps the script running
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
