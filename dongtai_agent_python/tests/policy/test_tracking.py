import unittest

from dongtai_agent_python.policy import tracking


class TestTracking(unittest.TestCase):
    def test_yaml_load_is_safe(self):
        try:
            import yaml
            self.assertFalse(tracking.yaml_load_is_safe(('test', yaml.UnsafeLoader), None))
            self.assertFalse(tracking.yaml_load_is_safe(('test',), {'Loader': yaml.UnsafeLoader}))
            self.assertTrue(tracking.yaml_load_is_safe(('test',), None))

            yaml.__version__ = '5.0'
            self.assertFalse(tracking.yaml_load_is_safe(('test',), None))
        except ImportError:
            pass


if __name__ == '__main__':
    unittest.main()
