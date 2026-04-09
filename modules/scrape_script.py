"""Main module script for script-extractor"""

import json
import re

from bs4 import BeautifulSoup
import requests

def _get_gandalf_lines(page: str) -> list[str]:
    """Method to extract voice lines that are from `GANDALF`.

    Args:
        url (str): Website URL from www.ageofthering.com

    Returns:
        list[str]: The found voice lines from `GANDALF`
    """

    print("Parsing", page)

    response = requests.get(page, timeout=10)
    if response.ok:
        html_doc = response.content.decode(errors='ignore')
    else:
        print("error on page", page)
        print(response)
        return []

    soup = BeautifulSoup(html_doc, "html.parser")
    cells = soup.find_all("td", string=re.compile("GANDALF"))

    found_lines = []
    for cell in cells:
        line = cell.next_sibling.next_sibling.text
        if line:
            cleaned_line = _clean_line(line)
            found_lines.append(cleaned_line)

    return found_lines

def _clean_line(line: str) -> str:
    """Method to clean voice lines.

    Args:
        line (str): A given voice line.

    Returns:
        str: A cleaned voice line.
    """

    cleaned_line = re.sub(r"\s?\([^)]*\)", "", line) # Removes text in paranthesis and the symbols
    final_line = re.sub(r"\s+", " ", cleaned_line).strip() # Removes newlines and whitespace
    return final_line

def _parse_fellowship(base_url: str) -> list[str]:
    """Method to parse the fellowship script.

    Returns:
        list[str]: found voice lines of Gandalf
    """

    urls = [
        "fellowshipofthering1to4.php", "fellowshipofthering5to8.php",
        "fellowshipofthering9to12.php", "fellowshipofthering13to16.php",
        "fellowshipofthering17to20.php", "fellowshipofthering21to24.php",
        "fellowshipofthering25to28.php", "fellowshipofthering29to32.php",
        "fellowshipofthering33to36.php", "fellowshipofthering37to40.php"
    ]

    lines = []
    for url in urls:
        page = base_url + url
        result = _get_gandalf_lines(page)
        if result:
            lines += result
    return lines

def _parse_towers(base_url: str) -> list[str]:
    """Method to parse the towers script.

    Returns:
        list[str]: found voice lines of Gandalf
    """

    urls = [
        "thetwotowers1to4.php", "thetwotowers5to8.php",
        "thetwotowers9to12.php", "thetwotowers13to16.php",
        "thetwotowers17to20.php", "thetwotowers21to24.php",
        "thetwotowers25to28.php", "thetwotowers29to32.php",
        "thetwotowers33to36.php", "thetwotowers37to40.php",
        "thetwotowers41to44.php", "thetwotowers45to48.php",
        "thetwotowers49to52.php", "thetwotowers53to56.php",
        "thetwotowers57to60.php", "thetwotowers61to64.php",
        "thetwotowers65to66.php"
    ]

    lines = []
    for url in urls:
        page = base_url + url
        result = _get_gandalf_lines(page)
        if result:
            lines += result
    return lines

def _parse_king(base_url) -> list[str]:
    """Method to parse the king script.

    Returns:
        list[str]: found voice lines of Gandalf
    """

    urls = [
        "returnoftheking1to4.php", "returnoftheking5to8.php",
        "returnoftheking9to12.php", "returnoftheking13to16.php",
        "returnoftheking17to20.php", "returnoftheking21to24.php",
        "returnoftheking25to28.php", "returnoftheking29to32.php",
        "returnoftheking33to36.php", "returnoftheking37to40.php",
        "returnoftheking41to44.php", "returnoftheking45to48.php",
        "returnoftheking49to52.php", "returnoftheking53to56.php",
        "returnoftheking57to60.php", "returnoftheking61to64.php",
        "returnoftheking65to68.php", "returnoftheking69to72.php",
        "returnoftheking73to76.php"
    ]

    lines = []
    for url in urls:
        page = base_url + url
        result = _get_gandalf_lines(page)
        if result:
            lines += result
    return lines

def _save_lines(filename: str, lines: list[str]) -> None:
    """Method to save voicelines to a JSON file.

    Args:
        filename (str): _description_
        lines (list[str]): _description_
    """

    with open(f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(lines, f)

def scrape(base_dir: str, base_url: str):
    """The main script method."""

    fellowship_lines = _parse_fellowship(base_url)
    if fellowship_lines:
        _save_lines(base_dir + "fellowship_script", fellowship_lines)

    towers_lines = _parse_towers(base_url)
    if towers_lines:
        _save_lines(base_dir + "towers_script", towers_lines)

    king_lines = _parse_king(base_url)
    if king_lines:
        _save_lines(base_dir + "king_script", king_lines)

    print("Script extraction done!")
