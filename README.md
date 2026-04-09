# Gandalf Voice

Accompanying scripts to my blog post about creating a "Gandalf" sounding RVC model for edge device text to speech deployment.
You can read all about it [on my website](https://blog.sstock.dev/Fun-Projects/Capturing-the-Voice-of-Gandalf).

## Requirements

- The extracted audio files and subtitles files from each movie in the Lord of the Rings Trilogy Extended Edition
- Python 3.10
- Install the Python requirements in requirements.txt
- You are required to change the base directory in `main.py:8`.

## GPU Acceleration (NVIDIA on Windows)

Please refer to the [`audio_separator` documentation](https://github.com/nomadkaraoke/python-audio-separator).