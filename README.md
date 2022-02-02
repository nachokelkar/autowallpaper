# autowallpaper

A python module that allows you to create your own wallpaper setting service.

## Installation

```shell
$ pip install autowallpaper
```

## Basic Usage

1. Create a new Python file.
1. In the file, write your own function (say, `my_image_function()`).This function should return the URL or file path of the image to be set as wallpaper. This function will be called every time the wallpaper is to be changed.
2. Create an object of `AutoWallpaper` with your function as the argument.
3. Run it with
    ```python
    from autowallpaper import AutoWallpaper

    autowallpaper = AutoWallpaper(
        my_image_function,
        # other arguments
    )

    autowallpaper.start()   # Starts the daemon
    autowallpaper.restart() # Restarts the daemon
    autowallpaper.stop()    # Stops the daemon
    ```
4. _(OPTIONAL)_ You can extend class `AutoWallpaper` and override `run()` to make your own scheduler, that changes wallpaper more frequently, less frequently, etc.

You can change where downloaded images and logs are stored using arguments to `AutoWallpaper`.

## Demo - NASA APOD

A working demo implementation is available in `demo/nasa_wallpaper.py`. This changes the wallpaper every 24 hours to the image featured on [NASA's Astronomy Picture of the Day](https://apod.nasa.gov/).

### Usage
1. Get an API key from [the NASA API website](https://api.nasa.gov). Save it in a file or just copy it.
2. Move `demo/nasa_wallpaper.py` in the parent directory (so the imports work fine).
3. Run using\
`$ python nasa_wallpaper.py -k [KEY | PATH_TO_KEYFILE] start|stop|restart`
4. Use `$ python nasa_wallpaper.py -h` to see additional options



---

## TODOs

- Add support to source automatically from a folder
- Simplify command for demo
- Add option to save all downloaded images instead of only the latest one
- Make logging optional
- Change paths for Windows
- Test Windows and Linux environments
- Add support for more environments
- ???