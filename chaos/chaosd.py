#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import signal
import sys

from config import DaemonConfig
from utils import randomhit

from bs4 import BeautifulSoup, NavigableString
from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, QMimeData


"""
Add/Fix:
1. Config options
2. Preserve data after quitting
3. Custom chars support
4. Tests
5. Coverage
6. Daemonize
"""


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
        #clipboard.selectionChanged.connect(self.foo)
        clipboard.dataChanged.connect(self.overwrite)

    def unsafe(self, mime_data):
        format_list = mime_data.formats()
        if not format_list:
            return True

        # Filter the MIME types "image/*" to ignore image data
        # and "text/uri-list" to ignore files and directories.
        if mime_data.hasImage() or mime_data.hasUrls():
            return True

        # Custom MIME data is highly specific and varies wildly across
        # applications. It usually takes the format:
        # application/x-y-z;value="somevalue"
        # Currently, chaos does not modify objects with such MIME data.
        for format in format_list:
            if format.endswith('"'):
                return True

    def tset(self, mime_data, fin_mime_data, format_list):
        if mime_data.hasText():
            plaintext = mime_data.text()
            p = ModifyData(plaintext)
            modified_plaintext = p.replace_chars()
            fin_mime_data.setText(modified_plaintext)
            format_list.remove('text/plain')

    def hset(self, mime_data, fin_mime_data, format_list):
        if mime_data.hasHtml():
            markup = mime_data.html()
            soup = BeautifulSoup(markup, "html.parser")
            for inner_text in list(soup.strings):
                p = ModifyData(inner_text)
                inner_text.replace_with(NavigableString(p.replace_chars()))
            fin_mime_data.setHtml(str(soup))
            format_list.remove('text/html')

    def oset(self, mime_data, fin_mime_data, format_list):
        for format in format_list:
            orig_data = mime_data.data(format)
            fin_mime_data.setData(format, orig_data)

    def set_clipboard(self, fin_mime_data):
        clipboard = QGuiApplication.clipboard()
        tmp = clipboard.blockSignals(True)
        clipboard.setMimeData(fin_mime_data)
        clipboard.blockSignals(tmp)

    @randomhit(cfg["random_hit_chance"])
    def overwrite(self):
        clipboard = QGuiApplication.clipboard()

        mime_data = clipboard.mimeData()
        fin_mime_data = QMimeData()
        format_list = mime_data.formats()

        if not self.unsafe(mime_data):
            if not ClipboardHandler.cfg["plaintext_only"]:
                self.tset(mime_data, fin_mime_data, format_list)
                self.hset(mime_data, fin_mime_data, format_list)
                self.oset(mime_data, fin_mime_data, format_list)
                self.set_clipboard(fin_mime_data)
            else:
                if not mime_data.hasHtml():
                    self.tset(mime_data, fin_mime_data, format_list)
                    self.oset(mime_data, fin_mime_data, format_list)
                    self.set_clipboard(fin_mime_data)


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
