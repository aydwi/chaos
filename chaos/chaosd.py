#!/usr/bin/python3
# -*- coding: utf-8 -*-

import functools
import os
import signal
import sys

from config import DaemonConfig
from random import random

from bs4 import BeautifulSoup, NavigableString
from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, QMimeData


"""
Add/Fix:
1. Config options
2. Preserve data after (force) quitting
3. Custom chars support
4. Tests and coverage
5. Dependency Injection
6. Daemonize
"""


def enable_rhc(flag):
    def decorator(func):
        @functools.wraps(func)
        def decorated_func(*args, **kwargs):
            if random() < 0.5:
                func(*args, **kwargs)
        if flag:
            return decorated_func
        else:
            return func
    return decorator


class ModifyData:

    def __init__(self, text):
        self.text = text

    def replace_chars(self):
        target = b'a'.decode("utf-8")
        gqm = b'\xcd\xbe'.decode("utf-8")
        s = self.text.replace(target, gqm)
        return s


class MimeHandler:

    def __init__(self, mime_data, fin_mime_data, format_list):
        self.mime_data = mime_data
        self.fin_mime_data = fin_mime_data
        self.format_list = format_list

    def filter(self):
        if not self.format_list:
            return True

        # Filter the MIME types "image/*" to ignore image data
        # and "text/uri-list" to ignore files and directories.
        if self.mime_data.hasImage() or self.mime_data.hasUrls():
            return True

        # Custom MIME data can vary wildly across applications, and
        # usually takes the following format:
        # application/x-y-z;value="somevalue"
        # Currently, chaos does not modify objects with such MIME data.
        for format in self.format_list:
            if format.endswith('"'):
                return True

    def tset(self):
        if self.mime_data.hasText():
            plaintext = self.mime_data.text()
            p = ModifyData(plaintext)
            modified_plaintext = p.replace_chars()
            self.fin_mime_data.setText(modified_plaintext)
            self.format_list.remove('text/plain')

    def hset(self):
        if self.mime_data.hasHtml():
            markup = self.mime_data.html()
            soup = BeautifulSoup(markup, "html.parser")
            for inner_text in list(soup.strings):
                p = ModifyData(inner_text)
                inner_text.replace_with(NavigableString(p.replace_chars()))
            self.fin_mime_data.setHtml(str(soup))
            self.format_list.remove('text/html')

    def oset(self):
        for format in self.format_list:
            orig_data = self.mime_data.data(format)
            self.fin_mime_data.setData(format, orig_data)


class Clipboard(QObject):

    dc = DaemonConfig()
    dc.set_config()
    if dc.valid_config():
        config = dc.custom_config
    else:
        sys.exit("Error: Daemon configuration file is invalid!")

    def __init__(self):
        super().__init__()
        clipboard = QGuiApplication.clipboard()
        clipboard.dataChanged.connect(self.overwrite)

    def set_mime_data(self, fin_mime_data):
        clipboard = QGuiApplication.clipboard()
        tmp = clipboard.blockSignals(True)
        clipboard.setMimeData(fin_mime_data, mode = 0)
        clipboard.blockSignals(tmp)

    @enable_rhc(config["random_hit_chance"])
    def overwrite(self):
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData(mode = 0)
        fin_mime_data = QMimeData()
        format_list = mime_data.formats()
        mh = MimeHandler(mime_data, fin_mime_data, format_list)

        if not mh.filter():
            if not Clipboard.config["plaintext_only"]:
                mh.tset()
                mh.hset()
                mh.oset()
                self.set_mime_data(fin_mime_data)
            else:
                if not mime_data.hasHtml():
                    mh.tset()
                    mh.oset()
                    self.set_mime_data(fin_mime_data)


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
    c = Clipboard()
    sys.exit(app.exec_())
