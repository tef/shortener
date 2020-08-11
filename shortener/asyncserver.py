import asyncio
import io
import sys

from . import testrunner

class HTTPRequest:
    def __init__(self):
        self.state = "first"
        self.raw_first = bytearray()
        self.raw_headers = bytearray()
        self.raw_body = bytearray()
        self.raw_body_length = 0
        self.method = None
        self.path = None
        self.headers = {}
        self.body = bytearray()

    def parse(self, buf):
        for c in buf:
            if self.state == "first":
                self.raw_first.append(c)
                if self.raw_first[-2:] == b"\r\n":
                    self.state = "headers"
                    first_line = self.raw_first.decode('utf-8').split(' ')
                    self.method = first_line[0]
                    self.path = first_line[1]

            elif self.state == "headers":
                self.raw_headers.append(c)
                if self.raw_headers[-4:] == b"\r\n\r\n":
                    headers = self.raw_headers.decode('utf-8').split('\r\n')
                    for line in headers:
                        line = line.rstrip()
                        if ':' in line:
                            k, v = line.split(':', 1)
                            self.headers[k.lower().strip()] = v.strip()
                    self.state = "body"
            elif self.state == "body":
                self.raw_body.append(c)
        if self.state == "body" and self.raw_body_length <= 0:
            self.state = "end"

    def complete(self):
        return self.state == "end"



def create_server(app):
    class WSGIServer(asyncio.Protocol):
        def __init__(self):
            self.req = HTTPRequest()

        def connection_made(self, transport):
            self.transport = transport
        def data_received(self, data):
            self.req.parse(data)
            if self.req.complete():
                environ = {
                    'REQUEST_METHOD': self.req.method,
                    'PATH_INFO': self.req.path,
                    'CONTENT_LENGTH': len(self.req.raw_body),
                    'wsgi.input': io.BytesIO(self.req.raw_body),
                }
                _status = "200 OK"
                _headers = {}

                def start_response(status, headers, exc_info=None):
                    nonlocal _status
                    _status = status
                    for name, value in headers:
                        _headers[name] = value

                body = app(environ, start_response)
                body = b"".join(body)

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

TESTS = testrunner.TestRunner()

@TESTS.add()
def parser_test():
    req = HTTPRequest()
    req.parse(b'GET / HTTP/1.1\r\nHost: 127.1:1729\r\nUser-Agent: curl/7.51.0\r\nAccept: */*\r\n\r\n')
    assert req.complete()

if __name__ == '__main__':
    TESTS.run()
