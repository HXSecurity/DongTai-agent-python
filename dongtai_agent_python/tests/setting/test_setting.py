import multiprocessing
import os
import threading
import time
import unittest

from dongtai_agent_python.setting.setting import Setting


class TestSetting(unittest.TestCase):
    def test_multithreading(self):
        def test_mt(name):
            st1 = Setting()
            st1.shm = None
            st1.set_shm("test-setting-001")
            st1.set_container({'name': name, 'version': '0.1'})
            st1.incr_request_seq()

        thread_num = 5
        for i in range(thread_num):
            t = threading.Thread(target=test_mt, args=['test' + str(i)])
            t.start()

        st = Setting()
        st.shm = None
        st.set_shm("test-setting-001")
        time.sleep(1)
        self.assertEqual(thread_num, st.request_seq)

    def test_multiprocessing(self):
        if os.name == "nt":
            return

        def test_mp(name):
            st1 = Setting()
            st1.shm = None
            st1.set_shm("test-setting-002")
            st1.set_container({'name': name, 'version': '0.1'})
            st1.incr_request_seq()

        process_num = 5
        for i in range(process_num):
            p = multiprocessing.Process(target=test_mp, args=('test' + str(i),))
            p.start()

        st = Setting()
        st.shm = None
        st.set_shm("test-setting-002")
        time.sleep(1)
        self.assertEqual(process_num, st.request_seq)


if __name__ == '__main__':
    unittest.main()
