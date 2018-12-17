#!/usr/bin/env python3

"""
Add/Fix:
1. Tests and coverage
2. CI
3. Dependency management
4. Build system
"""

import functools
import os
import signal
import sys

from bs4 import BeautifulSoup, NavigableString
from config import DaemonConfig
from daemon import DaemonContext
from PyQt5.QtGui import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, QMimeData, QTimer
from random import random
from utils.context_manager import PidFile


TGT = "a"
GQM = b"\xcd\xbe".decode("utf-8")


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


def enable_ri(flag):
    def decorator(func):
        @functools.wraps(func)
        def decorated_func(*args, **kwargs):
            text = args[0]
            occurences = [index for index, val in enumerate(text) if val == TGT]
            for occurence in occurences:
                if random() < 0.5:
                    text = text[:occurence] + GQM + text[occurence + 1 :]
            return text

        if flag:
            return decorated_func
        else:
            return func

    return decorator


def get_config():
    daemon_config = DaemonConfig()
    daemon_config.setup()
    if not daemon_config.valid():
        sys.exit("Error: Daemon configuration is incorrect!")
    config_dict = daemon_config.custom_config
    return config_dict


def signal_handler(signum, frame):
    QGuiApplication.quit()


def timer(interval, func):
    def timer_event():
        try:
            func()
        finally:
            QTimer.singleShot(interval, timer_event)

    timer_event()


class MimeHandler:
    def __init__(self, mime_data, fin_mime_data, format_list, config_dict):
        self.mime_data = mime_data
        self.fin_mime_data = fin_mime_data
        self.format_list = format_list
        self.config_dict = config_dict
        self.modify_text = enable_ri(config_dict["random_instances"])(self.modify_text)

    def restricted_type(self):
        if not self.format_list:
            return True

        # Filter the MIME types "image/*" to ignore image data and
        # "text/uri-list" to ignore files and directories.
        if self.mime_data.hasImage() or self.mime_data.hasUrls():
            return True

        # chaos does not reconstruct objects with custom MIME data.
        for format in self.format_list:
            if format.endswith('"'):
                return True

    # This method is wrapped by a decorator to modify its behaviour based on
    # value of the config flag "random_instances", passed to it as an argument,
    # handled by the function "enable_ri". Note that this is done when the
    # class is instantiated (see the constructor), instead of when the class
    # is created (which uses @decorator syntax), because the argument comes
    # from an instance variable (config_dict).
    def modify_text(self, text):
        s = text.replace(TGT, GQM)
        return s

    def set_text(self):
        if self.mime_data.hasText():
            plaintext = self.mime_data.text()
            modified_plaintext = self.modify_text(plaintext)
            self.fin_mime_data.setText(modified_plaintext)
            self.format_list.remove("text/plain")

    def set_html(self):
        if self.mime_data.hasHtml():
            markup = self.mime_data.html()
            soup = BeautifulSoup(markup, "html.parser")
            for inner_text in list(soup.strings):
                inner_text.replace_with(NavigableString(self.modify_text(inner_text)))
            self.fin_mime_data.setHtml(str(soup))
            self.format_list.remove("text/html")

    def set_other(self):
        for format in self.format_list:
            orig_data = self.mime_data.data(format)
            self.fin_mime_data.setData(format, orig_data)


class Clipboard(QObject):
    def __init__(self, config_dict):
        super().__init__()
        self.config_dict = config_dict
        self.clipboard = QGuiApplication.clipboard()
        self.reconstruct = enable_rhc(config_dict["random_hit_chance"])(
            self.reconstruct
        )
        self.clipboard.dataChanged.connect(self.reconstruct)

    def set_mime_data(self, fin_mime_data):
        tmp = self.clipboard.blockSignals(True)
        self.clipboard.setMimeData(fin_mime_data, mode=0)
        self.clipboard.blockSignals(tmp)

    # This method is wrapped by a decorator to modify its behaviour based on
    # value of the config flag "random_hit_chance", passed to it as an
    # argument, handled by the function "enable_rhc". Note that this is done
    # when the class is instantiated (see the constructor), instead of when
    # the class is created (which uses @decorator syntax), because the
    # argument comes from an instance variable (config_dict).
    def reconstruct(self):
        mime_data = self.clipboard.mimeData(mode=0)
        fin_mime_data = QMimeData()
        format_list = mime_data.formats()
        mimeobj = MimeHandler(mime_data, fin_mime_data, format_list, self.config_dict)

        if not mimeobj.restricted_type():
            if not self.config_dict["plaintext_only"]:
                mimeobj.set_text()
                mimeobj.set_html()
                mimeobj.set_other()
                self.set_mime_data(fin_mime_data)
            else:
                if not mime_data.hasHtml():
                    mimeobj.set_text()
                    mimeobj.set_other()
                    self.set_mime_data(fin_mime_data)


def execute_app(config_dict):
    # On systems running X11, possibly due to a bug, Qt fires the qWarning
    # "QXcbClipboard::setMimeData: Cannot set X11 selection owner" while
    # setting clipboard data when copy/selection events are encountered in
    # rapid succession, resulting in clipboard data not being set. This env
    # variable acts as a fail-safe which aborts the application if this
    # happens more than once. Similar situation arises when another clipboard
    # management app (like GPaste) is running alongside chaos.
    os.environ["QT_FATAL_WARNINGS"] = "1"

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    app = QGuiApplication(sys.argv)
    timer(100, lambda: None)
    cb = Clipboard(config_dict)
    sys.exit(app.exec_())


if __name__ == "__main__":
    uid = os.geteuid()
    pid_path = "/tmp/chaos-{}.pid".format(uid)
    context = DaemonContext(umask=0o002, pidfile=PidFile(pid_path))
    config_dict = get_config()

    with context:
        execute_app(config_dict)
