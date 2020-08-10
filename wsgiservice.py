"""
   Boilerplate code for starting a WSGI Server
"""

import threading
import socket
import traceback
import sys
import urllib
import urllib.request

from urllib.parse import urljoin, urlencode, parse_qs
from wsgiref.simple_server import make_server, WSGIRequestHandler

import testhelper

class WSGIServer(threading.Thread):
    class QuietWSGIRequestHandler(WSGIRequestHandler):
        def log_request(self, code='-', size='-'):
            pass

    def __init__(self, app, host="", port=0, request_handler=QuietWSGIRequestHandler):
        threading.Thread.__init__(self)
        self.daemon=True
        self.running = True
        self.server = make_server(host, port, app,
            handler_class=request_handler)

    @property
    def url(self):
        return u'http://%s:%d/'%(self.server.server_name, self.server.server_port)

    def run(self):
        self.running = True
        while self.running:
            self.server.handle_request()

    def stop(self):
        self.running =False
        if self.server and self.is_alive():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(self.server.socket.getsockname()[:2])
                s.send(b'\r\n')
                s.close()
            except IOError:
                traceback.print_exc()
        self.join(5)

class WSGIService:
    def __call__(self, environ, start_response):
        try:
            method = environ.get('REQUEST_METHOD', '')
            prefix = environ.get('SCRIPT_NAME', '')
            path = environ.get('PATH_INFO', '')
            parameters = parse_qs(environ.get('QUERY_STRING', ''))
            parameters = {k:v[0] for k,v in parameters.items()}

            content_length = environ.get('CONTENT_LENGTH','')
            content_type = environ.get('CONTENT_TYPE','')

            headers = {name[5:].lower():value for name, value in environ.items() if name.startswith('HTTP_')}

            if content_length:
                data = environ['wsgi.input'].read(int(content_length))
                if not data:
                    data = None
            else:
                data = None

            response = self.on_request(method, path, parameters, data, headers)

            if response is not None:
                content_type, data = response
                status = "200 OK"
                response_headers = [("content-type", content_type)]
                start_response(status, response_headers)
                return [data.encode('utf-8')]
            else:
                status = "204 No Data"
                response_headers = []
                start_response(status, response_headers)
                return []

        except (StopIteration, GeneratorExit, SystemExit, KeyboardInterrupt):
            raise
        except Exception as e:
            status = "500 bad"
            response_headers = [("content-type", "text/plain")]

            start_response(status, response_headers, exc_info = sys.exc_info())
            traceback.print_exc()
            return [traceback.format_exc().encode('utf8')]

    def on_request(self, method, path, query, data, headers):
        return None

def GET(url):
   req = urllib.request.Request(url)
   with urllib.request.urlopen(req) as response:
       return response.read().decode('utf-8')

def POST(url, data):
   req = urllib.request.Request(url, data)
   with urllib.request.urlopen(req) as response:
       return response.read().decode('utf-8')


TESTS = testhelper.TestRunner()

class TestWsgiService(WSGIService):
    def __init__(self, message):
        self.message = message
    def on_request(self, method, path, query, data, headers):
        return "text/plain", self.message

@TESTS.add()
def test_service():
    message = "test message"
    service = WSGIServer(TestWsgiService(message))
    service.start()
    response = GET(service.url)
    print(message, response)
    assert message == response
    service.stop()

if __name__ == '__main__':
    TESTS.run()
