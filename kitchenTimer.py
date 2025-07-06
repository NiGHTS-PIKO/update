import tkinter as tk
import time
import threading
import winsound
import os
import sys
import datetime

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

root = tk.Tk()
icon_path = resource_path("icon.ico")
root.iconbitmap(icon_path)

class KitchenTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("よくあるキッチンタイマー")

        self.total_seconds = 0
        self.running = False
        self.paused = False
        self.count_up = False
        self.beeping = False
        self.hold_job = None
        self.hold_repeat_job = None

        self.label = tk.Label(root, text="00:00:00", font=("Arial", 48))
        self.label.pack(pady=20)

        self.clock_label = tk.Label(root, font=("Arial", 14), fg="blue", bg="lightblue")
        self.clock_label.pack()
        self.update_clock()

        self.button_refs = []
        self.create_button_row("＋1時間", 3600, "＋1分", 60, "＋1秒", 1)
        self.create_button_row("＋10時間", 36000, "＋10分", 600, "＋10秒", 10)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.reset_button = tk.Button(control_frame, text="リセット", width=10, font=("Arial", 12), command=self.reset_timer)
        self.reset_button.pack(side="left", padx=10)
        self.button_refs.append(self.reset_button)

        self.start_pause_button = tk.Button(control_frame, text="スタート／一時停止", width=16, font=("Arial", 12), command=self.start_or_pause)
        self.start_pause_button.pack(side="right", padx=10)
        self.button_refs.append(self.start_pause_button)

        # すべてのボタンに「クリックで音を止める」イベントを追加
        for btn in self.button_refs:
            btn.bind("<Button-1>", self.stop_beep_on_click, add="+")

    def stop_beep_on_click(self, event):
        if self.beeping:
            self.beeping = False
            winsound.PlaySound(None, winsound.SND_PURGE)

    def update_clock(self):
        now = datetime.datetime.now()
        weekday = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]
        formatted = now.strftime(f"%Y/%m/%d（{weekday}）%H:%M")
        self.clock_label.config(text=formatted)
        delay = (60 - now.second) * 1000
        self.root.after(delay, self.update_clock)

    def create_button_row(self, label1, sec1, label2, sec2, label3, sec3):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        self.create_hold_button(frame, label1, sec1)
        self.create_hold_button(frame, label2, sec2)
        self.create_hold_button(frame, label3, sec3)

    def create_hold_button(self, parent, text, increment):
        btn = tk.Button(parent, text=text, width=10, font=("Arial", 12))
        btn.pack(side="left", padx=5)
        self.button_refs.append(btn)

        def on_press(event):
            if self.running:
                return
            self.hold_start_time = time.time()
            self.hold_job = self.root.after(1000, lambda: self.start_repeat(increment))

        def on_release(event):
            if self.running:
                return
            if self.hold_job:
                self.root.after_cancel(self.hold_job)
                self.hold_job = None
                if time.time() - self.hold_start_time < 1:
                    self.increment_time(increment)
            if self.hold_repeat_job:
                self.root.after_cancel(self.hold_repeat_job)
                self.hold_repeat_job = None

        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    def start_repeat(self, increment):
        self.increment_time(increment)
        self.hold_repeat_job = self.root.after(200, lambda: self.start_repeat(increment))

    def increment_time(self, seconds):
        self.total_seconds += seconds
        self.update_display()

    def update_display(self):
        hrs, rem = divmod(self.total_seconds, 3600)
        mins, secs = divmod(rem, 60)
        self.label.config(text=f"{hrs:02}:{mins:02}:{secs:02}")

    def start_or_pause(self):
        if not self.running:
            self.start_timer()
        else:
            self.paused = not self.paused

    def start_timer(self):
        self.running = True
        self.paused = False
        self.count_up = self.total_seconds == 0
        threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        while self.running:
            if not self.paused:
                self.update_display()
                if self.count_up:
                    time.sleep(1)
                    self.total_seconds += 1
                else:
                    if self.total_seconds <= 3 and self.total_seconds > 0:
                        winsound.Beep(1000, 150)
                    time.sleep(1)
                    self.total_seconds -= 1
                    if self.total_seconds == 0:
                        self.update_display()
                        self.running = False
                        self.start_kaeru_song()
                        break
            else:
                time.sleep(0.1)

    def start_kaeru_song(self):
        self.beeping = True
        threading.Thread(target=self._play_kaeru_looped, daemon=True).start()

    def _play_kaeru_looped(self):
        for _ in range(5):
            if not self.beeping:
                break
            winsound.PlaySound(resource_path("kaeru.wav"), winsound.SND_FILENAME | winsound.SND_ASYNC)
            time.sleep(11.0)
        self.beeping = False

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.count_up = False
        self.total_seconds = 0
        self.beeping = False
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.update_display()

app = KitchenTimer(root)
root.mainloop()