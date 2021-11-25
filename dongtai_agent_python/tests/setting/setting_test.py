import os
import threading
import time
import unittest

from dongtai_agent_python.setting.setting import Setting


class TestSetting(unittest.TestCase):
    def test_multithreading(self):
        os.environ['PROJECT_NAME'] = 'test'
        os.environ['AUTO_CREATE_PROJECT'] = '1'

        def test(name):
            st1 = Setting({'name': name, 'version': '0.1'})
            st1.incr_request_seq()

        thread_num = 5
        for i in range(thread_num):
            t = threading.Thread(target=test, args=['test' + str(i)])
            t.start()

        st = Setting()
        self.assertEqual('1', st.auto_create_project)
        self.assertEqual(thread_num, st.request_seq)
        self.assertEqual('test', st.project_name)
        self.assertEqual('test0', st.container.get('name', ''))
