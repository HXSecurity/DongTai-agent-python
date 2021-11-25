import threading
import unittest

from dongtai_agent_python.utils.scope import current_scope, in_scope, scope


class TestScope(unittest.TestCase):
    def test_scope(self):
        self.assertEqual('', current_scope())
        self.assertFalse(in_scope('test1'))

        with scope('test1'):
            self.assertEqual('test1', current_scope())
            self.assertTrue(in_scope('test1'))
            self.assertFalse(in_scope('test2'))

            with scope('test2'):
                self.assertEqual('test2', current_scope())
                self.assertTrue(in_scope('test1'))
                self.assertTrue(in_scope('test2'))
                self.assertEqual('test2', current_scope())

            self.assertFalse(in_scope('test2'))
            self.assertTrue(in_scope('test1'))
        self.assertFalse(in_scope('test1'))

    def test_multithreading(self):
        thread_num = 5
        for i in range(thread_num):
            t = threading.Thread(target=self.test_scope)
            t.start()
