# File Manager
 This Python-based Automated File Manager System organizes downloaded files into specific course folders based on predefined criteria. It monitors the Downloads folder for new files and automatically sorts them into designated directories for study guides, lecture notes, and lab files.
Key features are listed below:

+ File Organization: It automatically categorizes the files according to their name with an extension and puts them inside the folder associated with a course, CMSC 122, CMSC 154, CMSC 13.
+ Handling the conflict: Checks for prior existence of files so that duplication is avoided and names are appropriately modified.
+ Automatic Backup: It creates backup files of files before it is moved.
+ Zip files Content Extraction: Extract the zip files downloaded from internet to view easily.
+ Logging: Creates the Log: records actions and errors to be followed up for debugging.
+ Automatic Monitoring: uses the Watchdog library constantly monitoring the Downloads directory for new files.
  
This project is designed to automatically organize files and help students dealing with piles of coursework to efficiently manage their work.
