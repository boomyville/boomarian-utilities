# Sound Compressor

## Description

This Python script uses FFmpeg to compress audio files by increasing their speed, effectively reducing their duration. 

It processes all supported audio files in the current directory and saves the sped-up versions to a subdirectory named `compressed_audio`.

## Rationale

I made this to help with recording videos for university assignments. Many of my subjects now require code / essay to have a video component included where the submitter provides a narrated slideshow / presentation / screen recording of assignment. The issue is that many of these submissions have a very strict time limit and it can be difficult to fit all your ideas and explanations into such a tight timeframe. My process of creating such videos generally involved me writing a script (much easier for me to read something prepared than try to talk off the cuff - not to mention heavily reduces the amount of retakes when it comes to recording), and then recording myself reading the script (usually in chunks in case I make a mistake). I would then stitch up the audio and have it play back whilst I screen recorded my presentation (whether it was me flicking through the slideshow or me navigating to different sections of code in VS studio). Finally, I would use my video editing software of choice to combine the audio and video clips into one nice package and then inevitably find out that my video is way too long.

By using this python script, I could shorten the duration of audio clips which allowed me to essentially cram more information within a set time frame. Obviously, there are limits to how fast a human can listen but if you need to shave up to 50% off your audio clips, then this is a good place to start. And yes, Audacity exists and can do the same thing but this script is much easier with a dozen audio files.

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

