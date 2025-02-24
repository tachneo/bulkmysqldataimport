import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox, Menu
import pymysql
import threading
import queue
import os
import time
import datetime

# Global variables
connection = None
databases = []
recent_files = []
cancel_import = False

# Color scheme
BACKGROUND_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#4a90e2"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
ERROR_COLOR = "#e74c3c"
TEXT_COLOR = "#2c3e50"

# Theme settings
current_theme = "light"

# Apply theme to widgets
def apply_theme(widget):
    if current_theme == "light":
        widget.config(bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    else:
        widget.config(bg="#2c3e50", fg="#ecf0f1")

# Database connection
def connect_to_database():
    global connection, databases
    host = host_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            autocommit=True
        )
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        database_combo['values'] = databases
        connection_status.config(text="Connected", fg=SUCCESS_COLOR)
        log_text.insert(tk.END, "Connected to database server.\n", "info")
    except Exception as e:
        connection_status.config(text="Connection Failed", fg=ERROR_COLOR)
        log_text.insert(tk.END, f"Connection error: {e}\n", "error")

# Select database from dropdown
def select_database(event):
    selected_db = database_combo.get()
    if selected_db and connection:
        try:
            connection.select_db(selected_db)
            log_text.insert(tk.END, f"Selected database: {selected_db}\n", "info")
        except Exception as e:
            log_text.insert(tk.END, f"Error selecting database: {e}\n", "error")

# Import SQL file with advanced features
def import_large_sql_file(file_path, batch_size, dry_run, log_queue, progress_var):
    global cancel_import, connection
    try:
        if not connection:
            log_queue.put(("Connection not established.", "error"))
            return
        log_queue.put(("Starting import...", "info"))
        file_size = os.path.getsize(file_path)
        processed_size = 0
        start_time = time.time()
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_command = ""
            batch = []
            while True:
                if cancel_import:
                    log_queue.put(("Import cancelled.", "warning"))
                    break
                chunk = file.read(1024)
                if not chunk:
                    break
                processed_size += len(chunk)
                sql_command += chunk
                while ';' in sql_command:
                    pos = sql_command.index(';')
                    query = sql_command[:pos].strip()
                    sql_command = sql_command[pos + 1:]
                    if query:
                        batch.append(query)
                        if len(batch) >= batch_size:
                            execute_batch(batch, dry_run, log_queue)
                            batch = []
                progress_var.set((processed_size / file_size) * 100)
                elapsed_time = time.time() - start_time
                if processed_size > 0:
                    estimated_total_time = (elapsed_time / processed_size) * file_size
                    remaining_time = estimated_total_time - elapsed_time
                    log_queue.put((f"Estimated time remaining: {str(datetime.timedelta(seconds=int(remaining_time)))}", "info"))
            if batch:
                execute_batch(batch, dry_run, log_queue)
        if not cancel_import:
            log_queue.put(("Import completed successfully.", "success"))
    except Exception as e:
        log_queue.put((f"Import failed: {e}", "error"))

# Execute batch of queries
def execute_batch(batch, dry_run, log_queue):
    if dry_run:
        for query in batch:
            log_queue.put((f"[DRY RUN] Would execute: {query[:50]}...", "info"))
    else:
        try:
            cursor = connection.cursor()
            for query in batch:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            log_queue.put((f"Batch execution error: {e}", "error"))

# Start import process
def start_import():
    global cancel_import
    cancel_import = False
    file_path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
    if not file_path:
        return
    if file_path not in recent_files:
        recent_files.append(file_path)
        update_recent_files_menu()
    batch_size = int(batch_size_entry.get())
    dry_run = dry_run_var.get()
    progress.set(0)
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Starting import...\n", "info")
    result_text.delete(1.0, tk.END)
    log_queue = queue.Queue()
    progress_var = tk.DoubleVar()
    import_thread = threading.Thread(target=import_large_sql_file, args=(file_path, batch_size, dry_run, log_queue, progress_var))
    import_thread.start()
    def check_queue():
        try:
            while True:
                message, tag = log_queue.get_nowait()
                log_text.insert(tk.END, message + "\n", tag)
                log_text.see(tk.END)
        except queue.Empty:
            pass
        progress.set(progress_var.get())
        progress_bar.update()
        if import_thread.is_alive():
            root.after(100, check_queue)
        else:
            progress.set(100)
            result_text.insert(tk.END, "Import process finished.\n")
            messagebox.showinfo("Info", "Import process completed.")
    root.after(100, check_queue)

# Cancel import
def cancel_import_process():
    global cancel_import
    cancel_import = True
    log_text.insert(tk.END, "Cancelling import...\n", "warning")

# Update recent files menu
def update_recent_files_menu():
    recent_menu.delete(0, tk.END)
    for file in recent_files:
        recent_menu.add_command(label=file, command=lambda f=file: load_file(f))

def load_file(file_path):
    log_text.insert(tk.END, f"Loaded file: {file_path}\n", "info")

# Set theme
def set_theme(theme):
    global current_theme
    current_theme = theme
    if theme == "light":
        root.config(bg=BACKGROUND_COLOR)
        for widget in root.winfo_children():
            apply_theme(widget)
    else:
        root.config(bg="#2c3e50")
        for widget in root.winfo_children():
            apply_theme(widget)

# GUI Setup
root = tk.Tk()
root.title("Advanced SQL Import Tool")
root.geometry("800x700")
root.configure(bg=BACKGROUND_COLOR)

# Menu Bar
menu_bar = Menu(root)
root.config(menu=menu_bar)
file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
recent_menu = Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Recent Files", menu=recent_menu)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
theme_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Theme", menu=theme_menu)
theme_menu.add_command(label="Light", command=lambda: set_theme("light"))
theme_menu.add_command(label="Dark", command=lambda: set_theme("dark"))

# Database Connection Frame
conn_frame = tk.LabelFrame(root, text="Database Connection", padx=10, pady=10, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
conn_frame.pack(fill=tk.X, padx=10, pady=5)
tk.Label(conn_frame, text="Host:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
host_entry = tk.Entry(conn_frame)
host_entry.grid(row=0, column=1, padx=5, pady=5)
host_entry.insert(0, "localhost")
tk.Label(conn_frame, text="User:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
user_entry = tk.Entry(conn_frame)
user_entry.grid(row=1, column=1, padx=5, pady=5)
user_entry.insert(0, "root")
tk.Label(conn_frame, text="Password:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
password_entry = tk.Entry(conn_frame, show="*")
password_entry.grid(row=2, column=1, padx=5, pady=5)
connect_button = tk.Button(conn_frame, text="Connect", command=connect_to_database, bg=PRIMARY_COLOR, fg="white")
connect_button.grid(row=3, column=0, columnspan=2, pady=10)
connection_status = tk.Label(conn_frame, text="Not Connected", fg=WARNING_COLOR, bg=BACKGROUND_COLOR)
connection_status.grid(row=4, column=0, columnspan=2)
tk.Label(conn_frame, text="Database:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
database_combo = ttk.Combobox(conn_frame, state="readonly")
database_combo.grid(row=5, column=1, padx=5, pady=5)
database_combo.bind("<<ComboboxSelected>>", select_database)

# Import Settings Frame
settings_frame = tk.LabelFrame(root, text="Import Settings", padx=10, pady=10, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
settings_frame.pack(fill=tk.X, padx=10, pady=5)
tk.Label(settings_frame, text="Batch Size:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
batch_size_entry = tk.Entry(settings_frame)
batch_size_entry.grid(row=0, column=1, padx=5, pady=5)
batch_size_entry.insert(0, "100")
dry_run_var = tk.BooleanVar()
dry_run_check = tk.Checkbutton(settings_frame, text="Dry Run", variable=dry_run_var, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
dry_run_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

# Progress Bar
progress = tk.DoubleVar()
progress_label = tk.Label(root, text="Progress:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
progress_label.pack(anchor=tk.W, padx=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=700, mode="determinate", variable=progress)
progress_bar.pack(padx=10, pady=5, fill=tk.X)

# Buttons Frame
button_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
button_frame.pack(pady=10)
import_button = tk.Button(button_frame, text="Import SQL File", command=start_import, bg=PRIMARY_COLOR, fg="white")
import_button.pack(side=tk.LEFT, padx=5)
cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_import_process, bg=WARNING_COLOR, fg="white")
cancel_button.pack(side=tk.LEFT, padx=5)
exit_button = tk.Button(button_frame, text="Exit", command=root.quit, bg=ERROR_COLOR, fg="white")
exit_button.pack(side=tk.LEFT, padx=5)

# Result and Log Boxes
result_label = tk.Label(root, text="Result:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
result_label.pack(anchor=tk.W, padx=10)
result_text = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD, bg="#ffffff", fg=TEXT_COLOR)
result_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
log_label = tk.Label(root, text="Logs:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
log_label.pack(anchor=tk.W, padx=10)
log_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD, bg="#ffffff", fg=TEXT_COLOR)
log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
log_text.tag_config("info", foreground="black")
log_text.tag_config("warning", foreground=WARNING_COLOR)
log_text.tag_config("error", foreground=ERROR_COLOR)
log_text.tag_config("success", foreground=SUCCESS_COLOR)

# Start GUI
root.mainloop()
