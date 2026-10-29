import os
import zipfile
import tempfile
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup

def run_injection(epub_path, poison_path, output_path, status_var, inject_button):
    if not epub_path or not poison_path or not output_path:
        messagebox.showerror("Error", "Please select all required files.")
        return

    # Disable button and update status to show work is happening
    inject_button.config(state="disabled")
    status_var.set("Status: Processing ePub archive...")

    def background_task():
        try:
            # 1. Read the poison content
            with open(poison_path, 'r', encoding='utf-8') as f:
                poison_content = f.read()

            status_var.set("Status: Extracting ePub contents...")
            # 2. Extract ePub into a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(epub_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # 3. Find all XHTML / HTML content files
                xhtml_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.xhtml', '.html', '.htm')):
                            xhtml_files.append(os.path.join(root, file))

                if not xhtml_files:
                    raise ValueError("No HTML/XHTML files found inside the ePub container.")

                status_var.set("Status: Scanning paragraphs (<p> tags)...")
                # 4. Parse files and gather all <p> tags
                all_paragraphs = []
                file_soup_map = {}

                for file_path in xhtml_files:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                    file_soup_map[file_path] = soup
                    for p in soup.find_all('p'):
                        all_paragraphs.append((file_path, p))

                if not all_paragraphs:
                    raise ValueError("No <p> tags found in any of the ePub documents.")

                status_var.set("Status: Injecting content randomly...")
                # 5. Pick a random paragraph and inject
                chosen_file, chosen_p = random.choice(all_paragraphs)
                soup = file_soup_map[chosen_file]
                
                poison_soup = BeautifulSoup(poison_content, 'html.parser')
                chosen_p.insert_after(poison_soup)

                with open(chosen_file, 'w', encoding='utf-8') as f:
                    f.write(str(soup))

                status_var.set("Status: Repackaging ePub archive...")
                # 6. Repackage into a new ePub file
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    mimetype_path = os.path.join(temp_dir, 'mimetype')
                    if os.path.exists(mimetype_path):
                        zip_out.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
                    
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file == 'mimetype':
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_out.write(file_path, arcname)

            status_var.set("Status: Done!")
            messagebox.showinfo("Success!", f"Successfully created:\n{output_path}")
        except Exception as e:
            status_var.set("Status: Failed.")
            messagebox.showerror("An Error Occurred", str(e))
        finally:
            # Re-enable the button when finished
            inject_button.config(state="normal")

    # Start the task in a background thread so the GUI stays responsive
    threading.Thread(target=background_task, daemon=True).start()

# --- GUI Setup ---
def create_gui():
    root = tk.Tk()
    root.title("ePub Content Injector")
    root.geometry("450x370")
    root.resizable(False, False)

    # Variables
    epub_var = tk.StringVar()
    poison_var = tk.StringVar()
    output_var = tk.StringVar(value="output_infected.epub")
    status_var = tk.StringVar(value="Status: Ready")

    def select_epub():
        filename = filedialog.askopenfilename(filetypes=[("ePub files", "*.epub"), ("All files", "*.*")])
        if filename:
            epub_var.set(filename)

    def select_poison():
        filename = filedialog.askopenfilename(filetypes=[("Text/HTML files", "*.txt *.html"), ("All files", "*.*")])
        if filename:
            poison_var.set(filename)

    # Layout elements
    tk.Label(root, text="Input ePub File:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 0))
    tk.Entry(root, textvariable=epub_var, width=50).pack(padx=20, pady=2)
    tk.Button(root, text="Browse ePub...", command=select_epub).pack(anchor="e", padx=20, pady=2)

    tk.Label(root, text="Poison File (HTML/TXT):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
    tk.Entry(root, textvariable=poison_var, width=50).pack(padx=20, pady=2)
    tk.Button(root, text="Browse Poison File...", command=select_poison).pack(anchor="e", padx=20, pady=2)

    # Inject Button reference saved for disabling/enabling
    inject_btn = tk.Button(
        root, text="Inject and Save ePub", bg="#28a745", fg="white", font=("Arial", 11, "bold"),
        command=lambda: run_injection(epub_var.get(), poison_var.get(), output_var.get(), status_var, inject_btn)
    )
    inject_btn.pack(pady=15)

    # Status Bar Label
    status_label = tk.Label(root, textvariable=status_var, font=("Arial", 9, "italic"), fg="gray")
    status_label.pack(side="bottom", anchor="w", padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()