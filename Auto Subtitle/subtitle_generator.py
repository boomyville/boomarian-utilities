#==============================================================================
# Title:        Audio to SRT Subtitle Generator
# Author:       Kevin Teong
# Description:  Generates .srt subtitle files from M4A audio files using the Whisper ASR model.
# Usage:        python3 subtitle_generator.py
# Version:      1.0
# Date:         24/01/2025
#==============================================================================

import os
import whisper
from datetime import timedelta

def generate_subtitles(audio_directory):
    """
    Generate .srt subtitle files for all M4A files in the given directory.
    
    :param audio_directory: Path to directory containing M4A files
    """
    # Load the Whisper model (can choose different sizes: tiny, base, small, medium, large)
    model = whisper.load_model('base')
    
    # Iterate through all M4A files in the directory
    for filename in os.listdir(audio_directory):
        if filename.endswith('.m4a'):
            # Full path to the audio file
            audio_path = os.path.join(audio_directory, filename)
            
            # Generate subtitles
            result = model.transcribe(audio_path, word_timestamps=True)
            
            # Generate .srt filename
            srt_filename = os.path.splitext(filename)[0] + '.srt'
            srt_path = os.path.join(audio_directory, srt_filename)
            
            # Write subtitles to .srt file
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(result['segments'], start=1):
                    # Convert timestamps to SRT format
                    start_time = format_timestamp(segment['start'])
                    end_time = format_timestamp(segment['end'])
                    
                    # Write subtitle entry
                    srt_file.write(f"{i}\n{start_time} --> {end_time}\n{segment['text'].strip()}\n\n")
            
            print(f"Generated subtitles for {filename}: {srt_filename}")

def format_timestamp(seconds):
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    :param seconds: Time in seconds
    :return: Formatted timestamp string
    """
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# Run the script in the current directory
if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    generate_subtitles(current_directory)
