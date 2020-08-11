from urllib.parse import parse_qs

from . import database
from . import wsgiservice
from . import testhelper

class ShortenerService(wsgiservice.WSGIService):
    def __init__(self, store):
        self.store = store

    def on_request(self, method, path, query, content_type, data, headers):
        if method == "GET":
            if path.startswith("/u/"):
                short_key = path[3:]
                url = self.store.get_long_url(short_key)
                if url:
                    self.raise_redirect(url)
                else:
                    self.raise_notfound()
            self.raise_notfound()
        elif method == "POST":
            if path == "/shorten":
                long_url = data.decode('utf-8')
                short_key = self.store.create_short_url(long_url)
                return "text/plain", "/u/{}".format(short_key)

        self.raise_notfound()


TESTS = testhelper.TestRunner()

@TESTS.add()
def test_service():
    urlstore = database.TempStore()
    service = wsgiservice.WSGIServer(ShortenerService(urlstore))
    service.start()

    long_url = "http://a-long-url/"

    short_key = database.create_url_key(long_url)
    response = wsgiservice.POST("{}shorten".format(service.url), long_url.encode("utf-8"))
    print(response)
    assert response == "/u/{}".format(short_key)
    service.stop()

if __name__ == '__main__':
    TESTS.run()
