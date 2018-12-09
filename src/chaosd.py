import daemon

from chaos import initialize, execute

"""
Add/Fix:
1. Logging
2. pidfile
3. File descriptors
4. Tests and coverage
5. Build system
"""

context = daemon.DaemonContext(umask=0o002)

config_dict = initialize()

with context:
    execute(config_dict)
