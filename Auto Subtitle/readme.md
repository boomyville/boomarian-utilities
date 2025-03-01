
## Description

This Python script automates the creation of `.srt` (SubRip Subtitle) files from `.m4a` audio files. It utilises the Whisper automatic speech recognition (ASR) model to transcribe the audio and then formats the transcription into the standard SRT format. The script processes all `.m4a` files found in the current directory.

## Rationale

After watching f4mi's video on AI subtitle poisoning (https://www.youtube.com/watch?v=NEDFUjqA1s8), I was for some reason compelled to add subtitles to videos I made. In that video, she mentioned the use of Whisper and how it was used by content thieves to extract voice data from YouTube videos which could then be processed through natural language models to produce AI-generated videos using essentially stolen content. Whilst her video whilst primarily about combatting a different method of video content theft (the use of subtitles which already had the text of the video), it did make me think about the potential for Whisper to be used for good. So this script was born and whilst its not perfect, it's pretty good with converting speech to text and then converting that text to subtitles.

## Requirements

*   **Python:** Python 3.6 or higher.
*   **Whisper:** The `openai-whisper` package must be installed.

    ```
    pip install -U openai-whisper
    ```

## Usage

1.  **Save the Script:** Save the script as `subtitle_generator.py` (or any name you prefer with a `.py` extension).

2.  **Place Audio Files:** Put the `.m4a` audio files you want to process in the same directory as the `subtitle_generator.py` script.

3.  **Run the Script:** Open a terminal or command prompt, navigate to the directory where you saved the script and audio files, and run the script:

    ```
    python3 subtitle_generator.py
    ```

4.  **Locate Subtitle Files:** The script will generate `.srt` files in the same directory as the audio files. The SRT filenames will match the audio filenames (e.g., `audio.m4a` will produce `audio.srt`).

## Customization

*   **Whisper Model:** The script currently uses the `"base"` Whisper model. You can change this to `"tiny"`, `"small"`, `"medium"`, or `"large"` by modifying the `model = whisper.load_model('base')` line. Note that larger models will produce more accurate transcriptions but require more computational resources and time.

## Example

1.  You have `lecture1.m4a` and `interview.m4a` in a directory called `audio_recordings`.
2.  You save `subtitle_generator.py` in the same `audio_recordings` directory.
3.  You open a terminal, navigate to the `audio_recordings` directory:

    ```
    cd /path/to/audio_recordings
    ```

4.  You run the script:

    ```
    python3 subtitle_generator.py
    ```

5.  The script will process the audio files and create `lecture1.srt` and `interview.srt` in the `audio_recordings` directory.

## Notes

*   Use this with your favourite video editor (I use ShotCut) to add subtitles to your videos!
