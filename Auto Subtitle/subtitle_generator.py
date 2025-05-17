#==============================================================================
# Title:        Audio to SRT Subtitle Generator
# Author:       Kevin Teong
# Description:  Generates .srt subtitle files from M4A and OGG audio files using the Whisper ASR model.
# Usage:        python3 subtitle_generator.py
# Version:      1.2
# Date:         17/05/2025
#==============================================================================
import os
import warnings
import torch
import whisper
from datetime import timedelta

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.timing")
warnings.filterwarnings("ignore", category=UserWarning, module="numba.np.ufunc.parallel")

def generate_subtitles(audio_directory):
    """
    Generate .srt subtitle files for all M4A and OGG files in the given directory.
    
    :param audio_directory: Path to directory containing audio files
    """
    print("Loading Whisper model (this may take a moment)...")
    
    # Configure PyTorch to use weights_only=True to prevent future warning
    torch.serialization.set_weights_only(True)
    
    # Load the Whisper model (can choose different sizes: tiny, base, small, medium, large)
    try:
        model = whisper.load_model('base')
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Supported audio formats
    supported_formats = ['.m4a', '.ogg']
    
    # Check if there are any supported files
    audio_files = [f for f in os.listdir(audio_directory) 
                  if os.path.splitext(f)[1].lower() in supported_formats]
    
    if not audio_files:
        print(f"No supported audio files (.m4a, .ogg) found in {audio_directory}")
        return
    
    print(f"Found {len(audio_files)} audio file(s) to process.")
    
    # Iterate through all audio files in the directory
    for filename in audio_files:
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Full path to the audio file
        audio_path = os.path.join(audio_directory, filename)
        
        print(f"Processing {filename}...")
        try:
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
            
            print(f"✓ Generated subtitles for {filename}: {srt_filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

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
    print("Audio to SRT Subtitle Generator v1.2")
    print("====================================")
    
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        if not current_directory:  # If the script is run from REPL
            current_directory = os.getcwd()
            
        print(f"Searching for audio files in: {current_directory}")
        generate_subtitles(current_directory)
        print("\nDone! Check the directory for generated .srt files.")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("\nIf you're seeing CUDA/Triton warnings, don't worry - the script will still work,")
        print("but processing might be slower as it's using CPU instead of GPU acceleration.")
        print("\nCommon issues:")
        print("- Make sure you have whisper installed: pip install openai-whisper")
        print("- For faster processing, install PyTorch with CUDA if you have a compatible GPU")
