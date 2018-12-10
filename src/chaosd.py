#!/usr/bin/env python3

import daemon

from chaos import initialize, execute

"""
Add/Fix:
1. Daemon behaviour - privileges, pidfile, boot
2. Tests and coverage
3. CI
4. Dependency management
5. Build system
6. init.py
"""

context = daemon.DaemonContext(umask=0o002)

config_dict = initialize()

with context:
    execute(config_dict)
