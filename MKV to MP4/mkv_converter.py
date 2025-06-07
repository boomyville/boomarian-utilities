#!/usr/bin/env python3
"""
MKV to Home Assistant Compatible Format Converter

This script converts MKV files to MP4 format with H.264 encoding,
which is optimal for Home Assistant media management.

Requirements:
- ffmpeg installed on system
- Python 3.6+

Usage:
    python mkv_converter.py [input_directory] [output_directory]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mkv_conversion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("ffmpeg not found. Please install ffmpeg first.")
        return False

def get_video_info(input_file):
    """Get video information using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(input_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get video info for {input_file}: {e}")
        return None

def get_video_resolution(input_file):
    """Get video resolution using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(input_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dimensions = result.stdout.strip().split(',')
        if len(dimensions) == 2:
            width, height = int(dimensions[0]), int(dimensions[1])
            return width, height
        return None, None
    except (subprocess.CalledProcessError, ValueError):
        return None, None

def get_video_bit_depth(input_file):
    """Get video bit depth using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=pix_fmt', '-of', 'csv=p=0', str(input_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pix_fmt = result.stdout.strip()
        
        # Check if it's 10-bit format
        is_10bit = any(fmt in pix_fmt for fmt in ['10le', '10be', 'p010', 'yuv420p10'])
        
        return is_10bit, pix_fmt
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not determine bit depth for {input_file}: {e}")
        return False, "unknown"

def get_audio_streams(input_file):
    """Get information about audio streams in the file."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'a',
            '-show_entries', 'stream=index,codec_name,channels,sample_rate,bit_rate',
            '-of', 'csv=p=0', str(input_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        streams = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return [s for s in streams if s]  # Filter out empty strings
    except subprocess.CalledProcessError:
        return []

def get_appropriate_h264_level(width, height):
    """Get appropriate H.264 level based on resolution."""
    if width is None or height is None:
        return '4.0'  # Safe default
    
    # Calculate total pixels
    pixels = width * height
    
    # H.264 level guidelines
    if pixels <= 152064:  # 414x368 or smaller
        return '1.3'
    elif pixels <= 345600:  # 720x480 or smaller
        return '3.0'
    elif pixels <= 921600:  # 1280x720 or smaller
        return '3.1'
    elif pixels <= 2073600:  # 1920x1080 or smaller
        return '4.0'
    elif pixels <= 8294400:  # 3840x2160 or smaller
        return '5.1'
    else:
        return '5.2'

def convert_mkv_to_mp4(input_file, output_file, encoder='nvenc_h264', quality='medium'):
    """
    Convert MKV file to MP4 with GPU or CPU encoding.
    
    Args:
        input_file: Path to input MKV file
        output_file: Path to output MP4 file
        encoder: Encoding method ('nvenc_h264', 'nvenc_av1', 'cpu')
        quality: Conversion quality ('fast', 'medium', 'high')
    """
    
    # Check if source is 10-bit
    is_10bit, pix_fmt = get_video_bit_depth(input_file)
    
    # Get video resolution
    width, height = get_video_resolution(input_file)
    h264_level = get_appropriate_h264_level(width, height)
    
    logger.info(f"Video resolution: {width}x{height}, using H.264 level {h264_level}")
    
    # Get audio stream info
    audio_streams = get_audio_streams(input_file)
    logger.info(f"Found {len(audio_streams)} audio streams in {input_file.name}")
    if audio_streams:
        logger.info(f"Audio streams: {audio_streams}")
    
    # Base ffmpeg command
    cmd = ['ffmpeg', '-i', str(input_file)]
    
    if encoder == 'nvenc_h264':
        if is_10bit:
            logger.info(f"10-bit source detected ({pix_fmt}), using format conversion for NVENC")
            # Convert 10-bit to 8-bit for NVENC compatibility
            cmd.extend([
                '-c:v', 'h264_nvenc',
                '-profile:v', 'high',         # Use high profile for better compression
                '-level', h264_level,         # Dynamic level based on resolution
                '-pix_fmt', 'yuv420p',        # Force 8-bit output
                '-preset', 'p4',
                '-tune', 'hq',
            ])
        else:
            cmd.extend([
                '-c:v', 'h264_nvenc',
                '-profile:v', 'high',         # Use high profile for better compression
                '-level', h264_level,         # Dynamic level based on resolution
                '-preset', 'p4',
                '-tune', 'hq',
            ])
        
        # Quality settings for NVENC
        quality_settings = {
            'fast': ['-cq', '28', '-b:v', '0'],
            'medium': ['-cq', '23', '-b:v', '0'],
            'high': ['-cq', '18', '-b:v', '0']
        }
        
    elif encoder == 'nvenc_av1':
        # AV1 NVENC can handle 10-bit better
        cmd.extend([
            '-c:v', 'av1_nvenc',
            '-preset', 'p4',
            '-tune', 'hq',
        ])
        
        if is_10bit:
            # Keep 10-bit for AV1 if possible
            cmd.extend(['-pix_fmt', 'yuv420p10le'])
        
        quality_settings = {
            'fast': ['-cq', '32', '-b:v', '0'],
            'medium': ['-cq', '28', '-b:v', '0'],
            'high': ['-cq', '24', '-b:v', '0']
        }
        
    else:  # CPU encoding
        cmd.extend([
            '-c:v', 'libx264',
            '-profile:v', 'high',         # Use high profile for better compression
            '-level', h264_level,         # Dynamic level based on resolution
        ])
        
        if is_10bit:
            # For CPU encoding, we can preserve 10-bit with x265 or convert to 8-bit with x264
            logger.info(f"10-bit source detected, converting to 8-bit for x264 compatibility")
            cmd.extend(['-pix_fmt', 'yuv420p'])  # Convert to 8-bit
        
        quality_settings = {
            'fast': ['-preset', 'fast', '-crf', '28'],
            'medium': ['-preset', 'medium', '-crf', '23'],
            'high': ['-preset', 'slow', '-crf', '18']
        }
    
    # Add quality settings
    cmd.extend(quality_settings.get(quality, quality_settings['medium']))
    
    # Improved audio settings for better compatibility
    cmd.extend([
        '-c:a', 'aac',               # Audio codec (widely compatible)
        '-b:a', '192k',              # Higher bitrate for better quality
        '-ac', '2',                  # Force stereo output for compatibility
        '-ar', '48000',              # Standard sample rate
        '-movflags', '+faststart',   # Optimize for streaming
        '-map', '0:v:0',             # Map first video stream
    ])
    
    # Map audio streams more intelligently
    if audio_streams:
        cmd.extend(['-map', '0:a:0'])  # Map first audio stream
        logger.info("Mapping first audio stream")
    else:
        logger.warning(f"No audio streams found in {input_file.name}")
        # Still add audio mapping in case ffprobe missed it
        cmd.extend(['-map', '0:a?'])  # Optional audio mapping
    
    cmd.extend(['-y', str(output_file)])  # Overwrite output file
    
    try:
        bit_info = f" (10-bit source)" if is_10bit else " (8-bit source)"
        audio_info = f" with {len(audio_streams)} audio streams" if audio_streams else " (no audio detected)"
        logger.info(f"Converting {input_file.name} to {output_file.name}{bit_info}{audio_info}")
        logger.info(f"Using {encoder.upper()} encoder with {quality} quality")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Run conversion with fallback
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Successfully converted {input_file.name}")
            
            # Verify audio in output file
            output_audio_streams = get_audio_streams(output_file)
            if output_audio_streams:
                logger.info(f"Output file has {len(output_audio_streams)} audio streams")
            else:
                logger.warning(f"Output file may not have audio streams!")
            
            return True
            
        except subprocess.CalledProcessError as nvenc_error:
            error_msg = str(nvenc_error.stderr) if nvenc_error.stderr else str(nvenc_error)
            
            # Check for various NVENC failure conditions
            nvenc_failures = [
                '10 bit encode not supported',
                'No capable devices found',
                'InitializeEncoder failed',
                'invalid param',
                'Cannot load nvcuda.dll',
                'NVENC not available'
            ]
            
            if encoder.startswith('nvenc') and any(fail in error_msg for fail in nvenc_failures):
                logger.warning(f"NVENC failed for {input_file.name}, falling back to CPU encoding")
                logger.warning(f"NVENC Error: {error_msg}")
                
                # Fallback to CPU encoding
                return convert_mkv_to_mp4(input_file, output_file, 'cpu', quality)
            else:
                raise nvenc_error
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Conversion failed for {input_file.name}: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def find_mkv_files(directory):
    """Find all MKV files in the given directory."""
    mkv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mkv'):
                mkv_files.append(Path(root) / file)
    return mkv_files

def check_gpu_encoding():
    """Check if NVIDIA GPU encoding is available."""
    try:
        # Test if NVENC is available
        cmd = ['ffmpeg', '-hide_banner', '-encoders']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        nvenc_available = 'h264_nvenc' in result.stdout
        av1_nvenc_available = 'av1_nvenc' in result.stdout
        
        return nvenc_available, av1_nvenc_available
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, False

def get_user_preferences():
    """Get user preferences for conversion settings."""
    print("\n=== MKV to MP4 Converter for Home Assistant ===")
    print("This script will convert MKV files to MP4 format in the same directory.")
    print("Converted files will be renamed with '_converted' suffix.")
    print("Audio will be converted to AAC stereo at 192kbps for maximum compatibility.\n")
    
    # Check GPU encoding availability
    nvenc_available, av1_nvenc_available = check_gpu_encoding()
    
    # Get encoding preference
    print("Encoding Options:")
    if nvenc_available:
        print("1. GPU Encoding (NVIDIA NVENC H.264) - FASTEST, uses your RTX 4060")
        if av1_nvenc_available:
            print("2. GPU Encoding (NVIDIA AV1) - Modern codec, smaller files")
        print("3. CPU Encoding (x264) - Slower but maximum compatibility")
        
        while True:
            max_choice = 3 if av1_nvenc_available else 2
            choice = input(f"\nSelect encoding (1-{max_choice}) [default: 1]: ").strip()
            if choice == '' or choice == '1':
                encoder = 'nvenc_h264'
                break
            elif choice == '2' and av1_nvenc_available:
                encoder = 'nvenc_av1'
                break
            elif choice == str(max_choice) or (choice == '2' and not av1_nvenc_available):
                encoder = 'cpu'
                break
            else:
                print(f"Invalid choice. Please enter 1-{max_choice}.")
    else:
        print("1. CPU Encoding (x264) - GPU encoding not available")
        encoder = 'cpu'
        input("\nPress Enter to continue with CPU encoding...")
    
    # Get quality preference
    print(f"\nQuality Options for {encoder.upper()}:")
    if encoder.startswith('nvenc'):
        print("1. Fast (CQ 28 - quick conversion)")
        print("2. Medium (CQ 23 - balanced)")
        print("3. High (CQ 18 - best quality)")
    else:
        print("1. Fast (CRF 28 - quick conversion)")
        print("2. Medium (CRF 23 - balanced)")
        print("3. High (CRF 18 - best quality)")
    
    while True:
        choice = input("\nSelect quality (1-3) [default: 2]: ").strip()
        if choice == '' or choice == '2':
            quality = 'medium'
            break
        elif choice == '1':
            quality = 'fast'
            break
        elif choice == '3':
            quality = 'high'
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Get suffix preference
    default_suffix = "_converted"
    suffix = input(f"\nFile suffix for converted files [default: '{default_suffix}']: ").strip()
    if not suffix:
        suffix = default_suffix
    
    # Get deletion preference
    while True:
        delete_original = input("\nDelete original MKV files after conversion? (y/n) [default: n]: ").strip().lower()
        if delete_original == '' or delete_original == 'n':
            delete_original = False
            break
        elif delete_original == 'y':
            delete_original = True
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    
    return encoder, quality, suffix, delete_original

def main():
    parser = argparse.ArgumentParser(
        description='Convert MKV files to Home Assistant compatible MP4 format'
    )
    parser.add_argument(
        'input_dir',
        nargs='?',
        help='Directory containing MKV files (optional - will prompt if not provided)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Run in batch mode with default settings (no prompts)'
    )
    
    args = parser.parse_args()
    
    
    # Get input directory
    if args.input_dir:
        input_dir = Path(args.input_dir)
    else:
        input_path = input("\nEnter the directory containing MKV files: ").strip()
        input_dir = Path(input_path)
    
    # Validate input directory
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return 1
    
    # Get user preferences (unless in batch mode)
    if args.batch:
        # Check GPU availability for batch mode
        nvenc_available, _ = check_gpu_encoding()
        encoder = 'nvenc_h264' if nvenc_available else 'cpu'
        quality = 'medium'
        suffix = '_converted'
        delete_original = False
        logger.info(f"Running in batch mode with {encoder.upper()} encoder")
    else:
        encoder, quality, suffix, delete_original = get_user_preferences()
    
    # Check for ffmpeg
    if not check_ffmpeg():
        return 1
    
    # Find MKV files
    mkv_files = find_mkv_files(input_dir)
    if not mkv_files:
        logger.info("No MKV files found in the input directory.")
        return 0
    
    logger.info(f"Found {len(mkv_files)} MKV files to convert")
    logger.info(f"Encoder: {encoder.upper()}, Quality: {quality}, Suffix: {suffix}, Delete originals: {delete_original}")
    logger.info("Audio will be converted to AAC stereo at 192kbps for maximum compatibility")
    
    if not args.batch:
        proceed = input(f"\nProceed with conversion? (y/n) [default: y]: ").strip().lower()
        if proceed == 'n':
            logger.info("Conversion cancelled by user.")
            return 0
    
    # Convert files
    converted_count = 0
    failed_count = 0
    
    for mkv_file in mkv_files:
        # Create output file in same directory with suffix
        output_file = mkv_file.parent / f"{mkv_file.stem}{suffix}.mp4"
        
        # Skip if output file already exists
        if output_file.exists():
            logger.info(f"Skipping {mkv_file.name} - output file already exists")
            continue
        
        # Convert file
        if convert_mkv_to_mp4(mkv_file, output_file, encoder, quality):
            converted_count += 1
            
            # Delete original if requested
            if delete_original:
                try:
                    mkv_file.unlink()
                    logger.info(f"Deleted original file: {mkv_file.name}")
                except OSError as e:
                    logger.error(f"Failed to delete original file {mkv_file.name}: {e}")
        else:
            failed_count += 1
    
    # Summary
    logger.info(f"Conversion complete!")
    logger.info(f"Successfully converted: {converted_count} files")
    logger.info(f"Failed conversions: {failed_count} files")
    
    return 0 if failed_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
