import unittest


class PublicImportsTests(unittest.TestCase):

    def test_top_level_imports(self):
        from pywinauto import ElementNotFoundError, ElementAmbiguousError, WindowNotFoundError, WindowAmbiguousError
        self.assertEqual(len(set([ElementNotFoundError, ElementAmbiguousError, WindowNotFoundError, WindowAmbiguousError])),
                         4)

            
if __name__ == "__main__":
    unittest.main()
