import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("lunar_python"), "lunar-python is not installed")
class ComputeFromBirthTest(unittest.TestCase):
    def test_compute_from_birth_returns_public_contract(self):
        from miaosuan_bazi_engine import computeFromBirth

        result = computeFromBirth(
            {
                "name": "Example",
                "gender": "male",
                "datetime": "1990-05-15T14:30:00+08:00",
                "city": "广州",
            }
        )

        self.assertEqual(result["engine"], "miaosuan-bazi-engine")
        self.assertIn("pillars", result)
        self.assertIn("rule", result)
        self.assertIn("tags", result["rule"])
        self.assertIn("day_master", result)
        self.assertEqual(result["input"]["gender"], "男")


if __name__ == "__main__":
    unittest.main()
