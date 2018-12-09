import os
import sys
import signal
import daemon

from chaos import initialize, execute

context = daemon.DaemonContext(umask=0o002)

config_dict = initialize()

with context:
    execute(config_dict)