""" wsgi app for url shortener service """

import html
from urllib.parse import parse_qs, urlencode

from . import database
from . import wsgiutil
from . import testrunner
from . import metrics

HOMEPAGE = """
<html><head><title>url shortener example</title></head>
<body>
<form action="/shorten" method="POST">
Long URL: <input name="url"> <input type="submit" value="Shorten!">
</form>
</body>
</html>
"""

def SHORTENED(url):
    return """
        <HTML><head><title>shortened url</title></head>
        <body>
        Your url is <A href="{}">{}</a>
        </body>
        </html>
    """.format(html.escape(url, quote=True), html.escape(url))

class ShortenerService(wsgiutil.WSGIService):
    def __init__(self, store):
        self.store = store

    def on_request(self, method, path, query, content_type, data, headers):
        if method == "GET":
            if path.startswith("/u/"):
                short_key = path[3:]
                url = self.store.get_long_url(short_key)
                if url:
                    metrics.log_redirect(short_key)
                    self.raise_redirect(url)
                else:
                    self.raise_notfound()
            elif path == "/":
                return "text/html", HOMEPAGE

            self.raise_notfound()
        elif method == "POST":
            if path == "/shorten":
                if content_type == "application/x-www-form-urlencoded":
                    data = data.decode('utf-8')
                    data = parse_qs(data)
                    long_url = data['url'][0]
                else:
                    raise Exception('bad data')
                short_key = self.store.create_short_url(long_url)
                metrics.log_creation(short_key, long_url)
                return "text/html", SHORTENED("/u/{}".format(short_key))

        self.raise_notfound()


TESTS = testrunner.TestRunner()

@TESTS.add()
def test_service():
    urlstore = database.TempStore()
    service = wsgiutil.WSGIServer(ShortenerService(urlstore))
    service.start()

    long_url = "http://a-long-url/"

    args = urlencode({'url': long_url}).encode('utf-8')
    response = wsgiutil.POST("{}shorten".format(service.url), args)

    short_key = database.create_url_key(long_url)
    assert "/u/{}".format(short_key) in response
    service.stop()

if __name__ == '__main__':
    TESTS.run()
