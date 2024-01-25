import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import threading
import time


class TimerEntry:
    def __init__(self, parent, volume_var):
        self.parent = parent
        self.sound_file = filedialog.askopenfilename(title="Select an MP3 File", filetypes=[("MP3 Files", "*.mp3")])
        self.duration, self.buffer_time = self.get_time_input()  # <-- This line was modified
        minutes, seconds = divmod(self.duration, 60)
        self.time_left_var = tk.StringVar(value=f"Time Left: {minutes}m {seconds}s")

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(pady=10, fill=tk.X)

        self.label = ttk.Label(self.frame, text=self.sound_file)
        self.label.pack(side=tk.LEFT, padx=5)

        self.time_left_label = ttk.Label(self.frame, textvariable=self.time_left_var)
        self.time_left_label.pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(self.frame, text="Start", command=self.start_timer)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(self.frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.is_running = threading.Event()
        self.volume_var = volume_var

        # Add the remove button
        self.remove_btn = ttk.Button(self.frame, text="Remove", command=self.remove_timer)
        self.remove_btn.pack(side=tk.LEFT, padx=5)


    def remove_timer(self):
        self.stop_timer()  # Stop the timer if it's running
        self.frame.destroy()  # Remove the frame from the parent

    def get_time_input(self):
        dialog = TimeInputDialog(self.parent)
        self.parent.wait_window(dialog.top)
        return dialog.result

    def start_timer(self):
        self.is_running.set()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        threading.Thread(target=self.timer_thread).start()

    def stop_timer(self):
        self.is_running.clear()
        pygame.mixer.music.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def timer_thread(self):
        while self.is_running.is_set():
            for i in range(self.duration, 0, -1):
                if not self.is_running.is_set():
                    return
                minutes, seconds = divmod(i, 60)
                self.time_left_var.set(f"Time Left: {minutes}m {seconds}s")
                time.sleep(1)

            threading.Thread(target=self.play_music).start()

            # Wait for the buffer duration after playing music
            time.sleep(self.buffer_time)

            self.time_left_var.set(f"Time Left: {self.duration // 60}m {self.duration % 60}s")

    def play_music(self):
        pygame.mixer.music.load(self.sound_file)
        pygame.mixer.music.set_volume(self.volume_var.get() / 100.0)
        pygame.mixer.music.play()
        time.sleep(5)
        pygame.mixer.music.stop()


class TimeInputDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        top.title("Set Timer")

        self.label_frame = ttk.LabelFrame(top, text="Enter Time", padding=(10, 5))
        self.label_frame.pack(pady=20)

        self.minute_label = ttk.Label(self.label_frame, text="Minutes:")
        self.minute_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.minutes_entry = ttk.Entry(self.label_frame)
        self.minutes_entry.grid(row=0, column=1, padx=5, pady=5)

        self.second_label = ttk.Label(self.label_frame, text="Seconds:")
        self.second_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.seconds_entry = ttk.Entry(self.label_frame)
        self.seconds_entry.grid(row=1, column=1, padx=5, pady=5)

        self.ok_button = ttk.Button(top, text="OK", command=self.on_ok)
        self.ok_button.pack(pady=10)

        self.buffer_label = ttk.Label(self.label_frame, text="Buffer (seconds):")
        self.buffer_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.buffer_entry = ttk.Entry(self.label_frame)
        self.buffer_entry.grid(row=2, column=1, padx=5, pady=5)

        # Position the dialog relative to the parent window
        x = parent.winfo_x()
        y = parent.winfo_y()
        top.geometry("+%d+%d" % (x + 50, y + 50))

        # Default result
        self.result = 0

    def on_ok(self):
        minutes = int(self.minutes_entry.get()) if self.minutes_entry.get().strip() else 0
        seconds = int(self.seconds_entry.get()) if self.seconds_entry.get().strip() else 0
        buffer_time = int(self.buffer_entry.get()) if self.buffer_entry.get().strip() else 0

        self.result = (minutes * 60 + seconds, buffer_time)
        self.top.destroy()




class SimpleTimerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()

        self.title("Multi-Timer App")
        self.geometry('800x600')  # Set default window size

        self.volume_var = tk.IntVar(value=50)
        self.volume_label = ttk.Label(self, text="Volume:")
        self.volume_label.pack(pady=10)

        self.volume_slider = ttk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.volume_var)
        self.volume_slider.pack(pady=10, fill=tk.X)

        self.add_timer_btn = ttk.Button(self, text="Add Timer", command=self.add_timer)
        self.add_timer_btn.pack(pady=20)

    def add_timer(self):
        TimerEntry(self, self.volume_var)  # <-- This line was modified



if __name__ == "__main__":
    app = SimpleTimerApp()
    app.mainloop()
