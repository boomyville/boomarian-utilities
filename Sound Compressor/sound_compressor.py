#==============================================================================
# Title:        Audio Speed Compressor
# Author:       Kevin Teong 
# Description:  Compress audio files by changing speed using FFmpeg.
# Usage:        python3 sound_compressor.py
# Version:      1.2
# Date:         26/04/2025
# Requirements: sudo apt install ffmpeg
# How to use:   Place the script in the same directory as the audio files
#               you want to compress. Run the script to compress the audio
#               files at the configured speed.
#               You can change the speed factor, output format, and audio 
#               file extensions in the CONFIG section below.
#==============================================================================
import os
import subprocess

# Global configuration
CONFIG = {
    'SPEED_FACTOR': 1.5,        # Speed multiplier (1.5 = 1.5x speed)
    'OUTPUT_FORMAT': 'ogg',     # Output format: 'ogg', 'mp3', 'wav', 'm4a', etc.
    'INPUT_EXTENSIONS': ['.m4a', '.mp3', '.wav', '.ogg'],  # Extensions to process
}

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

def process_audio_files():
    """
    Process audio files in the current directory using CONFIG settings.
    """
    speed_factor = CONFIG['SPEED_FACTOR']
    extensions = CONFIG['INPUT_EXTENSIONS']
    output_format = CONFIG['OUTPUT_FORMAT']
    
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
        # Replace extension with output format
        base_name = os.path.splitext(file)[0]
        output_path = os.path.join('compressed_audio', f'sped_{base_name}.{output_format}')
        compress_audio(input_path, output_path, speed_factor)
    
    print(f"Processed {len(audio_files)} files at {speed_factor}x speed to {output_format} format.")
    print(f"Input formats processed: {', '.join(ext.lstrip('.') for ext in extensions)}")

# Run the script
if __name__ == "__main__":
    process_audio_files()
