import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
from threading import Thread
from preferences import Preferences
from spellcheck import SpellCheck

AUTOSAVE_INTERVAL = 10

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Vertex Ideas")
        self.root.geometry("800x600")

        # Set logo
        self.root.iconphoto(False, tk.PhotoImage(file="logo.png"))

        # Editor state
        self.file_path = None
        self.settings = {
            "autosave_enabled": True,
            "spellcheck_enabled": True,
            "font_size": 12,
        }

        # Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.create_menus()

        # Text widget
        self.text = tk.Text(self.root, undo=True, wrap="word", font=("Consolas", self.settings["font_size"]))
        self.text.pack(expand=True, fill=tk.BOTH)

        # Scrollbar
        scrollbar = tk.Scrollbar(self.text, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Spellcheck and syntax highlighting
        self.spellcheck = SpellCheck(self.text)
        self.text.bind("<KeyRelease>", self.on_key_release)

        # Autosave thread
        self.autosave_thread = Thread(target=self.autosave, daemon=True)
        self.autosave_thread.start()

    def create_menus(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Preferences", command=self.open_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

    def new_file(self):
        if not self.confirm_discard_changes():
            return
        self.text.delete(1.0, tk.END)
        self.file_path = None
        self.root.title("Vertex Ideas - New File")

    def open_file(self):
        if not self.confirm_discard_changes():
            return
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, file.read())
            self.file_path = file_path
            self.root.title(f"Vertex Ideas - {os.path.basename(file_path)}")

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(self.text.get(1.0, tk.END))
            messagebox.showinfo("Save", "File saved successfully!")
        else:
            self.save_as()

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.save_file()
            self.root.title(f"Vertex Ideas - {os.path.basename(file_path)}")

    def on_key_release(self, event=None):
        if self.settings["spellcheck_enabled"]:
            self.spellcheck.run()
        self.syntax_highlight()

    def syntax_highlight(self):
        self.text.tag_remove("keyword", "1.0", tk.END)
        self.text.tag_remove("string", "1.0", tk.END)
        self.text.tag_remove("comment", "1.0", tk.END)

        keywords = r"\b(def|class|if|else|elif|while|for|return|import|from|with|as|try|except|finally|break|continue|lambda)\b"
        strings = r"(['\"])(.*?)(\1)"
        comments = r"#.*"

        patterns = [
            ("keyword", keywords, "blue"),
            ("string", strings, "green"),
            ("comment", comments, "gray"),
        ]

        for tag, pattern, color in patterns:
            start_index = "1.0"
            while True:
                start_index = self.text.search(pattern, start_index, tk.END, regexp=True)
                if not start_index:
                    break
                end_index = self.text.index(f"{start_index}+{len(self.text.get(start_index))}c")
                self.text.tag_add(tag, start_index, end_index)
                start_index = end_index
            self.text.tag_configure(tag, foreground=color)

    def confirm_discard_changes(self):
        if self.text.edit_modified():
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Save before continuing?")
            if response:  # Save and continue
                self.save_file()
            return response is not None
        return True

    def autosave(self):
        while True:
            time.sleep(AUTOSAVE_INTERVAL)
            if self.settings["autosave_enabled"] and self.file_path:
                with open(self.file_path, "w", encoding="utf-8") as file:
                    file.write(self.text.get(1.0, tk.END))

    def open_preferences(self):
        Preferences(self.root, self.settings, self.apply_preferences)

    def apply_preferences(self):
        self.text.config(font=("Consolas", self.settings["font_size"]))
        self.spellcheck.enabled = self.settings["spellcheck_enabled"]


