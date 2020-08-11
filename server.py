import asyncio
import sys

def app(environ,start_response):
    return ["Hello\n"]

def create_server(app):
    class WSGIServer(asyncio.Protocol):
        def __init__(self):
            self.buf = bytearray()

        def connection_made(self, transport):
            self.transport = transport
        def data_received(self, data):
            self.buf.extend(data)
            if self.buf and self.buf[-4:] == b"\r\n\r\n":
                environ = {}
                _status = "200 OK"
                _headers = {}

                def start_response(status, headers):
                    nonlocal _status, _headers
                    _status = status
                    _headers = headers

                body = app(environ, start_response)
                body = "".join(body).encode('utf-8')

                if 'content-type' not in _headers or 'Content-Type' not in _headers:
                    _headers['Content-Type'] = "text/plain"
                _headers['Content-Length'] = str(len(body))
                _headers['Connection'] = 'Close'

                out = [ "HTTP/1.0 {}".format(_status) ]
                for name, value in _headers.items():
                    out.append("{}: {}".format(name, value))
                self.transport.write("\r\n".join(out).encode('utf-8'))
                self.transport.write(b"\r\n\r\n")
                self.transport.write(body)
                self.transport.close()
    return WSGIServer

async def run_server(app, host, port):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(create_server(app), host, port)
    await server.serve_forever()

if __name__ == '__main__':
    host = "0.0.0.0"
    port = 1729
    if sys.argv[1:]:
        arg = sys.argv[1].split(":")
        host = arg[0]
        if len(arg) > 1:
            port = arg[1]

    print("http://{}:{}".format(host, port))
    asyncio.run(run_server(app, host, port))
