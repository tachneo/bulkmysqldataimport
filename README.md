# SQL Import Tool

A Python-based GUI tool designed to import large `.sql` files into a MySQL database efficiently. Built with `tkinter`, this tool is user-friendly and handles large file imports by processing the SQL file in chunks.

## Features

- **Chunk-Based File Processing:**
  Efficiently reads and executes SQL commands line by line, suitable for handling large files without memory overload.
  
- **Progress Bar:**
  Displays real-time progress of the import process based on the number of lines processed.

- **Connection Status:**
  Shows the current database connection status, helping users quickly identify connectivity issues.

- **Result Box:**
  Summarizes the outcome of the import process, confirming successful completion or highlighting issues.

- **Log Box:**
  Provides detailed logs of the import process, including query execution and any errors encountered.

- **User-Friendly Interface:**
  Intuitive design with a simple and clear layout.

## Prerequisites

- Python 3.x
- `pymysql` package (Install using `pip install pymysql`)

## Installation

How to Use
Launch the tool.
Click on "Import SQL File" to select a .sql file from your system.
Monitor the import progress via the Progress Bar.
View the detailed logs in the Log Box and the summary in the Result Box.
Exit the application by clicking the "Exit" button.
Screenshots

Database Configuration
Ensure that your MySQL database credentials are correctly set in the script:

python
Copy
Edit
connection = pymysql.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="your_database",
    autocommit=True
)
Replace your_username, your_password, and your_database with your MySQL credentials.

Limitations
Only supports .sql files.
Designed for MySQL databases.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributions
Contributions, issues, and feature requests are welcome! Feel free to check out the issues page.

javascript
Copy
Edit

Replace placeholders like `your-r

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/sql-import-tool.git
   cd sql-import-tool
