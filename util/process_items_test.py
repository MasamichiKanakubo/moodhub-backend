import unittest
from process_items import process_items

class TestProcessItems(unittest.TestCase):

    def test_process_items(self):
        items = [1, 2, 3, 4, 5]
        expected_results = [1, 4, 9, 16, 25]

        results = process_items(items)

        self.assertEqual(results, expected_results)

if __name__ == '__main__':
    unittest.main()