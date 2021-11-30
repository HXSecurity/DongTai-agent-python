import threading
import unittest

from dongtai_agent_python.utils.singleton import Singleton


class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        class Test(Singleton):
            def init(self, seq=0):
                self.seq = seq

            def incr(self):
                self.seq = self.seq + 1

        s1 = Test(1)
        s2 = Test(2)
        self.assertEqual(s1, s2)
        self.assertEqual(1, s1.seq)

        s1.incr()
        s2.incr()
        self.assertEqual(3, s1.seq)

    def test_multithreading(self):
        class Test(Singleton):
            def init(self, seq=0):
                self.seq = seq

            def incr(self):
                self.seq = self.seq + 1

        def test_incr():
            s1 = Test()
            s1.incr()

        thread_num = 5
        for i in range(thread_num):
            t = threading.Thread(target=test_incr)
            t.start()

        s = Test()
        self.assertEqual(thread_num, s.seq)
