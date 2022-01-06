import unittest

from dongtai_agent_python.utils import utils


class TestUtils(unittest.TestCase):
    def test_get_packages(self):
        packages = utils.get_packages()
        for package in packages:
            print(package)


if __name__ == '__main__':
    unittest.main()
