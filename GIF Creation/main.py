import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import threading
import os

class GIFMaker(tk.Tk):
    def __init__(self):
        super().__init__()

        # window setup
        self.title("gif maker tool")
        self.geometry("800x850")

        # variables
        self.video_path = ""
        self.output_path = ""
        self.frames = []
        self.preview_frame_index = 0

        # ui elements
        self.create_widgets()

    def create_widgets(self):
        # select video button
        self.select_video_button = tk.Button(self, text="select video", command=self.select_video)
        self.select_video_button.pack(pady=10)

        # video preview label
        self.preview_label = tk.Label(self, text="video preview")
        self.preview_label.pack(pady=10)

        # canvas for video preview
        self.canvas = tk.Canvas(self, width=640, height=480, bg="#eeeeee")
        self.canvas.pack(pady=10)

        # speed input
        self.speed_label = tk.Label(self, text="speed (fps)")
        self.speed_label.pack()
        self.speed_entry = tk.Entry(self)
        self.speed_entry.insert(0, "10")
        self.speed_entry.pack()

        # scale input
        self.scale_label = tk.Label(self, text="scale (e.g., 1.0 = 100%)")
        self.scale_label.pack()
        self.scale_entry = tk.Entry(self)
        self.scale_entry.insert(0, "0.5")
        self.scale_entry.pack()

        # export gif button
        self.export_button = tk.Button(self, text="export gif", command=self.export_gif)
        self.export_button.pack(pady=10)

        # progress bar
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=300, mode="indeterminate")
        self.progress.pack(pady=20)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            title="select video",
            filetypes=(
                ("mp4 files", "*.mp4"),
                ("all files", "*.*")
            )
        )
        if self.video_path:
            self.process_video()

    def process_video(self):
        if not self.video_path:
            return

        cap = cv2.VideoCapture(self.video_path)
        self.frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # convert bgr to rgb
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frames.append(frame)

        cap.release()
        self.preview_frame_index = 0
        self.animate_preview()

    def animate_preview(self):
        if not self.frames:
            return

        frame = self.frames[self.preview_frame_index]
        frame_image = Image.fromarray(frame)
        frame_image = frame_image.resize((640, 480), Image.Resampling.LANCZOS)
        frame_photo = ImageTk.PhotoImage(frame_image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_photo)
        self.canvas.image = frame_photo

        self.preview_frame_index = (self.preview_frame_index + 1) % len(self.frames)
        self.after(100, self.animate_preview)

    def export_gif(self):
        try:
            fps = int(self.speed_entry.get())
            scale = float(self.scale_entry.get())

            if not self.frames or fps <= 0 or scale <= 0:
                raise ValueError

            self.output_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=(
                    ("gif files", "*.gif"),
                    ("all files", "*.*")
                )
            )

            if not self.output_path:
                return

            self.progress.start(10)

            threading.Thread(
                target=self.create_gif, args=(fps, scale), daemon=True
            ).start()

        except ValueError:
            messagebox.showerror("error", "invalid inputs or no video selected.")

    def create_gif(self, fps, scale):
        output_frames = []

        for frame in self.frames:
            image = Image.fromarray(frame)

            new_width = int(image.width * scale)
            new_height = int(image.height * scale)

            # safety clamp to prevent zero-size errors
            if new_width < 1:
                new_width = 1
            if new_height < 1:
                new_height = 1

            image = image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

            output_frames.append(image)

        output_frames[0].save(
            self.output_path,
            save_all=True,
            append_images=output_frames[1:],
            optimize=False,
            duration=int(1000 / fps),
            loop=0
        )

        self.after(0, self.on_export_complete)

    def on_export_complete(self):
        self.progress.stop()
        messagebox.showinfo("success", "gif successfully exported!")

if __name__ == "__main__":
    app = GIFMaker()
    app.mainloop()





