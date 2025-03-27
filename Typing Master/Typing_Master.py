import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np

class TypingTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Master")
        self.root.geometry("950x700+200+10")
        self.root.resizable(False, False)

        self.time_limit = 30
        self.elapsed_time = 0
        self.total_words = 0
        self.wrong_words = 0
        self.wpm = 0
        self.accuracy = 0
        self.timer_running = False
        self.timer_id = None

        self.attempts = 0
        self.used_paragraphs = []

        self.attempt_data = {
            "attempts": [],
            "wpm": [],
            "accuracy": [],
        }

        self.paragraphs = self.load_paragraphs("File.txt")
        self.setup_gui()

    def load_paragraphs(self, file_path):
        try:
            with open(file_path, "r") as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"Error: File '{file_path}' not found.")
            return ["Sample paragraph for typing test."]

    def setup_gui(self):
        main_frame = tk.Frame(self.root, bg="white", bd=4)
        main_frame.pack(fill="both", expand=True)

        frame_title = tk.Frame(main_frame, bg="orange", relief="flat")
        lbl_title = tk.Label(
            frame_title,
            text="Typing Master",
            font="algerian 35 bold",
            bg="yellow",
            fg="black",
            relief="flat",
            bd=10,
            width=30,
        )
        lbl_title.grid(row=0, column=0, pady=10)
        frame_title.grid(row=0, column=0)

        frame_test = tk.LabelFrame(main_frame, text="Test", bg="white", relief="groove")
        self.lbl_paragraph = tk.Label(
            frame_test, text="", wraplength=800, justify="left", font="Tahoma 12", bg="white"
        )
        self.lbl_paragraph.grid(row=0, column=0, pady=5)

        self.entry = tk.Text(frame_test, height=5, width=80, bd=2, font="Tahoma 12")
        self.entry.grid(row=1, column=0, pady=5, padx=5)
        self.entry.config(state="disabled")
        frame_test.grid(row=1, column=0)

        frame_output = tk.Frame(main_frame, bg="white", relief="flat")
        frame_labels = tk.Frame(frame_output, bg="white")

        self.lbl_elapsed_time = self.create_label(frame_labels, "Elapsed", 0, 0)
        self.lbl_remaining_time = self.create_label(frame_labels, "Remaining", 0, 2)
        self.lbl_wpm = self.create_label(frame_labels, "WPM", 0, 4)
        self.lbl_accuracy = self.create_label(frame_labels, "Accuracy", 0, 6)
        self.lbl_total_words = self.create_label(frame_labels, "Total", 0, 8)
        self.lbl_wrong_words = self.create_label(frame_labels, "Wrong", 0, 10)

        frame_labels.grid(row=0)
        frame_controls = tk.Frame(frame_output, bg="white")
        self.btn_start = ttk.Button(frame_controls, text="Start", command=self.start)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_reset = ttk.Button(frame_controls, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=1, padx=5)

        self.btn_show_graphs = ttk.Button(frame_controls, text="Graphs", command=self.show_graphs)
        self.btn_show_graphs.grid(row=0, column=2, padx=5)

        frame_controls.grid(row=1)
        frame_output.grid(row=2, column=0, pady=5)

        self.setup_virtual_keyboard(main_frame)

    def create_label(self, frame, text, row, column, font_size=10):
        label = tk.Label(
            frame, text=text, font=f"Tahoma {font_size} bold", fg="red", bg="white"
        )
        value = tk.Label(frame, text="0", font=f"Tahoma {font_size} bold", fg="black", bg="white")
        label.grid(row=row, column=column, padx=2, pady=2)
        value.grid(row=row, column=column + 1, padx=2, pady=2)
        return value

    def setup_virtual_keyboard(self, main_frame):
        frame_keyboard = tk.Frame(main_frame, bg="white")
        keyboard_rows = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM",
            " ",
        ]

        self.key_labels = {}
        for row_idx, row in enumerate(keyboard_rows):
            frame_row = tk.Frame(frame_keyboard, bg="white")
            for col_idx, key in enumerate(row):
                label = tk.Label(
                    frame_row,
                    text=key,
                    bg="black",
                    fg="white",
                    width=5,
                    height=2,
                    relief="groove",
                    bd=10,
                )
                label.grid(row=0, column=col_idx, padx=5, pady=5)
                self.key_labels[key] = label
            frame_row.grid(row=row_idx, column=0, pady=5)

        frame_keyboard.grid(row=3, column=0, pady=10)
        self.root.bind("<Key>", self.highlight_key)

    def highlight_key(self, event):
        key = event.char.upper()
        if key in self.key_labels:
            label = self.key_labels[key]
            label.config(bg="blue")
            self.root.after(100, lambda: label.config(bg="black"))

    def start_timer(self):
        if not self.timer_running:
            return

        if self.elapsed_time < self.time_limit:
            self.elapsed_time += 1
            self.lbl_elapsed_time.config(text=self.elapsed_time)
            self.lbl_remaining_time.config(text=self.time_limit - self.elapsed_time)
            self.timer_id = self.root.after(1000, self.start_timer)
        else:
            self.timer_running = False
            self.entry.config(state="disabled")
            self.calculate_results()
            self.attempts += 1

    def stop_timer(self):
        if self.timer_running and self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_running = False
            self.timer_id = None

    def calculate_results(self):
        para_words = self.lbl_paragraph["text"].split()
        entered_text = self.entry.get(1.0, "end-1c")
        entered_words = entered_text.split()

        self.total_words = len(entered_words)
        min_length = min(len(para_words), len(entered_words))
        self.wrong_words = sum(1 for i in range(min_length) if para_words[i] != entered_words[i])

        elapsed_time_minutes = self.elapsed_time / 60
        self.wpm = (self.total_words - self.wrong_words) / elapsed_time_minutes
        gross_wpm = self.total_words / elapsed_time_minutes
        self.accuracy = (self.wpm / gross_wpm) * 100 if gross_wpm != 0 else 0

        self.lbl_wpm.config(text=f"{self.wpm:.2f}")
        self.lbl_accuracy.config(text=f"{self.accuracy:.2f}")
        self.lbl_total_words.config(text=self.total_words)
        self.lbl_wrong_words.config(text=self.wrong_words)

        self.highlight_incorrect_words(para_words, entered_words)
        self.attempt_data["attempts"].append(self.attempts)
        self.attempt_data["wpm"].append(self.wpm)
        self.attempt_data["accuracy"].append(self.accuracy)

    def highlight_incorrect_words(self, para_words, entered_words):
        self.entry.tag_configure("incorrect", foreground="red")
        self.entry.tag_remove("incorrect", "1.0", "end")

        entered_text = self.entry.get(1.0, "end-1c")
        start_index = 0

        for i in range(min(len(para_words), len(entered_words))):
            if para_words[i] != entered_words[i]:
                word_start = entered_text.find(entered_words[i], start_index)
                word_end = word_start + len(entered_words[i])
                start_index_text = f"1.0 + {word_start} chars"
                end_index_text = f"1.0 + {word_end} chars"
                self.entry.tag_add("incorrect", start_index_text, end_index_text)
            start_index += len(entered_words[i]) + 1

    def start(self):
        self.stop_timer()
        self.reset_data()
        
        # Enable entry widget at the start
        self.entry.config(state="normal")
        self.entry.focus_set()

        if len(self.used_paragraphs) == len(self.paragraphs):
            self.used_paragraphs = []

        if not self.used_paragraphs:
            self.selected_paragraph = self.paragraphs[0]
        else:
            last_used_index = self.paragraphs.index(self.used_paragraphs[-1])
            next_index = (last_used_index + 1) % len(self.paragraphs)
            self.selected_paragraph = self.paragraphs[next_index]

        while len(self.selected_paragraph.split()) < 10:
            next_index = (next_index + 1) % len(self.paragraphs)
            self.selected_paragraph = self.paragraphs[next_index]

        self.used_paragraphs.append(self.selected_paragraph)
        self.lbl_paragraph.config(text=self.selected_paragraph)

        self.timer_running = True
        self.start_timer()

    def reset_data(self):
        self.stop_timer()
        self.elapsed_time = 0
        self.total_words = 0
        self.wrong_words = 0
        self.wpm = 0
        self.accuracy = 0

        self.lbl_elapsed_time.config(text="0")
        self.lbl_remaining_time.config(text=str(self.time_limit))
        self.lbl_wpm.config(text="0")
        self.lbl_accuracy.config(text="0")
        self.lbl_total_words.config(text="0")
        self.lbl_wrong_words.config(text="0")
        
        self.entry.config(state="normal")
        self.entry.delete(1.0, tk.END)
        self.entry.tag_remove("incorrect", "1.0", "end")

    def reset(self):
        self.stop_timer()
        self.reset_data()
        self.lbl_paragraph.config(text="")
        self.entry.config(state="disabled")  # Disable entry after reset
        self.used_paragraphs.clear()  # Clear used paragraphs to start fresh
        self.attempts = 0  # Reset attempt counter
        
        # Clear attempt data
        self.attempt_data["attempts"] = []
        self.attempt_data["wpm"] = []
        self.attempt_data["accuracy"] = []

    def show_graphs(self):
        if self.attempts < 2:
            messagebox.showwarning("Incomplete Data", "Please complete at least 2 attempts to view the graph.")
            return

        attempts = [i + 1 for i in range(self.attempts)]
        wpm = self.attempt_data["wpm"]
        accuracy = self.attempt_data["accuracy"]

        plt.figure(figsize=(8, 5))
        bar_width = 0.35
        x = np.arange(len(attempts))

        plt.bar(x - bar_width/2, wpm, width=bar_width, label='WPM', color='b')
        plt.bar(x + bar_width/2, accuracy, width=bar_width, label='Accuracy', color='r')

        plt.xlabel('Attempt Number')
        plt.ylabel('Score')
        plt.title('WPM and Accuracy Over Attempts')
        plt.xticks(x, attempts)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTest(root)
    root.mainloop()