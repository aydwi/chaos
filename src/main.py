#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import random
import signal
import subprocess
import sys

from bs4 import BeautifulSoup, NavigableString
from cerberus import Validator
from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, pyqtSignal, QMimeData, QByteArray


"""
Add/Fix:
1. Simultaneous selection of unrelated elements
2. Custom MIME data handling
3. Avoid reconstructing copy of mime obj for every selection
4. X11 stuff
5. Config options
6. Memory usage considerations
7. Consider Black code style
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


class DaemonConfig:

    def __init__(self):
        self.default_config = {'save_logs': False,
                               'randomize': False,
                               'X11_special_paste': False,
                               'plaintext_only': False}
        self.custom_config = self.default_config

    def set_custom_config(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.split(cur_dir)[0]
        cfg_path = os.path.join(parent_dir, 'config', 'daemon.json')
        try:
            with open(cfg_path) as f:
                try:
                    custom_config = json.load(f)
                except json.JSONDecodeError:
                    sys.exit("Daemon configuration file is not a valid JSON document!")
            self.custom_config = custom_config
        except FileNotFoundError:
            pass

    def validate_config(self):
        schema = {'save_logs': {'type': 'boolean'},
                  'randomize': {'type': 'boolean'},
                  'X11_special_paste': {'type': 'boolean'},
                  'plaintext_only': {'type': 'boolean'}}
        v = Validator()
        res = v.validate(self.custom_config, schema)
        return res


class ModifyData:

    def __init__(self, text):
        self.text = text

    def replace_chars(self):
        new_str = self.text.replace('a', b'\xcd\xbe'.decode('utf-8'))
        return new_str


class ClipboardHandler(QObject):

    def __init__(self):
        super().__init__()

        dconf = DaemonConfig()
        dconf.set_custom_config()
        if dconf.validate_config():
            self.config_flags = dconf.custom_config
        else:
            sys.exit("Daemon configuration file is invalid! Please check the specification and try again.")

        QGuiApplication.clipboard().dataChanged.connect(self.read_from_clipboard)

    def read_from_clipboard(self):
        cb = QGuiApplication.clipboard()

        mime_data = cb.mimeData()
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
            soup = BeautifulSoup(markup, 'html.parser')
            for inner_text in list(soup.strings):
                p = ModifyData(inner_text)
                inner_text.replace_with(NavigableString(p.replace_chars()))
            fin_mime_data.setHtml(str(soup))

        bool_state = cb.blockSignals(True)
        cb.setMimeData(fin_mime_data)
        cb.blockSignals(bool_state)


if __name__ == "__main__":

    # Python cannot handle signals while the Qt event loop is running.
    # This statement is required to force quit (dump core and exit) the
    # application when Ctrl-C is pressed. A custom handler is not used
    # to avoid the overhead of running the Python interpreter from time
    # to time.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QGuiApplication(sys.argv)
    c = ClipboardHandler()
    sys.exit(app.exec_())
