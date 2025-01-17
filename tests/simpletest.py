import unittest
from configpy.configure import ConfigBuild


def multiply(a, b):
    return a * b 

def add(a,b):
    return a + b

def subtract(a, b):
    return a - b

myconfig = ConfigBuild(obj = add,
                        a = 10, 
                        b = ConfigBuild(obj = subtract,
                                        a = 10, b = ConfigBuild(obj = multiply,
                                                            a = 4,
                                                            b = 2)))

json_config = ConfigBuild.from_json('./config.json')

class TestConfig(unittest.TestCase):
    def test_bodmas(self):
        """Test the operations on give numbers"""
        self.assertEqual(myconfig(), 10+(10-4*2))
    def test_json(self):
        self.assertDictEqual(json_config(), {'a': 10, 'b': 2})


if __name__ == "__main__":
    unittest.main()