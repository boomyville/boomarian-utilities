# The Boomarian Utilities
A collection of utilities built by me to help with University studies and general computing (such as file conversion)


## Sound compressor

This Python script compresses audio files by increasing their speed using FFmpeg, which I developed to address time constraints in narrated video assignments. It processes .m4a, .mp3, and .wav files in the current directory, saving sped-up versions to a compressed_audio subdirectory. FFmpeg and Python 3.6+ are required. To use, place the script with audio files, run python3 sound_compressor.py, and find compressed files in the output directory. Customise the script's speed factor and file extensions to alter the compression speed and audio files. 

## Auto subtitles

This Python script creates .srt subtitle files from .m4a audio using the Whisper ASR model. It processes all .m4a files in the script's directory. Requires Python 3.6+ and openai-whisper (pip install -U openai-whisper). To use, save the script, place .m4a files in its directory, run python3 subtitle_generator.py, and find .srt files in the same location. Customise the Whisper model for transcription accuracy by modifying model = whisper.load_model('base') to smaller or larger models. Use your favourite video editor (such as ShotCut) to embed or attached .srt files to your videos.

## MKV to MP4

This Python script uses CPU or GPU to convert MKV files to H254 MPEG files. Mainly used to allow for playing on browser / home assistant.
