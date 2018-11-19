#!/usr/bin/python3
# -*- coding: utf-8 -*-

import functools
import os
import signal
import subprocess
import sys

from bs4 import BeautifulSoup, NavigableString
from config import DaemonConfig
from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, pyqtSignal, QMimeData
from random import random

"""
Add/Fix:
1. Simultaneous selection of unrelated elements
2. Custom MIME data handling
3. Avoid reconstructing copy of mime obj for every selection
4. X11 stuff
5. Config options - More random
6. Memory usage considerations
7. Consider Black code style
"""

def random_hit_chance_util(flag):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if random() < 0.5:
                func(*args, **kwargs)
        if flag:
            return wrapper
        else:
            return func
    return decorator


def X_server_running():
    """Return a bool indicating whether an X server is running or not"""
    try:
        proc = subprocess.Popen(["xset", "q"], stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL)
    except OSError:
        return False
    try:
        proc.communicate(timeout=4)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
    return proc.returncode == 0


class ModifyData:

    def __init__(self, text):
        self.text = text

    def replace_chars(self):
        target = b'a'.decode("utf-8")
        gqm = b'\xcd\xbe'.decode("utf-8")

        s = self.text.replace(target, gqm)
        return s


class ClipboardHandler(QObject):

    dc = DaemonConfig()
    dc.set_config()
    if dc.valid_config():
        cfg = dc.custom_config
    else:
        sys.exit("Error: Daemon configuration file is invalid!")

    def __init__(self):
        super().__init__()

        self.clipboard = QGuiApplication.clipboard()
        self.clipboard.dataChanged.connect(self.overwrite)

    def reconstruct(self, mime_data):
        fin_mime_data = QMimeData()

        format_list = mime_data.formats()
        #print(format_list)

        for format in format_list:
            if not format == "text/plain" and not format == "text/html":
                orig_data = mime_data.data(format)
                fin_mime_data.setData(format, orig_data)

        if mime_data.hasText():
            plaintext = mime_data.text()
            p = ModifyData(plaintext)
            modified_plaintext = p.replace_chars()
            fin_mime_data.setText(modified_plaintext)

        if mime_data.hasHtml():
            markup = mime_data.html()
            soup = BeautifulSoup(markup, "html.parser")
            for inner_text in list(soup.strings):
                p = ModifyData(inner_text)
                inner_text.replace_with(NavigableString(p.replace_chars()))
            fin_mime_data.setHtml(str(soup))

        return fin_mime_data

    @random_hit_chance_util(cfg["random_hit_chance"])
    def overwrite(self):
        
        mime_data = self.clipboard.mimeData()
        fin_mime_data = self.reconstruct(mime_data)

        temp_state = self.clipboard.blockSignals(True)
        self.clipboard.setMimeData(fin_mime_data)
        self.clipboard.blockSignals(temp_state)

if __name__ == "__main__":

    # Courtesy of a known bug, Qt fires the qWarning
    # "QXcbClipboard::setMimeData: Cannot set X11 selection owner"
    # while setting clipboard data when cut/copy events are encountered
    # in rapid succession, resulting in clipboard data not being set.
    # This env variable acts as a fail-safe which aborts the application
    # if this happens more than once.
    os.environ["QT_FATAL_WARNINGS"] = "1"

    # Python cannot handle signals while the Qt event loop is running.
    # This is required to force quit the application when SIGINT is sent, 
    # typically during development or testing. A custom handler is not
    # used here to avoid the overhead of running the Python interpreter
    # from time to time.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QGuiApplication(sys.argv)
    c = ClipboardHandler()
    sys.exit(app.exec_())
