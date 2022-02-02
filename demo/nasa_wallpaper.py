"""
NASA APOD Wallpaper
-------------------

This program is used to demonstrate how to use `autowallpaper` to make your own.
Source of images : NASA Astronomy Photo Of The Day (https://apod.nasa.gov/apod/astropix.html).
"""

import argparse
from json import loads
from os import path

from requests import get

from autowallpaper import AutoWallpaper

parser = argparse.ArgumentParser(
    description="Changes wallpaper daily to NASA's APOD."
)

parser.add_argument(
    "action",
    help="starts, stops, or restarts daemon",
    choices=["start", "stop", "restart"]
)
parser.add_argument(
    "-k", "--api_key",
    help="NASA API key OR file that contains NASA API key"
)
parser.add_argument(
    "-p", "--pidfile",
    nargs="?", default='/tmp/autowallpaper.pid',
    help="path where the PID is to be stored, default is '/tmp/autowallpaper.pid'"
)
parser.add_argument(
    "-i", "--image_dir",
    nargs="?", default='/tmp/',
    help="path where the image is to be stored, default is '/tmp/'"
)
parser.add_argument(
    "-o", "--output_file",
    nargs="?", default='/tmp/autowallpaper.out',
    help="path where code outputs are logged, default is '/tmp/autowallpaper.out'"
)
parser.add_argument(
    "-e", "--error_file",
    nargs="?", default='/tmp/autowallpaper.err',
    help="path where code errors are logged, default is '/tmp/autowallpaper.err'"
)
parser.add_argument(
    "-x", "--explanations",
    nargs="?", default=False,
    help="to log explanations in the log file, default is '/tmp/autowallpaper.err'"
)


# ---------
# EXCEPTION
# ---------
class APIKeyException(Exception):
    """
    Handles issues with API key
    """

# -----------------------
# IMAGE SOURCING FUNCTION
# -----------------------
def source_image(api_key: str, explanations: bool = False) -> str:
    """
    Fetches the URL of the latest image

    Parameter
    ---------
        api_key : str
            Path the the file containining the API key.
        explanations: bool, optional
            Boolean to check whether the title and explanation of the image
            must be logged or not.
            Default is `False`.
    """

    if path.isfile(api_key):
        with open(api_key, "r") as keyfile:
            api_key = keyfile.read().strip()

    if not api_key:
        raise APIKeyException("Please provide a valid NASA API key [https://api.nasa.gov].")

    status_code = 500
    while status_code != 200:
        apod_page = get("https://api.nasa.gov/planetary/apod?api_key=" + api_key)
        status_code = apod_page.status_code
    if status_code in [401, 403]:
        raise APIKeyException("Invalid NASA API key. Generate new key at https://api.nasa.gov.")

    apod_page = loads(apod_page.content.decode('utf-8'))
    if explanations:
        print(f"[{apod_page['date']}] - {apod_page['title']}")
        print(apod_page['explanation'])
    return apod_page['hdurl']


if __name__ == "__main__":
    args = parser.parse_args()
    autowallpaper = AutoWallpaper(
            source_function=source_image,
            pidfile=args.pidfile,
            image_dir=args.image_dir,
            output_file=args.output_file,
            error_file=args.error_file
    )

    if args.action == "start":
        autowallpaper.start(args.api_key, args.explanations)

    if args.action == "stop":
        autowallpaper.stop()

    if args.action == "restart":
        autowallpaper.restart(args.api_key, args.explanations)
