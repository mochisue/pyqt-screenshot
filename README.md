# pyqt-screenshot

Create a GIF file of the screenshot.

![demo](rsc/demo.gif)

# You'll learn how to

- create a simple GUI applications with PyQt’s thread support
- implement asynchronous processing that can be safely started and stopped
- display the standard output process on the PyQt screen
- make it possible to display a progress bar

# Usage

### Install

The following command will install the latest version of a module and its dependencies.

```
pip install git+https://github.com/mochisue/pyqt-screenshot.git
```

### Run GUI

The following command will launch the GUI application. You can also do the same by running the [sample.py](src/main_gui.py) program.

```
pyqt_screehshot
```

### Take a snapshoot

1. Select the fps in the range of 1 to 9, and press the "Start" button.
2. The screenshot range can be selected by dragging and dropping. You can also press the Enter key to take a picture of the entire screen.
3. The shooting will continue until you press the "Finish" button or 30 seconds have passed.
4. When the shooting is finished, a GIF file will be created on your desktop.

# Pre-built applications

I have placed the Mac OS X application in github Releases, sorry, but it is not notarized.
This is created with [pyinstaller](https://github.com/pyinstaller/pyinstaller).

# Author

[mochisue](https://github.com/mochisue)

# Licence

[MIT](https://github.com/mochisue/pyqt-async-sample/blob/main/LICENSE)
