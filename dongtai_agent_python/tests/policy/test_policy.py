import unittest

from dongtai_agent_python.policy import policy
from dongtai_agent_python.setting import const


class TestPolicy(unittest.TestCase):
    def test_policy_rule(self):
        detail = {
            "track": "true",
            "value": "os.system",
            "inherit": "false"
        }
        # invalid rule type
        p = policy.new_policy_rule(-1, detail)
        self.assertIsNone(p)

        detail = {
            "track": "true",
            "value": "os.system",
            "inherit": "false"
        }
        p = policy.new_policy_rule(const.NODE_TYPE_PROPAGATOR, detail)
        self.assertTrue(p.source_from.from_all_parameters)
        self.assertTrue(p.target_from.from_return)

        detail = {
            "source": "P1,4,k5,3,k2",
            "track": "true",
            "target": "R",
            "value": "os.system",
            "inherit": "false"
        }
        p = policy.new_policy_rule(const.NODE_TYPE_PROPAGATOR, detail)
        self.assertFalse(p.source_from.from_object)
        self.assertFalse(p.source_from.from_return)
        self.assertFalse(p.source_from.from_all_parameters)
        self.assertEqual(p.source_from.from_args, set([0, 3, 2]))
        self.assertEqual(p.source_from.from_kwargs, set(['k5', 'k2']))
        self.assertTrue(p.target_from.from_return)
        self.assertFalse(p.target_from.from_object)
        self.assertFalse(p.target_from.from_all_parameters)

        detail = {
            "source": "O",
            "track": "true",
            "target": "P1",
            "value": "os.system",
            "inherit": "false"
        }
        p = policy.new_policy_rule(const.NODE_TYPE_PROPAGATOR, detail)
        self.assertTrue(p.source_from.from_object)
        self.assertFalse(p.source_from.from_return)
        self.assertFalse(p.source_from.from_all_parameters)
        self.assertEqual(p.target_from.from_args, set([0]))

        detail = {
            "source": "O|P",
            "track": "true",
            "target": "O|R",
            "value": "os.system",
            "inherit": "false"
        }
        p = policy.new_policy_rule(const.NODE_TYPE_PROPAGATOR, detail)
        self.assertTrue(p.source_from.from_object)
        self.assertFalse(p.source_from.from_return)
        self.assertTrue(p.source_from.from_all_parameters)
        self.assertTrue(p.target_from.from_object)
        self.assertTrue(p.target_from.from_return)
        self.assertFalse(p.target_from.from_all_parameters)


if __name__ == '__main__':
    unittest.main()
