# https://www.internalpointers.com/post/run-painless-test-suites-python-unittest

import unittest
import test.database_api_tests_message as msg_tests
import test.database_api_tests_user as user_tests
import test.database_api_tests_room as room_tests
import test.chirrup_api_tests

# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(msg_tests))
suite.addTests(loader.loadTestsFromModule(user_tests))
suite.addTests(loader.loadTestsFromModule(room_tests))
suite.addTests(loader.loadTestsFromModule(test.chirrup_api_tests))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)

