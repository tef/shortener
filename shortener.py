import store
import wsgiservice
import testhelper

class ShortenerService(wsgiservice.WSGIService):
    def on_request(self, method, path, query, data, headers):
        pass


TESTS = testhelper.TestRunner()

@TESTS.add()
def test_service():
    service = wsgiservice.WSGIServer(ShortenerService())
    service.start()
    response = wsgiservice.GET(service.url)
    print(response)
    assert response == ""
    service.stop()

if __name__ == '__main__':
    TESTS.run()
