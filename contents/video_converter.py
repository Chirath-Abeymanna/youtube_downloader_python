import os
import subprocess
import sys


def get_ffmpeg_path():
    # Determine the path to the FFmpeg executable
    if getattr(sys, 'frozen', False):  # If the application is bundled by PyInstaller
        application_path = os.path.dirname(sys.executable)
        path = application_path + "\contents"
        print("path is: ",path)
        ffmpeg_path = os.path.join(path, 'ffmpeg', 'ffmpeg.exe')
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        print("Application path: ",application_path)
        ffmpeg_path = os.path.join(application_path, 'ffmpeg', 'ffmpeg.exe')
    
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"FFmpeg executable not found at {ffmpeg_path}")
    
    return ffmpeg_path

def video_joiner(video_file,audio_file,output_file):
    
    ffmpeg_path = get_ffmpeg_path()

    if not os.path.isfile(ffmpeg_path):
        print(f"FFmpeg executable not found at {ffmpeg_path}")
        return
    
    try:

        # Run ffmpeg command to join video with audio
        process = subprocess.run([
            ffmpeg_path, '-i', video_file, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        
        if process.returncode == 0:
            print("Process executed successfully")
        else:
            print("Error occurred during process execution")
        
    except :
        ffmpeg_dir = os.path.join(os.path.dirname(sys.executable), 'ffmpeg')
        if not os.path.exists(ffmpeg_dir):
            id =1
            input_file = None
            os.makedirs(ffmpeg_dir)
            #download_ffmpeg(id,input_file,video_file,audio_file,output_file)

def convert_to_mp3(input_file, output_file):
    
    ffmpeg_path = get_ffmpeg_path()

    if not os.path.isfile(ffmpeg_path):
        print(f"FFmpeg executable not found at {ffmpeg_path}")
        return
    
    try:
        # Run ffmpeg command to convert video to MP3
        subprocess.run(
            [ffmpeg_path, '-i', input_file, '-vn', '-acodec', 'libmp3lame', '-q:a', '0', output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("\nConversion successful!")
    except subprocess.CalledProcessError as e:
        print("Error during conversion")
        print(e.stderr.decode())
    except Exception as e:
        print("An unexpected error occurred")
        print(e)

#For debugging
if __name__ == "__main__":
    input_file = input("Enter your file path: ")
    output_file = input("Enter your output file name: ")

    convert_to_mp3(input_file, output_file)
