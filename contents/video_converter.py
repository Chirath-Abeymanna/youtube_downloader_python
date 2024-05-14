import subprocess


def convert_to_mp3(input_file, output_file):
        try:
            # Run ffmpeg command to convert video to MP3
            subprocess.run(['ffmpeg', '-i', input_file, '-vn', '-acodec', 'libmp3lame', '-q:a', '0', output_file])
            print("\nConversion successful!")
        except Exception as e:
            print(f"An error occurred: {e}")

