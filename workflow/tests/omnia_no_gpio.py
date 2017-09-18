from workflow.tests.omnia import (
    TESTS as ORIG_TESTS, GpioTest
)

TESTS = [e for e in ORIG_TESTS if not isinstance(e, GpioTest)]
