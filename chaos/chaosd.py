#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import signal
import subprocess
import sys

from bs4 import BeautifulSoup, NavigableString
from configoptions import DaemonConfig
from configutils import randomhit
from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, QMimeData

"""
Add/Fix:
1. X11 stuff
2. Config options
3. Memory usage considerations
4. Consider Black code style
"""


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

        clipboard = QGuiApplication.clipboard()
        clipboard.dataChanged.connect(self.overwrite)

    def unsafe(self, mime_data):
        format_list = mime_data.formats()

        if not format_list:
            return True

        # Filter the MIME types "image/*" to ignore image data
        # and "text/uri-list" to ignore files and directories.
        if mime_data.hasImage() or mime_data.hasUrls():
            return True

        # Custom MIME data is very application specific and varies
        # wildly across applications. It usually takes the format:
        # application/x-x-x;value="somevalue"
        # Currently, chaos does not modify objects with such MIME data.
        for format in format_list:
            if format.endswith('"'):
                return True

    def reconstruct(self, mime_data):
        format_list = mime_data.formats()
        fin_mime_data = QMimeData()

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

    @randomhit(cfg["random_hit_chance"])
    def overwrite(self):
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()

        if not self.unsafe(mime_data):
            fin_mime_data = self.reconstruct(mime_data)
            temp_state = clipboard.blockSignals(True)
            clipboard.setMimeData(fin_mime_data)
            clipboard.blockSignals(temp_state)


if __name__ == "__main__":

    # On systems running X11, possibly due to a bug, Qt fires the qWarning
    # "QXcbClipboard::setMimeData: Cannot set X11 selection owner"
    # while setting clipboard data when cut/copy events are encountered
    # in rapid succession, resulting in clipboard data not being set.
    # This env variable acts as a fail-safe which aborts the application
    # if this happens more than once. Similar situation arises when another
    # clipboard management app (like GPaste) is running alongside chaos.
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
