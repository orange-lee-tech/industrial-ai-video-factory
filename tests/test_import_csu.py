import unittest
from scripts.import_csu import load_first_sheet
class ImportTests(unittest.TestCase):
    def test_missing_input(self):
        with self.assertRaises(FileNotFoundError): load_first_sheet('does-not-exist.xlsx')
if __name__=='__main__': unittest.main()
