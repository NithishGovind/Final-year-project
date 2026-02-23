import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class FeedbackWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Feedback")
        self.root.geometry("520x320")
        self.root.configure(bg="#F5F5F7")  # Apple-like light gray background

        # Main container frame (adds padding)
        self.container = tk.Frame(self.root, bg="#F5F5F7")
        self.container.pack(expand=True, fill="both", padx=20, pady=20)

        self.text_widget = ScrolledText(
            self.container,
            wrap=tk.WORD,
            font=("san francisco", 15),  # Clean Apple-style font
            bg="#110505",
            fg="#F0F0F0",  # Soft black (Apple style)
            bd=0,
            highlightthickness=0,
            relief="flat",
            padx=15,
            pady=15
        )

        self.text_widget.pack(expand=True, fill="both")

        self.text_widget.insert(
            tk.END,
            "Make a move to receive feedback...\n"
        )

        self.text_widget.config(state=tk.DISABLED)

    def update_text(self, new_text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, new_text)
        self.text_widget.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()