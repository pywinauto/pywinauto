import unittest

from pywinauto import UIA_support


class PublicImportsTests(unittest.TestCase):

    def test_top_level_imports(self):
        if UIA_support:
            from pywinauto import ElementNotFoundError, ElementAmbiguousError, WindowNotFoundError, WindowAmbiguousError
            self.assertEqual(len(set([ElementNotFoundError, ElementAmbiguousError, WindowNotFoundError, WindowAmbiguousError])),
                             4)
        else:
            from pywinauto import WindowNotFoundError, WindowAmbiguousError
            self.assertEqual(len(set([WindowNotFoundError, WindowAmbiguousError])),
                             2)

            
if __name__ == "__main__":
    unittest.main()
