"""The main module."""

from modules.scrape_script import scrape
from modules.compare_subtitles import compare
from modules.rip_audio import rip
from modules.clean_audio import clean

BASE_DIR = "..." # Change me
BASE_URL = "http://www.ageofthering.com/atthemovies/scripts/"

if __name__ == "__main__":
    scrape(BASE_DIR, BASE_URL)
    compare(BASE_DIR)
    rip(BASE_DIR)
    clean(BASE_DIR)
