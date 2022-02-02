"""
This module provides a boilerplate to create your own automatic wallpaper setter!
The main class to be used is `AutoWallpaper`. Documentation of the class is in the
class docstring.
"""

import sys
from datetime import date
from os import path, remove
from time import perf_counter, sleep
from typing import Callable, Union

from requests import get

from .daemon import Daemon

# TODO : Add support for more desktop envs
if sys.platform in ["darwin"]:
    from os import system
elif sys.platform in ["win32", "cygwin"]:
    import ctypes
elif sys.platform in ["linux"]:
    from subprocess import Popen


# -----------
# GLOBAL VARS
# -----------
IMAGE_FILE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png"
)

# TODO : Make this a dict to point to various OSes and desktop envs
SUPPORTED_PLATFORMS = [
    "darwin",
    "win32",
    "cygwin",
    "linux"
]


# ----------
# EXCEPTIONS
# ----------
class ImageSourceException(Exception):
    """
    Used to handle invalid sources.
    These may include URL being unreachable, or the file having
    the wrong format.
    """

class SetWallpaperException(Exception):
    """
    Used to handle errors while setting wallpaper.
    """

class ImageDirectoryException(Exception):
    """
    Used to handle issues with image directory.
    """


# --------------------
# MAIN WALLPYPER CLASS
# --------------------
class AutoWallpaper(Daemon):
    """
    Daemon that handles the setting of wallpaper periodically.

    Attributes
    ----------
        source_function : Callable
            The function that fetches the URL of the image
            as string.
        image_path : str, optional
            Path where the images will be saved.
            Note that images may be saved with the same name but with a
            different file format based on source image.
            Default is "/tmp/".
        pidfile : str, optional
            Path to the file containing PID of the daemon.
            Default is "/tmp/autowallpaper.pid".
        output_file : str, optional
            Path to the file that will store output.
            Default is "/tmp/autowallpaper.out".
        error_file : str, optional
            Path to the file that will contain errors.
            Default is "/tmp/autowallpaper.err".
        log_file : str, optional
            Path to the file that will contain logs.
            Default is "/tmp/autowallpaper.log".
    """
    def __init__(
            self,
            source_function: Callable,
            image_dir: str = "/tmp/",
            pidfile: str = "/tmp/autowallpaper.pid",
            output_file: str = "/tmp/autowallpaper.out",
            error_file: str = "/tmp/autowallpaper.err",
            log_file: str = "/tmp/autowallpaper.log"
        ):
        self._os = sys.platform
        self.source_function = source_function

        # Clean up directory argument
        if not path.isdir(image_dir):
            raise ImageDirectoryException(f"Invalid image directory {image_dir}.")
        if not image_dir.endswith("/"):
            image_dir = image_dir + "/"

        self.image_dir = image_dir
        self._debug = "DEBUG"
        self._error = "ERROR"
        super().__init__(pidfile, output_file, error_file, log_file)

    def source_image(self, *args, **kwargs) -> Union[str, None]:
        """
        This method calls the input function that fetches the URL of an image.
        Returns filepath of the upon successful execution, else None.
        """
        image_source = self.source_function(*args, **kwargs)

        # Check if URL or file path has right extension
        file_ext = "." +image_source.split(".")[-1]
        if file_ext not in IMAGE_FILE_EXTENSIONS:
            # This error isn't raised to avoid program stoppage due to a single error
            self.log(
                ImageSourceException(f"Invalid file extension {file_ext} found at {image_source}"),
                self._error
            )
            return None


        if path.isfile(image_source):
            return image_source

        try:
            image = get(image_source)
            filepath = self.image_dir +str(date.today()) +file_ext

            with open(filepath, "wb") as image_file:
                image_file.write(image.content)

            self.log(f"Fetched image from {image_source}.", self._debug)
            return filepath

        except ConnectionError as exception:
            # This error isn't raised because there may be problems with the internet connection
            self.log(exception, self._error)
            return None

    def set_wallpaper(self, image_path: str) -> bool:
        """
        This function sets the wallpaper with the image at `image_path`.
        Returns `True` if successful, raises SetWallpaperException if not.

        Parameters
        ----------
            image_path : str
                The path of the image that needs to be set as a wallpaper
        """
        if path.isfile(image_path):
            # Mac OS
            if self._os in ["darwin"]:
                system(
                    "osascript -e\
                    'tell application \"Finder\" to set desktop picture to POSIX file\
                    \"" +image_path + "\"'"
                )

            # Windows
            elif self._os in ["win32", "cygwin"]:
                # TODO : Test this
                ctypes.windll.user32.SystemParametersInfoW(
                    20, 0, self.image_path.replace("/", "\\"), 0
                )

            # Linux (only Gnome is supported so far)
            elif self._os in ["linux"]:
                # TODO : Test this
                args = [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.background",
                    "picture-uri",
                    self.image_path
                ]
                with Popen(args) as _:
                    pass

            self.log("Wallpaper set succesfully.", self._debug)
            return True

        raise SetWallpaperException(f"Path {image_path} is not valid path.")

    def run(self, *args, **kwargs):
        """
        This is the code that is run by the daemon process.
        This part can be overridden to control your own wallpaper changing
        method. Default function changes wallpaper every 24 hours.

        `*args` and `**kwargs` are passed as-is to the `source_image()` function
        of the object.
        """
        fetched_image = ""
        while True:
            self.log("Running...", self._debug)

            # Deletes older images
            # TODO : Change this to not delete local images
            if path.isfile(fetched_image):
                remove(fetched_image)

            time_start = perf_counter()

            fetched_image =  self.source_image(*args, **kwargs)

            if fetched_image:
                self.set_wallpaper(fetched_image)

            time_end = perf_counter()

            # To run every 24h since program start
            sleep(24 * 60 * 60 - (time_end - time_start))
