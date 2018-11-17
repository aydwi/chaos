#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random
import signal
import subprocess
import sys

from bs4 import BeautifulSoup, NavigableString
from config import DaemonConfig
from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, pyqtSignal, QMimeData


"""
Add/Fix:
1. Simultaneous selection of unrelated elements
2. Custom MIME data handling
3. Avoid reconstructing copy of mime obj for every selection
4. X11 stuff
5. Config options - More rando
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


class ModifyData:

    def __init__(self, text):
        self.text = text

    def replace_chars(self):
        gqm = b'\xcd\xbe'
        new_str = self.text.replace('a', gqm.decode('utf-8'))
        return new_str


class ClipboardHandler(QObject):

    def __init__(self):
        super().__init__()

        dc = DaemonConfig()
        dc.set_config()
        if dc.valid_config():
            self.config_flags = dc.custom_config
        else:
            sys.exit("Error: Daemon configuration file is invalid!")

        clipboard = QGuiApplication.clipboard()
        clipboard.dataChanged.connect(self.clipboard_changed)

    def clipboard_changed(self):

        clipboard = QGuiApplication.clipboard()

        mime_data = clipboard.mimeData()
        format_list = mime_data.formats()
        print(format_list)
        fin_mime_data = QMimeData()

        print("\n")
        for x in format_list:
            print("For format " + str(x))
            print(mime_data.data(x))

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

        temp_state = clipboard.blockSignals(True)
        clipboard.setMimeData(fin_mime_data)
        clipboard.blockSignals(temp_state)


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
