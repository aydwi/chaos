# chaos

[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/chaos-tool/Lobby)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/aydwi/chaos)

<br>

<blockquote><p>MT: Replace a semicolon (;) with a greek question mark (;) in your friend&#39;s C# code and watch them pull their hair out over the syntax error</p>&mdash; Peter Ritchie (@peterritchie) <a href="https://twitter.com/peterritchie/status/534011965132120064">November 16, 2014</a></blockquote>

<br>

*chaos* is a pastejacking tool which modifies text copied to the operating system clipboard. The idea is to replace the ASCII character semicolon (;) with an identical looking Unicode character Greek question mark (;) as soon as any text is copied to the clipboard, so that when a user tries to compile some copied code, their life becomes harder.

Click [here](https://vimeo.com/306616721) for a small demo showing what happens when *chaos* is running in the background.


## Warning - Please read before proceeding

Running *chaos* is a **potentially destructive** action, and it can cause irreversible damage when important text (say a password, or a cryptographic key) is copied to clipboard without any visible indication that the text was modified. I wrote it as a proof-of-concept tool to show how easy it is for a rogue program to manipulate your system clipboard (after reading about a malicious [clipboard hijacker discovered in PyPI](https://medium.com/@bertusk/crydataptocurrency-clipboard-hijacker-discovered-in-pypi-repository-b66b8a534a8)), as well as a tool which can be used to play practical jokes on people, if that's your thing.

It is not recommended to leave *chaos* running on a system for an extended period of time. Please use it judiciously, if you decide to do so.


## Installation

### Download the pre-built binary

**[Download](https://github.com/aydwi/chaos/releases)** the latest release, unarchive it, and run the executable inside.

### Build from source

Building *chaos* from source requires:

* Python 3
* [`poetry`](https://poetry.eustace.io/)
* [`virtualenv`](https://virtualenv.pypa.io/en/latest/)
