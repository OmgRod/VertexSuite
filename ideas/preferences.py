import tkinter as tk
from tkinter import ttk, colorchooser
import configparser

class Preferences:
    def __init__(self, root, settings, apply_callback):
        self.root = tk.Toplevel(root)
        self.root.title("Preferences")
        self.settings = settings
        self.apply_callback = apply_callback

        # Load config settings
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Autosave setting
        self.autosave_var = tk.BooleanVar(value=self.settings["autosave_enabled"])
        tk.Checkbutton(self.root, text="Enable Autosave", variable=self.autosave_var).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Spellcheck setting
        self.spellcheck_var = tk.BooleanVar(value=self.settings["spellcheck_enabled"])
        tk.Checkbutton(self.root, text="Enable Spellcheck", variable=self.spellcheck_var).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        # Font size setting
        tk.Label(self.root, text="Font Size:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.font_size_var = tk.IntVar(value=self.settings["font_size"])
        font_size_spinbox = tk.Spinbox(self.root, from_=8, to=32, textvariable=self.font_size_var, width=5)
        font_size_spinbox.grid(row=2, column=1, padx=10, pady=5)

        # Color settings
        self.misspelled_color = tk.StringVar(value=self.settings.get("misspelled_color", "red"))
        self.grammar_color = tk.StringVar(value=self.settings.get("grammar_color", "blue"))

        tk.Label(self.root, text="Misspelled Word Color:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        tk.Button(self.root, text="Choose Color", command=self.choose_misspelled_color).grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Grammar Error Color:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        tk.Button(self.root, text="Choose Color", command=self.choose_grammar_color).grid(row=4, column=1, padx=10, pady=5)

        # Buttons
        ttk.Button(self.root, text="Apply", command=self.apply_settings).grid(row=5, column=0, padx=10, pady=10, sticky="e")
        ttk.Button(self.root, text="Close", command=self.root.destroy).grid(row=5, column=1, padx=10, pady=10, sticky="w")

    def apply_settings(self):
        self.settings["autosave_enabled"] = self.autosave_var.get()
        self.settings["spellcheck_enabled"] = self.spellcheck_var.get()
        self.settings["font_size"] = self.font_size_var.get()
        self.settings["misspelled_color"] = self.misspelled_color.get()
        self.settings["grammar_color"] = self.grammar_color.get()

        # Save to config file
        self.save_settings_to_config()

        self.apply_callback()
        self.root.destroy()

    def choose_misspelled_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.misspelled_color.set(color)

    def choose_grammar_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.grammar_color.set(color)

    def save_settings_to_config(self):
        # Ensure config file exists
        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")

        self.config.set("Settings", "autosave_enabled", str(self.settings["autosave_enabled"]))
        self.config.set("Settings", "spellcheck_enabled", str(self.settings["spellcheck_enabled"]))
        self.config.set("Settings", "font_size", str(self.settings["font_size"]))
        self.config.set("Settings", "misspelled_color", self.settings["misspelled_color"])
        self.config.set("Settings", "grammar_color", self.settings["grammar_color"])

        with open("config.ini", "w") as configfile:
            self.config.write(configfile)
