"""Module to extract audio clips from the original movie audios."""

import subprocess
import datetime
import os
import re

import json

def _extract_clips(source_filepath: str, clips_list: list) -> None:
    """Extracts multiple clips from a single FLAC file."""

    if not os.path.exists(source_filepath):
        print(f"Error: Source file '{source_filepath}' not found.")
        return

    print(f"--- Processing {len(clips_list)} clips from {source_filepath} ---")

    for output_name, start_time, end_time in clips_list:

        duration = end_time - start_time
        start_sec = str(start_time.total_seconds())
        duration_sec = str(duration.total_seconds())

        cmd = [
            'ffmpeg',
            '-n', # Do not overwrite if exists
            '-ss', start_sec,
            '-i', source_filepath,
            '-t', duration_sec,
            output_name
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"[OK] Saved: {output_name}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed on {output_name}: {e}")

def _convert_str_to_timedelta(input_string: str) -> datetime.timedelta:
    """Method to convert strings to timedelta objects.

    Args:
        input (str): A string formatted as "H:M:S.f"

    Returns:
        datetime.timedelta: The corresponding timedelta objects
    """
    t = datetime.datetime.strptime(input_string, "%H:%M:%S.%f")
    td = datetime.timedelta(
        hours=t.hour,
        minutes=t.minute,
        seconds=t.second,
        microseconds=t.microsecond
        )

    return td

def _safe_filename(s: str) -> str:
    """Method to convert string to filename safe string on Windows

    Args:
        s (str): unsafe string

    Returns:
        (str): safe string
    """

    s = s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    return re.sub(r'[<>:"/\\|?*]', '', s).strip() or "unnamed"

def _get_clips(filepath: str, output_folder: str):
    """Method to grab clips from matches file and return a clip object.

    Args:
        filepath (str): The filepath of a matches file.

    Returns:
        _type_: The clips object
    """

    with open(filepath, "r", encoding="utf-8") as f:
        content = json.load(f)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    found_clips = []
    for key in content:
        value = content[key]
        start = _convert_str_to_timedelta(value[0])
        end = _convert_str_to_timedelta(value[1])
        found_clips.append((output_folder + _safe_filename(key) + ".wav", start, end))

    return found_clips

def rip(base_dir: str):
    """The main method"""

    fellowship_clips = _get_clips(base_dir + "fellowship_matches.json", base_dir + 
                                  "clips\\")
    towers_clips = _get_clips(base_dir + "towers_matches.json", base_dir + "clips\\")
    king_clips = _get_clips(base_dir + "king_matches.json", base_dir + "clips\\")
    _extract_clips(base_dir + "fellowship.flac", fellowship_clips)
    _extract_clips(base_dir + "towers.flac", towers_clips)
    _extract_clips(base_dir + "king.flac", king_clips)

    print("Audio extraction done!")
