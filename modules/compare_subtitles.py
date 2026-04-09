"""Module script to extract voice lines from subtitle 
files and compare them with extracted script lines."""

from typing import Dict
import datetime
import json
import re

from difflib import SequenceMatcher
import srt

def _get_srt(filepath: str) -> list:
    """Method to get srt.Subtitle object from file.

    Args:
        filepath (str): The filepath of the srt file.

    Returns:
        srt.Subtitle: The srt.Subtitle object
    """

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    subtitle = srt.parse(content)
    return list(subtitle)

def _parse_srt(srt_obj: list) -> Dict[str, list[datetime.timedelta]]:
    """Method to parse srt.Subtitle object and get [line, list[start, end]].

    Args:
        srt_obj (srt.Subtitle): The srt.Subtitle object

    Returns:
        Dict[str, datetime]: [line, list[start, end]]
    """

    result = {}
    for event in srt_obj:
        result[event.content] = [event.start, event.end]

    return result

def _get_script_lines(filepath: str) -> list[str]:
    """Method to open a file containing extracted Gandalf voice lines and returns them.

    Args:
        filepath (str): The filepath of a JSON file containing extracted Gandalf voicelines.

    Returns:
        list[str]: A list of Gandalf voicelines.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def _compare_line(subtitle_line: str, script_line: str) -> bool:
    """Method to compare a subtitle line with a script line.

    Args:
        subtitle_line (str): A subtitle line
        script_line (str): A script line

    Returns:
        bool: Did the line pass the threshold?
    """

    # find words
    words1 = re.findall(r'\w+', subtitle_line.lower())
    words2 = re.findall(r'\w+', script_line.lower())

    # Finds the longest contiguous matching subsequences.
    matcher = SequenceMatcher(None, words1, words2)

    # .ratio() returns a float in [0, 1] measuring similarity.
    # 1.0 means identical word sequences.
    result = matcher.ratio()

    # Threshold of 0.8
    return result > 0.8

def _compare_srt_script(
    subtitle_obj: Dict[str, list[datetime.timedelta]],
    script_lines: list[str]
    ) -> Dict[str, str]:
    """Method to compare subtitle lines against extracted script lines.

    Args:
        subtitle_lines (Dict[str, list[datetime.timedelta]]): Subtitle object
        script_lines (list[str]): Script object

    Returns:
        Dict[str, str]: Matched subtitle events.
    """

    matches = {}
    for subtitle_entry in subtitle_obj:
        for script_line in script_lines:
            match = _compare_line(subtitle_entry, script_line)
            if match is True:
                matches[subtitle_entry] = (
                    str(subtitle_obj[subtitle_entry][0]),
                    str(subtitle_obj[subtitle_entry][1])
                    )

    return matches

def _save_matches(filepath: str, matches: Dict[str, list[datetime.timedelta]]) -> None:
    """Method to save matches to a JSON file."""

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(matches, f)

def compare(base_dir: str):
    """The main compare method."""

    # Get SRT objects
    fellowship_srt = _get_srt(base_dir + "fellowship.srt")
    towers_srt = _get_srt(base_dir + "towers.srt")
    king_srt = _get_srt(base_dir + "king.srt")

    # Parse those objects
    fellowship_lines = _parse_srt(fellowship_srt)
    towers_lines = _parse_srt(towers_srt)
    king_lines = _parse_srt(king_srt)

    # Get extracted script lines
    fellowship_script_lines = _get_script_lines(base_dir + "fellowship_script.json")
    towers_script_lines = _get_script_lines(base_dir + "towers_script.json")
    king_script_lines = _get_script_lines(base_dir + "king_script.json")

    # Compare them!
    fellowship_matches = _compare_srt_script(fellowship_lines, fellowship_script_lines)
    towers_matches = _compare_srt_script(towers_lines, towers_script_lines)
    king_matches = _compare_srt_script(king_lines, king_script_lines)

    # Save matches!
    _save_matches(base_dir + "fellowship_matches.json", fellowship_matches)
    _save_matches(base_dir + "towers_matches.json", towers_matches)
    _save_matches(base_dir + "king_matches.json", king_matches)

    print("Compare Script Done!")
