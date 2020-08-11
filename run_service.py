#!/usr/bin/env python3 
import sys
import asyncio

from shortener import database, wsgiutil, service, asyncserver

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 1729
    if sys.argv[1:]:
        arg = sys.argv[1].split(":")
        host = arg[0]
        if len(arg) > 1:
            port = arg[1]

    if sys.argv[2:]:
        db_file = sys.argv[2]
    else:
        db_file = "shortener.db"
    storage = database.Store(db_file)
    app = service.ShortenerService(storage)

    print("STARTED: Database '{}', http://{}:{}/ ".format(db_file, host, port))
    try:
        asyncio.run(asyncserver.run_server(app, host, port))
    except KeyboardInterrupt:
        print("\rEXITING")
