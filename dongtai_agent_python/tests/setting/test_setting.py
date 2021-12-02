import threading
import unittest

from dongtai_agent_python.setting.setting import Setting


class TestSetting(unittest.TestCase):
    def test_multithreading(self):
        def test(name):
            st1 = Setting()
            st1.set_container({'name': name, 'version': '0.1'})
            st1.incr_request_seq()

        thread_num = 5
        for i in range(thread_num):
            t = threading.Thread(target=test, args=['test' + str(i)])
            t.start()

        st = Setting()
        self.assertEqual(thread_num, st.request_seq)


if __name__ == '__main__':
    unittest.main()
