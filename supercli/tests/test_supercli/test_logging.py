
import unittest
try:
    import mock
except:
    from unittest import mock

import supercli.logging

class TestTesting( unittest.TestCase ):
    def test_testing(self):
        self.assertEqual( 'a', 'a' )
    def test_testing2(self):
        self.assertEqual( 'a', 'a' )
    def test_testing3(self):
        self.assertEqual( 'a', 'b' )


