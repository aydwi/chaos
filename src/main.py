#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import signal
import enum

from bs4 import BeautifulSoup, NavigableString

from PyQt5.Qt import QGuiApplication, QClipboard
from PyQt5.QtCore import QObject, pyqtSignal, QMimeData, QByteArray

"""
Add/Fix:
1. Simultaneous selection of unrelated elements
2. Custom MIME data handling
3. Avoid reconstructing copy of mime obj for every selection
"""


class Replace():

    def __init__(self, text):
        self.text = text

    def replace_chars(self):
        new_str = self.text.replace('a', b'\xcd\xbe'.decode('utf-8'))
        return new_str


class ClipboardHandler(QObject):

    def __init__(self):
        super().__init__()
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
            p = Replace(plaintext)
            modified_plaintext = p.replace_chars()
            fin_mime_data.setText(modified_plaintext)

        if mime_data.hasHtml():
            markup = mime_data.html()
            soup = BeautifulSoup(markup, 'html.parser')
            for inner_text in list(soup.strings):
                p = Replace(inner_text)
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
    clipboardObj = ClipboardHandler()
    sys.exit(app.exec_())
