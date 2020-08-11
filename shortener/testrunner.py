""" bare bones test runner """
import sys
import os.path

class TestRunner:
    def __init__(self):
        self.tests = []

    def add(self):
        def _decorator(fn):
            self.tests.append(fn)
            return fn
        return _decorator

    def run(self):
        file = os.path.relpath(sys.argv[0])
        count, success, fail, error = 0,0,0,0
        for test in self.tests:
            count +=1
            try:
                test()
                success +=1
            except AssertionError as e:
                fail +=1
                print("{}: Failed Assertion {} in test {}".format(file, e, test.__name__), file=sys.stderr)
            except Exception as e:
                error +=1
                print("{}: Error: {} in test {}".format(file, e, test.__name__), file=sys.stderr)
        if count == success:
            print("{}: ran {} tests, {} passed".format(file, count, success))
        else:
            print("{}: ran {} tests, {} passed, {} failed, {} errors".format(file, count, success, fail, error))

if __name__ == '__main__':
    runner = TestRunner()
    @runner.add()
    def example():
        pass
    runner.run()
