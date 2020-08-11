import sys
import asyncio

from shortener import database, wsgiutil, service, asyncserver

if __name__ == '__main__':
    host = "0.0.0.0"
    port = 1729
    if sys.argv[1:]:
        arg = sys.argv[1].split(":")
        host = arg[0]
        if len(arg) > 1:
            port = arg[1]

    db_file = "shortener.db"
    storage = database.Store(db_file)
    app = service.ShortenerService(storage)

    print("http://{}:{}".format(host, port))
    asyncio.run(asyncserver.run_server(app, host, port))
