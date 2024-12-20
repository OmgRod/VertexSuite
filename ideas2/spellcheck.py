import tkinter as tk
from spellchecker import SpellChecker
import re

class SpellCheck:
    def __init__(self, text_widget):
        self.text = text_widget
        self.spell = SpellChecker()
        self.enabled = True
        self.forget_list = set()  # Keeps track of words the user has chosen to forget

        # Tag configurations
        self.text.tag_configure("misspelled", underline=True, foreground="red")
        self.text.tag_configure("grammar", underline=True, foreground="blue")

        # Bind right-click for spell and grammar suggestions
        self.text.bind("<Button-3>", self.show_suggestions)
        self.text.bind("<KeyRelease>", self.run)  # Re-run spellcheck on key release

    def run(self, event=None):
        print("Running spellcheck...")
        if not self.enabled:
            return

        self.text.tag_remove("misspelled", "1.0", tk.END)
        self.text.tag_remove("grammar", "1.0", tk.END)

        content = self.text.get("1.0", tk.END)
        words = re.findall(r'\b\w+\b', content)

        for word in words:
            if not word.strip():
                continue

            # Check spelling (ignore case and words in forget_list)
            lowercase_word = word.lower()
            if lowercase_word in self.spell.unknown([lowercase_word]) and lowercase_word not in self.forget_list:
                print(f"Misspelled word found: {word}")
                self.highlight_word(word, "misspelled")

            # Check grammar (basic heuristic: repeated words)
            self.check_grammar(word, content)

    def highlight_word(self, word, tag):
        start_index = "1.0"
        while True:
            start_index = self.text.search(rf"\b{re.escape(word)}\b", start_index, tk.END, nocase=True, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(word)}c"
            print(f"Highlighting word: {word} from {start_index} to {end_index}")
            self.text.tag_add(tag, start_index, end_index)
            start_index = end_index

    def check_grammar(self, word, content):
        # Basic grammar check for repeated words (e.g., "the the")
        repeated_word_pattern = rf"\b({re.escape(word)})\s+\1\b"
        start_index = "1.0"
        while True:
            start_index = self.text.search(repeated_word_pattern, start_index, tk.END, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(word) * 2 + 1}c"
            self.text.tag_add("grammar", start_index, end_index)
            start_index = end_index

    def show_suggestions(self, event):
        if not self.enabled:
            return

        # Get the word at the mouse cursor
        index = self.text.index(f"@{event.x},{event.y}")
        word_start = self.text.search(r"\b", index, backwards=True, regexp=True) or index
        word_end = self.text.search(r"\b", index, regexp=True) or index
        word = self.text.get(word_start, word_end).strip()

        if word:
            menu = tk.Menu(self.text, tearoff=0)

            # If the word is misspelled
            if word.lower() in self.spell.unknown([word.lower()]) and word.lower() not in self.forget_list:
                suggestions = self.spell.candidates(word.lower())
                if suggestions:
                    for suggestion in suggestions:
                        menu.add_command(label=suggestion, command=lambda s=suggestion: self.replace_word(word, s))
                else:
                    menu.add_command(label="No suggestions", state=tk.DISABLED)

                menu.add_separator()
                menu.add_command(label="Forget Word", command=lambda: self.forget_word(word))

            # Grammar-related suggestions (e.g., repeated words)
            if self.text.tag_ranges("grammar"):
                menu.add_command(label="Remove Redundancy", command=lambda: self.fix_grammar(word))

            menu.post(event.x_root, event.y_root)

    def replace_word(self, old_word, new_word):
        start_index = "1.0"
        while True:
            start_index = self.text.search(rf"\b{re.escape(old_word)}\b", start_index, tk.END, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(old_word)}c"
            self.text.delete(start_index, end_index)
            self.text.insert(start_index, new_word)

    def forget_word(self, word):
        self.forget_list.add(word.lower())
        self.run()  # Refresh highlights

    def fix_grammar(self, word):
        # Fix redundant repeated words
        start_index = "1.0"
        while True:
            repeated_word_pattern = rf"\b({re.escape(word)})\s+\1\b"
            start_index = self.text.search(repeated_word_pattern, start_index, tk.END, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(word) * 2 + 1}c"
            self.text.delete(f"{start_index}+{len(word)}c", end_index)
