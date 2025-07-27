#!/usr/bin/env python3
# Mixxx_DeDupe_GUI.py
# Created by Chris Smith & Grok
#
# MIT License
#
# Copyright (c) 2025 Chris Smith
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import os
import threading
import platform
import queue
import select
import time

class MixxxDeDupeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mixxx DeDupe GUI")
        self.root.geometry("600x700")  # Default size
        self.root.minsize(600, 700)  # Prevent resizing below 600x700

        # Output queue for real-time updates
        self.output_queue = queue.Queue()

        # Credits and License
        tk.Label(root, text="Created by Chris Smith & Grok | MIT License", font=("Arial", 10)).pack(pady=10)

        # Input File
        tk.Label(root, text="M3U8 Playlist File", font=("Arial", 10)).pack(anchor="w", padx=10)
        self.m3u8_entry = tk.Entry(root, width=50)
        self.m3u8_entry.pack(padx=10, pady=5, fill="x")
        tk.Button(root, text="Browse", command=self.browse_m3u8).pack(padx=10, pady=2)

        # Output File
        tk.Label(root, text="Output File", font=("Arial", 10)).pack(anchor="w", padx=10)
        self.output_entry = tk.Entry(root, width=50)
        self.output_entry.insert(0, "deduped_tracks.txt")
        self.output_entry.pack(padx=10, pady=5, fill="x")
        tk.Button(root, text="Browse", command=self.browse_output).pack(padx=10, pady=2)

        # Options
        tk.Label(root, text="Options", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        self.i_var = tk.BooleanVar()
        self.s_var = tk.BooleanVar()
        self.n_var = tk.BooleanVar()

        self.i_check = tk.Checkbutton(root, text="Include album and path info (-i)", variable=self.i_var, command=self.update_checkboxes)
        self.i_check.pack(anchor="w", padx=10, pady=2)
        self.s_check = tk.Checkbutton(root, text="Single-line output (-s)", variable=self.s_var)
        self.s_check.pack(anchor="w", padx=10, pady=2)
        self.n_frame = tk.Frame(root)
        self.n_check = tk.Checkbutton(self.n_frame, text="Group titles (-n)", variable=self.n_var, command=self.update_n_spinbox)
        self.n_check.pack(side="left")
        tk.Label(self.n_frame, text="Group Size:", font=("Arial", 10)).pack(side="left", padx=5)
        self.n_spinbox = tk.Spinbox(self.n_frame, from_=1, to=50, width=10, value=10, state="disabled")
        self.n_spinbox.pack(side="left", padx=5)
        self.n_frame.pack(anchor="w", padx=10, pady=5)

        # Run Button
        tk.Button(root, text="Run DeDupe", command=self.run_script, bg="green", fg="white").pack(pady=10, padx=10, fill="x")

        # Output Area with Frame for Scrollbar
        tk.Label(root, text="Output", font=("Arial", 10)).pack(anchor="w", padx=10)
        output_frame = tk.Frame(root)
        output_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.output_text = tk.Text(output_frame, height=10, width=50, state="disabled")
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)

        # Open Output File Button
        self.open_button = tk.Button(root, text="Open Output File", command=self.open_output_file, state="disabled", bg="blue", fg="white")
        self.open_button.pack(pady=10, padx=10, fill="x")

        # Start polling the output queue
        self.check_output_queue()

    def browse_m3u8(self):
        file_path = filedialog.askopenfilename(filetypes=[("M3U8 files", "*.m3u8")])
        if file_path:
            self.m3u8_entry.delete(0, tk.END)
            self.m3u8_entry.insert(0, file_path)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)

    def update_checkboxes(self):
        is_i_checked = self.i_var.get()
        self.s_check.config(state="disabled" if is_i_checked else "normal")
        self.n_check.config(state="disabled" if is_i_checked else "normal")
        self.n_spinbox.config(state="disabled" if is_i_checked or not self.n_var.get() else "normal")

    def update_n_spinbox(self):
        self.n_spinbox.config(state="normal" if self.n_var.get() and not self.i_var.get() else "disabled")

    def append_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
        self.root.update_idletasks()

    def check_output_queue(self):
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.append_output(text)
        except queue.Empty:
            pass
        self.root.after(100, self.check_output_queue)

    def run_script(self):
        def run():
            m3u8_path = self.m3u8_entry.get().strip()
            output_path = self.output_entry.get().strip()
            if not m3u8_path:
                self.output_queue.put("Error: Please select or enter a valid M3U8 playlist file.\n")
                return
            if not m3u8_path.lower().endswith('.m3u8'):
                self.output_queue.put("Error: Input file must be an .m3u8 playlist\n")
                return

            args = ["python3", "Mixxx_DeDupe.py", m3u8_path]
            if output_path:
                args.append(output_path)
            if self.i_var.get():
                args.append("-i")
            if self.s_var.get():
                args.append("-s")
            if self.n_var.get() and not self.i_var.get():
                args.extend(["-n", self.n_spinbox.get()])

            self.output_queue.put("Running script...\n")
            self.open_button.config(state="disabled")
            duplicates_found = False
            try:
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"  # Disable buffering
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffering
                    universal_newlines=True,
                    cwd=os.path.expanduser("~/Media Drive/Music/Playlists"),
                    env=env
                )

                # Non-blocking read with select for real-time output
                while True:
                    reads = [process.stdout, process.stderr]
                    readable, _, _ = select.select(reads, [], [], 0.1)
                    for stream in readable:
                        line = stream.readline()
                        if line:
                            self.output_queue.put(line)
                            if "Duplicate tracks written to" in line:
                                duplicates_found = True
                    if process.poll() is not None:
                        # Capture any remaining output
                        for line in process.stdout:
                            self.output_queue.put(line)
                            if "Duplicate tracks written to" in line:
                                duplicates_found = True
                        for line in process.stderr:
                            self.output_queue.put(line)
                        break
                    time.sleep(0.01)  # Small delay to prevent CPU overload

                # Check if output file exists and enable open button only if duplicates were found
                output_path = os.path.expanduser(output_path) if output_path else os.path.expanduser("deduped_tracks.txt")
                if duplicates_found and os.path.exists(output_path):
                    self.open_button.config(state="normal")
                else:
                    self.open_button.config(state="disabled")
            except Exception as e:
                self.output_queue.put(f"Error: {str(e)}\n")
                self.open_button.config(state="disabled")

        # Run in a separate thread to keep GUI responsive
        threading.Thread(target=run, daemon=True).start()

    def open_output_file(self):
        output_path = os.path.expanduser(self.output_entry.get().strip() or "deduped_tracks.txt")
        if os.path.exists(output_path):
            try:
                if platform.system() == "Windows":
                    os.startfile(output_path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", output_path], check=True)
                else:
                    subprocess.run(["xdg-open", output_path], check=True)
            except Exception as e:
                self.output_queue.put(f"Error opening file: {str(e)}\n")
        else:
            self.output_queue.put(f"Output file {output_path} does not exist\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = MixxxDeDupeGUI(root)
    root.mainloop()
