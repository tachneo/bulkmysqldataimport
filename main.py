import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import pymysql


def import_large_sql_file():
    file_path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
    if not file_path:
        return

    try:
        # Connect to the database
        connection_status.set("Connecting to database...")
        connection = pymysql.connect(
            host="localhost",
            user="root", 
            password="",
            database="nameyourdatabse",
            autocommit=True
        )
        connection_status.set("Connected to database.")
        cursor = connection.cursor()
    except Exception as e:
        connection_status.set("Failed to connect to database.")
        log_text.insert(tk.END, f"Connection error: {e}\n")
        return

    progress.set(0)
    progress_bar.update()

    try:
        log_text.insert(tk.END, f"Starting import of SQL file: {file_path}\n")
        total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_command = ""
            for idx, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith("--") or line.startswith("/*"):
                    continue
                sql_command += line

                if sql_command.endswith(";"):
                    try:
                        cursor.execute(sql_command)
                        sql_command = ""
                    except Exception as query_error:
                        log_text.insert(tk.END, f"Error executing query: {query_error}\n")
                        sql_command = ""

                progress.set((idx / total_lines) * 100)
                progress_bar.update()

        log_text.insert(tk.END, "Import completed successfully.\n")
        result_text.insert(tk.END, "Data imported into the database successfully.\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error during import: {e}\n")
    finally:
        cursor.close()
        connection.close()
        connection_status.set("Disconnected from database.")


# Set up the GUI
root = tk.Tk()
root.title("SQL Import Tool")
root.geometry("600x400")

# Progress bar
progress = tk.DoubleVar()
progress_label = tk.Label(root, text="Progress:")
progress_label.pack(anchor=tk.W, padx=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", variable=progress)
progress_bar.pack(padx=10, pady=5)

# Connection status
connection_status = tk.StringVar(value="Not connected")
connection_label = tk.Label(root, textvariable=connection_status, fg="blue")
connection_label.pack(anchor=tk.W, padx=10)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

import_button = tk.Button(button_frame, text="Import SQL File", command=import_large_sql_file)
import_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="Exit", command=root.quit)
exit_button.pack(side=tk.LEFT, padx=5)

# Result box
result_label = tk.Label(root, text="Result:")
result_label.pack(anchor=tk.W, padx=10)
result_text = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
result_text.pack(padx=10, pady=5)

# Log box
log_label = tk.Label(root, text="Logs:")
log_label.pack(anchor=tk.W, padx=10)
log_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD)
log_text.pack(padx=10, pady=5)

root.mainloop()
