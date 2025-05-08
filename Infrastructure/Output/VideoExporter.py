import cv2
import os
from datetime import datetime

class VideoExporter:
    def __init__(self, output_folder="Videos", fps=12):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

        self.fps = fps
        self.frame_size = (960, 480)
        self.video_writer = None
        self.recording = False
        self.current_filename = None

    def start_recording(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evento_somnolencia_{timestamp}.mp4"
        filepath = os.path.join(self.output_folder, filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(filepath, fourcc, self.fps, self.frame_size)
        self.recording = True
        self.current_filename = filename
        print(f"-> Grabación iniciada: {filepath}")
        return filename

    def write_frame(self, frame):
        if self.recording and self.video_writer is not None:
            self.video_writer.write(frame)

    def stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        print("-> Grabación finalizada")

    def is_recording(self):
        return self.recording
