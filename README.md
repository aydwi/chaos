# c̷h̵a̶o̴s̸

<br>

<blockquote><p>MT: Replace a semicolon (;) with a greek question mark (;) in your friend&#39;s C# code and watch them pull their hair out over the syntax error</p>&mdash; Peter Ritchie (@peterritchie) <a href="https://twitter.com/peterritchie/status/534011965132120064">November 16, 2014</a></blockquote>

<br>

*chaos* is a pastejacking tool for GNU/Linux which modifies text copied to the operating system clipboard. The idea is to replace the ASCII character semicolon (;) with an identical looking Unicode character Greek question mark (;) as soon as any text is copied to the clipboard, so that when a user tries to compile some copied code, their life becomes harder.

Click [here](https://vimeo.com/320997444) for a small demo showing what happens when *chaos* is running in the background.

<br>

## Warning - Please read before proceeding

Running *chaos* is a **potentially destructive** action, and it can cause irreversible damage when important text (say a password, or a cryptographic key) is copied to clipboard without any visible indication that the text was modified.

I wrote it as a proof-of-concept tool to show how easy it is for a rogue program to manipulate your system clipboard (after reading about a malicious [clipboard hijacker discovered in PyPI](https://medium.com/@bertusk/crydataptocurrency-clipboard-hijacker-discovered-in-pypi-repository-b66b8a534a8)), as well as a tool which can be used to play practical jokes on people, if that's your thing.

As the name signifies, it is an agent of chaos. Please use it judiciously, if you decide to do so.

<br>

## Installation

### Download the pre-built binary

Download the latest release from the [releases](https://github.com/aydwi/chaos/releases) page and unarchive it. No further installation is required.

### Build from source

Before building, make sure the following software is installed and added to the `PATH`-

* Python 3.6 or higher
* [`poetry`](https://poetry.eustace.io/)
* [`virtualenv`](https://virtualenv.pypa.io/en/latest/)

To build *chaos* from source, execute the Bash script `build.sh` with necessary privileges-

`./build.sh`

Note that this will remove all the source code as well, so if you are working on the code, you might want to modify the build script (see the comments inside the script).

<br>

## Usage

### Execution

*chaos* runs in the background as a Unix-style deamon process, and does not require any superuser privileges. To run it, execute the binary `chaosd` present inside the directory `chaos/`-

`./chaosd`

To stop it, kill the daemon-

`kill $(cat $(echo /tmp/chaos-$(id -u).pid))`


### Configuration

An optional configuration file `daemon.json` can be placed inside a parallel directory `config/` before starting the daemon to control its behaviour. Following options are currently supported-

| Flag | Description |
| --- | --- |
| `plaintext_only` | Only plaintext is modified, and all formatted text is ignored |
| `random_hit_chance` | Cut/copy events will be ignored entirely with a probability of 0.5 |
| `random_instances` | Random instances of target character (;) will be modified throughout the copied text. This flag can be set **if and only if** `plaintext_only` is also set.

If no configuration file is provided, every flag is assumed to be unset.

<br>

## Notes

* This tool could be used as a general purpose pastejacker by setting `TGT` and `GQM` in `chaosd.py` as required (see the comments) and rebuilding the binary. This might be generalized in a future release.

* The only platform currently supported is GNU/Linux. macOS support won't be particularly useful due to [this](https://doc.qt.io/qt-5/qclipboard.html#dataChanged) limitation, but Windows and BSD support are in the pipeline.

* There is no logging of any kind at the moment. This might change in the future, as this is the first release and a lot can be added. Contributions to the project are very welcome.

* This project is partially inspired by Greg Toombs' **[mimic](https://github.com/reinderien/mimic)**. Check that out as well.
