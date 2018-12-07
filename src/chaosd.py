import daemon

from chaos import main

with daemon.DaemonContext():
    main()