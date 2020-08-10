import store
import wsgiservice

import sys

class ShortenerService(wsgiservice.WSGIService):
    def on_request(self, method, path, query, data, headers):
        pass


TESTS = []
def Test():
    def _decorator(fn):
        TESTS.append(fn)
        return fn
    return _decorator


@Test()
def test_service():
    service = wsgiservice.WSGIServer(ShortenerService())
    service.start()
    response = wsgiservice.GET(service.url)
    print(response)
    assert response == ""
    service.stop()

if __name__ == '__main__':
    count, success, fail, error = 0,0,0,0
    for test in TESTS:
        count +=1
        try:
            test()
            success +=1
        except AssertionError as e:
            fail +=1
            print("Failed Assertion: {} in test {}".format(e, test.__name__), file=sys.stderr)
        except Exception as e:
            error +=1
            print("Error: {} in test {}".format(e, test.__name__), file=sys.stderr)
    if count == success:
        print("ran {} tests, {} passed".format(count, success))
    else:
        print("ran {} tests, {} passed, {} failed, {} errors".format(count, success, fail, error))
