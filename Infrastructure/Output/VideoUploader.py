import os
import boto3
import subprocess
import shutil
import platform

class VideoUploader:
    def __init__(self, bucket_name="videos-somnolencia-diego", ffmpeg_path=None):
        self.bucket_name = bucket_name

        if ffmpeg_path:
            self.ffmpeg_path = ffmpeg_path
        else:
            if platform.system() == "Windows":
                self.ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
            else:
                self.ffmpeg_path = "ffmpeg" 

        self.s3 = boto3.client("s3")

    def process_video(self, input_path):
        print(f"Procesando video con ffmpeg: {input_path}")
        temp_output = "temp_output.mp4"

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", input_path,
            "-vcodec", "libx264",
            "-acodec", "aac",
            "-movflags", "+faststart",
            temp_output
        ]

        try:
            subprocess.run(cmd, check=True)
            shutil.move(temp_output, input_path)
            print("-> Video procesado correctamente.")
        except FileNotFoundError:
            print("[ERROR] ffmpeg no encontrado. Asegúrate de que esté instalado y accesible.")
            raise
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] ffmpeg falló: {e}")
            raise

    def upload_video(self, local_path, object_name):
        print(f"Subiendo a S3: {object_name}")
        self.s3.upload_file(
            Filename=local_path,
            Bucket=self.bucket_name,
            Key=object_name,
            ExtraArgs={
                "ContentType": "video/mp4"
            }
        )
        url = f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"
        print(f"-> Subido: {url}")
        return url

    def process_and_upload_all(self, video_filenames, folder="Videos"):
        urls = []
        for name in video_filenames:
            path = os.path.join(folder, name)
            self.process_video(path)
            url = self.upload_video(path, name)
            urls.append(url)
        return urls
