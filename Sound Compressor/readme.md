# Sound Compressor

## Description

This Python script uses FFmpeg to compress audio files by increasing their speed, effectively reducing their duration. 

It processes all supported audio files in the current directory and saves the sped-up versions to a subdirectory named `compressed_audio`.

## Requirements

**Python:** Python 3.6 or higher.

**FFmpeg:** FFmpeg must be installed and accessible in your system's `PATH`.

**Installation (Example for Ubuntu/Debian):**

```
sudo apt update
sudo apt install ffmpeg
```

## Usage

1.  **Save the Script:** Save the script as `sound_compressor.py` (or any name you prefer with a `.py` extension).

2.  **Place Audio Files:** Place the audio files you want to compress in the same directory as the `sound_compressor.py` script. Supported audio file extensions are `.m4a`, `.mp3`, and `.wav` by default.

3.  **Run the Script:** Open a terminal or command prompt, navigate to the directory where you saved the script and audio files, and run the script:

```
python3 sound_compressor.py
```

4.  **Locate Compressed Files:** The script will create a directory named `compressed_audio` (if it doesn't already exist) in the same directory as the script. The compressed audio files will be saved here, with filenames prefixed with `sped_`.

## Customization

You can customize the script by modifying the following parameters within the `sound_compressor.py` file:

*   **Speed Factor:** Modify the `speed_factor` argument in the `process_audio_files()` function call to change the compression speed. For example, `process_audio_files(speed_factor=2.0)` will compress audio files at 2x speed. The default speed is 1.5x.

*   **Audio File Extensions:** Modify the `extensions` list in the `process_audio_files()` function to specify which audio file extensions should be processed. For example, to include `.ogg` files, use `process_audio_files(extensions=['.m4a', '.mp3', '.wav', '.ogg'])`.

## Example

1.  You have `lecture1.mp3` and `lecture2.wav` in a directory called `audio_processing`.
2.  You save `sound_compressor.py` in the same `audio_processing` directory.
3.  You open a terminal, navigate to the `audio_processing` directory:

    ```
    cd /path/to/audio_processing
    ```

4.  You run the script:

    ```
    python3 sound_compressor.py
    ```

5.  The script will process the audio files and create a directory named `compressed_audio` in `audio_processing`. Inside `compressed_audio`, you will find `sped_lecture1.mp3` and `sped_lecture2.wav`.

