import time
from workflow.base import BaseTest, BaseWorker


class SimpleTest(BaseTest):

    def __init__(self, name, result):
        self._name = name
        self.result = result

    def createWorker(self):
        return SimpleTestWorker(self.result)


class SimpleTestWorker(BaseWorker):
    def __init__(self, result):
        super(SimpleTestWorker, self).__init__()
        self.result = result

    def perform(self):

        for i in range(0, 100, 10):
            time.sleep(0.05)
            self.progress.emit(10)
            time.sleep(0.05)

        return self.result


TESTS = (
    SimpleTest("USB", True),
    SimpleTest("PCIA", True),
    SimpleTest("THERMOMETER", False),
    SimpleTest("GPIO", True),
    SimpleTest("CLOCK", False),
)

