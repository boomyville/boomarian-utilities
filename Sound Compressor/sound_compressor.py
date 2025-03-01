#==============================================================================
# Title:        Audio Speed Compressor
# Author:       Kevin Teong
# Description:  Compress audio files by changing speed using FFmpeg.
# Usage:        python3 sound_compressor.py
# Version:      1.0
# Date:         24/01/2025
# Requirements  sudo apt install ffmpeg
# How to use:   Place the script in the same directory as the audio files
#               you want to compress. Run the script to compress the audio
#               files at 1.5x speed.
#               You can change the speed factor and audio file extensions
#               in the script.
#==============================================================================

import os
import subprocess

def compress_audio(input_file, output_file, speed_factor=1.5):
    """
    Compress audio file using FFmpeg with speed change.
    
    :param input_file: Path to input audio file
    :param output_file: Path to output audio file
    :param speed_factor: Speed multiplier (1.5 = 1.5x speed)
    """
    # FFmpeg command to change speed while preserving pitch
    ffmpeg_cmd = [
        'ffmpeg', 
        '-i', input_file,  # Input file
        '-filter:a', f'atempo={speed_factor}',  # Audio tempo filter
        '-vn',  # No video
        '-sn',  # No subtitles
        output_file  # Output file
    ]
    
    try:
        # Run FFmpeg command
        subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.PIPE)
        print(f"Processed {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {input_file}: {e.stderr.decode()}")

def process_audio_files(speed_factor=1.5, extensions=['.m4a', '.mp3', '.wav']):
    """
    Process audio files in the current directory.
    
    :param speed_factor: Speed multiplier for audio files
    :param extensions: List of audio file extensions to process
    """
    # Get all audio files in current directory
    audio_files = [
        f for f in os.listdir('.') 
        if any(f.lower().endswith(ext) for ext in extensions)
    ]
    
    if not audio_files:
        print("No audio files found in the current directory.")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs('compressed_audio', exist_ok=True)
    
    # Process each audio file
    for file in audio_files:
        input_path = file
        output_path = os.path.join('compressed_audio', f'sped_{file}')
        compress_audio(input_path, output_path, speed_factor)
    
    print(f"Processed {len(audio_files)} files at {speed_factor}x speed.")

# Run the script
if __name__ == "__main__":
    process_audio_files()
