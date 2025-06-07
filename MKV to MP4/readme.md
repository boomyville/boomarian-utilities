# MKV to Home Assistant Compatible Format Converter

A Python script that converts MKV files to MP4 format with H.264 encoding, optimized for Home Assistant media management. Features GPU acceleration for faster conversions and intelligent handling of 10-bit video sources. I made it for converting Bluey episodes for my son...

## Features

- **GPU Acceleration**: NVIDIA NVENC H.264 and AV1 encoding support
- **CPU Fallback**: Automatic fallback to CPU encoding when GPU encoding fails
- **10-bit Video Support**: Intelligent handling of 10-bit video sources
- **Home Assistant Optimized**: Output format optimized for streaming and compatibility
- **Batch Processing**: Convert multiple files with a single command
- **Interactive Mode**: User-friendly prompts for encoding preferences
- **Logging**: Comprehensive logging to file and console
- **Smart Detection**: Automatic GPU capability detection

## Requirements

### Software Requirements
- Python 3.6 or higher
- FFmpeg with NVENC support (for GPU acceleration)

### Hardware Requirements

#### GPU Support (Optional but Recommended)
**NVIDIA GPUs with NVENC Support:**
- **RTX Series**: RTX 4090, RTX 4080, RTX 4070, RTX 4060, RTX 3090, RTX 3080, RTX 3070, RTX 3060, RTX 2080, RTX 2070, RTX 2060
- **GTX Series**: GTX 1660 Ti, GTX 1660 Super, GTX 1660, GTX 1650 Super, GTX 1650
- **Quadro Series**: Most modern Quadro cards
- **Tesla Series**: Tesla T4, Tesla V100, and newer

#### CPU Support
**Any modern CPU will work**, including:
- Intel Core series (i3, i5, i7, i9) - 4th generation and newer recommended
- AMD Ryzen series (3, 5, 7, 9) - all generations
- Intel Xeon processors
- AMD Threadripper processors

**CPU Performance Notes**:
- More cores = faster encoding when using CPU mode
- Intel Quick Sync Video (QSV) is not currently supported but could be added
- ARM processors (Apple Silicon, Raspberry Pi) will work but may be slower

## Installation

1. **Install Python 3.6+**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip
   
   # macOS (with Homebrew)
   brew install python3
   
   # Windows: Download from python.org
   ```

2. **Install FFmpeg with NVENC support**
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # macOS (with Homebrew)
   brew install ffmpeg
   
   # Windows: Download from https://ffmpeg.org/download.html
   # Make sure to get a build with NVENC support
   ```

3. **Download the script**
   ```bash
   curl -O https://raw.githubusercontent.com/yourusername/mkv-converter/main/mkv_converter.py
   chmod +x mkv_converter.py
   ```

## Usage

### Interactive Mode (Recommended)
```bash
python3 mkv_converter.py
```
The script will prompt you for:
- Input directory containing MKV files
- Encoding method (GPU/CPU)
- Quality settings
- File naming preferences
- Whether to delete original files

### Command Line Mode
```bash
# Convert files in specific directory
python3 mkv_converter.py /path/to/mkv/files

# Batch mode with default settings (no prompts)
python3 mkv_converter.py /path/to/mkv/files --batch
```

### Arguments
- `input_dir` (optional): Directory containing MKV files
- `--batch`: Run in batch mode with default settings

## Encoding Options

### GPU Encoding (NVIDIA NVENC)
**H.264 NVENC** (Recommended for compatibility)
- Fastest conversion speed
- Excellent Home Assistant compatibility
- Good quality-to-filesize ratio
- Supports RTX 4060 and all NVENC-capable GPUs

**AV1 NVENC** (For newer GPUs)
- Smaller file sizes
- Better compression efficiency
- Requires RTX 40 series or newer for optimal performance

### CPU Encoding
**x264** (Universal compatibility)
- Works on any CPU
- Slower than GPU encoding
- Maximum compatibility
- Better quality per bitrate (but much slower)

## Quality Settings

| Setting | GPU (CQ Value) | CPU (CRF Value) | Use Case |
|---------|----------------|-----------------|----------|
| Fast    | CQ 28          | CRF 28          | Quick conversion, larger files |
| Medium  | CQ 23          | CRF 23          | Balanced quality/size (default) |
| High    | CQ 18          | CRF 18          | Best quality, slower conversion |

## File Handling

- **Input**: Recursively scans directory for `.mkv` files
- **Output**: Creates MP4 files in the same directory as source files
- **Naming**: Adds suffix to converted files (default: `_converted`)
- **Preservation**: Original files preserved by default (optional deletion)
- **Streaming**: Output optimized with `faststart` flag for immediate playback

## 10-bit Video Support

The script automatically detects and handles 10-bit video sources:

- **NVENC H.264**: Converts 10-bit to 8-bit (NVENC limitation)
- **NVENC AV1**: Preserves 10-bit when possible
- **CPU x264**: Converts 10-bit to 8-bit for compatibility
- **CPU x265**: Could preserve 10-bit (not currently implemented)

## Logging

The script creates detailed logs:
- **Console Output**: Real-time progress and status
- **Log File**: `mkv_conversion.log` with full conversion details
- **Error Reporting**: Detailed error messages for troubleshooting

## Home Assistant Integration

Converted files are optimized for Home Assistant:
- **Container**: MP4 for universal compatibility
- **Video Codec**: H.264 (widely supported)
- **Audio Codec**: AAC at 128kbps
- **Streaming**: FastStart enabled for immediate playback
- **Compatibility**: Works with all Home Assistant media players

## Troubleshooting

### GPU Encoding Issues
```bash
# Check if NVENC is available
ffmpeg -encoders | grep nvenc

# Check GPU compatibility
nvidia-smi
```

### Common Solutions
- **"NVENC not found"**: Install GPU drivers or use CPU encoding
- **"10 bit encode not supported"**: Script automatically falls back to CPU
- **Permission errors**: Check file/directory permissions
- **Out of memory**: Reduce quality setting or use CPU encoding

## Performance Expectations

### RTX 4060 (Example GPU)
- **4K MKV**: ~2-4x real-time speed
- **1080p MKV**: ~5-10x real-time speed
- **720p MKV**: ~10-20x real-time speed

### Modern CPU (8-core example)
- **4K MKV**: ~0.5-1x real-time speed
- **1080p MKV**: ~1-2x real-time speed
- **720p MKV**: ~2-4x real-time speed

## Contributing

Feel free to submit issues and pull requests for:
- Additional codec support (HEVC, AV1)
- Intel Quick Sync Video support
- AMD GPU support (VCE)
- Additional quality presets
- UI improvements

## License

This project is open source. Please check the repository for license details.

## Changelog

### Version 1.0
- Initial release
- NVENC H.264 and AV1 support
- 10-bit video detection and handling
- Interactive and batch modes
- Comprehensive logging
- Home Assistant optimisation
