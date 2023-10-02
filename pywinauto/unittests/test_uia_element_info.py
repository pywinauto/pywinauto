import unittest
import os
import sys
import mock

sys.path.append(".")
from pywinauto.windows.application import Application  # noqa: E402
from pywinauto.handleprops import processid  # noqa: E402
from pywinauto.sysinfo import is_x64_Python  # noqa: E402
from pywinauto.sysinfo import UIA_support  # noqa: E402
from pywinauto.timings import Timings  # noqa: E402

if UIA_support:
    from pywinauto.windows.uia_element_info import UIAElementInfo, UIACondition
    from pywinauto.windows.uia_defines import IUIA

mfc_samples_folder = os.path.join(
    os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')
wpf_app_1 = os.path.join(mfc_samples_folder, u"WpfApplication1.exe")

if UIA_support:
    class UIAConditionTests(unittest.TestCase):
        def test_condition_ex_returns_bool_condition(self):
            condition = UIACondition.create_bool(True)
            self.assertIs(condition.condition, IUIA().true_condition)
            cond = condition.condition_ex
            self.assertIsInstance(cond, IUIA().UIA_dll.IUIAutomationBoolCondition)
            self.assertTrue(cond.BooleanValue)
            condition = UIACondition.create_bool(False)
            self.assertIs(condition.condition, IUIA().false_condition)
            cond = condition.condition_ex
            self.assertIsInstance(cond, IUIA().UIA_dll.IUIAutomationBoolCondition)
            self.assertFalse(cond.BooleanValue)

        def test_condition_ex_returns_property_condition(self):
            cond = UIACondition.create_property('Name', 'Foo').condition_ex
            self.assertIsInstance(cond, IUIA().UIA_dll.IUIAutomationPropertyCondition)
            self.assertEqual(cond.propertyId, IUIA().UIA_dll.UIA_NamePropertyId)
            self.assertEqual(cond.PropertyValue, 'Foo')

        @unittest.skipUnless(
            hasattr(IUIA().UIA_dll, "PropertyConditionFlags_None"),
            'The UIA dll in this env does not support PropertyConditionFlags_None',
        )
        def test_condition_ex_returns_property_condition_with_none_flags(self):
            cond = UIACondition.create_property('Name', 'Foo', 'none').condition_ex
            self.assertEqual(cond.propertyId, IUIA().UIA_dll.UIA_NamePropertyId)
            self.assertEqual(cond.PropertyValue, 'Foo')
            self.assertEqual(cond.PropertyConditionFlags, IUIA().UIA_dll.PropertyConditionFlags_None)

        @unittest.skipUnless(
            hasattr(IUIA().UIA_dll, "PropertyConditionFlags_IgnoreCase"),
            'The UIA dll in this env does not support PropertyConditionFlags_IgnoreCase',
        )
        def test_condition_ex_returns_property_condition_with_ignore_case_flags(self):
            cond = UIACondition.create_property('Name', 'Foo', 'ignore_case').condition_ex
            self.assertEqual(cond.propertyId, IUIA().UIA_dll.UIA_NamePropertyId)
            self.assertEqual(cond.PropertyValue, 'Foo')
            self.assertEqual(cond.PropertyConditionFlags, IUIA().UIA_dll.PropertyConditionFlags_IgnoreCase)

        @unittest.skipUnless(
            hasattr(IUIA().UIA_dll, "PropertyConditionFlags_MatchSubstring"),
            'The UIA dll in this env does not support PropertyConditionFlags_MatchSubstring',
        )
        def test_condition_ex_returns_property_condition_with_match_substring_flags(self):
            cond = UIACondition.create_property('Name', 'Foo', 'match_substring').condition_ex
            self.assertEqual(cond.propertyId, IUIA().UIA_dll.UIA_NamePropertyId)
            self.assertEqual(cond.PropertyValue, 'Foo')
            self.assertEqual(cond.PropertyConditionFlags, IUIA().UIA_dll.PropertyConditionFlags_MatchSubstring)

        def test_condition_ex_returns_not_condition(self):
            cond = (~UIACondition.create_bool(True)).condition_ex
            self.assertIsInstance(cond, IUIA().UIA_dll.IUIAutomationNotCondition)
            self.assertTrue(cond.GetChild().QueryInterface(IUIA().UIA_dll.IUIAutomationBoolCondition).BooleanValue)

        def test_condition_ex_returns_or_condition(self):
            cond = (UIACondition.create_bool(True) | UIACondition.create_bool(False)).condition_ex
            self.assertIsInstance(cond, IUIA().UIA_dll.IUIAutomationOrCondition)
            self.assertEqual(cond.ChildCount, 2)
            for ch, expected in zip(cond.GetChildren(), (True, False)):
                actual = ch.QueryInterface(IUIA().UIA_dll.IUIAutomationBoolCondition).BooleanValue
                self.assertEqual(expected, actual)

        def test_condition_ex_returns_and_condition(self):
            cond = (UIACondition.create_bool(True) & UIACondition.create_bool(False)).condition_ex
            self.assertIsInstance(cond, IUIA().UIA_dll.IUIAutomationAndCondition)
            self.assertEqual(cond.ChildCount, 2)
            for ch, expected in zip(cond.GetChildren(), (True, False)):
                actual = ch.QueryInterface(IUIA().UIA_dll.IUIAutomationBoolCondition).BooleanValue
                self.assertEqual(expected, actual)

        def test_create_or_condition_from_array(self):
            cond = UIACondition.from_array("or", [
                UIACondition.create_property('Name', 'Foo'),
                UIACondition.create_property('Name', 'Bar'),
                UIACondition.create_control_type('Button'),
                UIACondition.create_property('ProcessId', 1),
            ]).condition.QueryInterface(IUIA().UIA_dll.IUIAutomationOrCondition)
            self.assertEqual(cond.ChildCount, 4)
            expected_ids = (
                IUIA().UIA_dll.UIA_NamePropertyId,
                IUIA().UIA_dll.UIA_NamePropertyId,
                IUIA().UIA_dll.UIA_ControlTypePropertyId,
                IUIA().UIA_dll.UIA_ProcessIdPropertyId,
            )
            expected_values = ('Foo', 'Bar', IUIA().UIA_dll.UIA_ButtonControlTypeId, 1)
            for ch, prop_id, value in zip(cond.GetChildren(), expected_ids, expected_values):
                child = ch.QueryInterface(IUIA().UIA_dll.IUIAutomationPropertyCondition)
                self.assertEqual(child.propertyId, prop_id)
                self.assertEqual(child.PropertyValue, value)

        def test_create_and_condition_from_array(self):
            cond = UIACondition.from_array("and", [
                UIACondition.create_property('Name', 'Spam'),
                UIACondition.create_property('ClassName', 'Button'),
                UIACondition.create_property('IsContentElement', True),
            ]).condition.QueryInterface(IUIA().UIA_dll.IUIAutomationAndCondition)
            self.assertEqual(cond.ChildCount, 3)
            expected_ids = (
                IUIA().UIA_dll.UIA_NamePropertyId,
                IUIA().UIA_dll.UIA_ClassNamePropertyId,
                IUIA().UIA_dll.UIA_IsContentElementPropertyId,
            )
            expected_values = ('Spam', 'Button', True)
            for ch, prop_id, value in zip(cond.GetChildren(), expected_ids, expected_values):
                child = ch.QueryInterface(IUIA().UIA_dll.IUIAutomationPropertyCondition)
                self.assertEqual(child.propertyId, prop_id)
                self.assertEqual(child.PropertyValue, value)

        def test_inplace_operators(self):
            condition = UIACondition.create_control_type('SplitButton')
            condition |= UIACondition.create_control_type('Button')
            condition &= UIACondition.create_property('Name', 'Foo')
            cond = condition.condition_ex
            ctrl_or_condition, name_condition = (UIACondition(c) for c in cond.GetChildren())
            splitbtn_condition, btn_condition = (UIACondition(c) for c in ctrl_or_condition.condition_ex.GetChildren())
            splitbtn_cond = splitbtn_condition.condition_ex
            self.assertEqual(splitbtn_cond.propertyId, IUIA().UIA_dll.UIA_ControlTypePropertyId)
            self.assertEqual(splitbtn_cond.PropertyValue, IUIA().UIA_dll.UIA_SplitButtonControlTypeId)
            btn_cond = btn_condition.condition_ex
            self.assertEqual(btn_cond.propertyId, IUIA().UIA_dll.UIA_ControlTypePropertyId)
            self.assertEqual(btn_cond.PropertyValue, IUIA().UIA_dll.UIA_ButtonControlTypeId)
            name_cond = name_condition.condition_ex
            self.assertEqual(name_cond.propertyId, IUIA().UIA_dll.UIA_NamePropertyId)
            self.assertEqual(name_cond.PropertyValue, 'Foo')

        def test_takes_invalid_params(self):
            with self.assertRaises(TypeError):
                UIACondition.create_property(object(), 'Foo')  # type: ignore
            with self.assertRaises(TypeError):
                UIACondition.create_property('Name', 'Foo', object())  # type: ignore
            with self.assertRaises(TypeError):
                UIACondition.create_control_type(object())  # type: ignore
            with self.assertRaises(TypeError):
                UIACondition.from_array("nor", [])  # type: ignore

    class UIAElementInfoTests(unittest.TestCase):

        """Unit tests for the UIElementInfo class"""

        def setUp(self):
            """Set some data and ensure the application is in the state we want"""
            Timings.slow()

            self.app = Application(backend="uia")
            self.app = self.app.start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.handle = self.dlg.handle
            self.ctrl = UIAElementInfo(self.handle)

        def tearDown(self):
            """Close the application after tests"""
            self.app.kill()

        def testHash(self):
            """Test element info hashing"""
            d = { self.ctrl : "elem" }
            self.assertEqual(d[self.ctrl], "elem")

        def testProcessId(self):
            """Test process_id equals"""
            self.assertEqual(self.ctrl.process_id, processid(self.handle))

        def testName(self):
            """Test application name equals"""
            self.assertEqual(self.ctrl.name, "WPF Sample Application")

        def testHandle(self):
            """Test application handle equals"""
            self.assertEqual(self.ctrl.handle, self.handle)

        def testEnabled(self):
            """Test whether the element is enabled"""
            self.assertEqual(self.ctrl.enabled, True)

        def testVisible(self):
            """Test whether the element is visible"""
            self.assertEqual(self.ctrl.visible, True)

        def test_value_not_available(self):
            """Test correct handling case if ValuePattern is not available for element"""
            self.assertEqual(self.ctrl.value, "")

        def test_legacy_name(self):
            """Test application name from legacy pattern equals"""
            self.assertEqual(self.ctrl.legacy_name, "WPF Sample Application")

        def test_legacy_help(self):
            """Test get help string"""
            self.assertEqual(self.ctrl.legacy_help, "")

        def test_accelerator(self):
            """Test get AcceleratorKey value"""
            self.assertEqual(self.ctrl.accelerator, "")

        def testChildren(self):
            """Test whether a list of only immediate children of the element is equal"""
            self.assertEqual(len(self.ctrl.children()), 5)

        def test_children_generator(self):
            """Test whether children generator iterates over correct elements"""
            children = [child for child in self.ctrl.iter_children()]
            self.assertSequenceEqual(self.ctrl.children(), children)

        def test_default_depth_descendants(self):
            """Test whether a list of descendants with default depth of the element is equal"""
            self.assertEqual(len(self.ctrl.descendants(depth=None)), len(self.ctrl.descendants()))

        def test_depth_level_one_descendants(self):
            """Test whether a list of descendants with depth=1 of the element is equal to children set"""
            self.assertEqual(len(self.ctrl.descendants(depth=1)), len(self.ctrl.children()))

        def test_depth_level_three_descendants(self):
            """Test whether a list of descendants with depth=3 of the element is equal"""
            descendants = self.ctrl.children()

            level_two_children = []
            for element in descendants:
                level_two_children.extend(element.children())
            descendants.extend(level_two_children)

            level_three_children = []
            for element in level_two_children:
                level_three_children.extend(element.children())
            descendants.extend(level_three_children)

            self.assertEqual(len(self.ctrl.descendants(depth=3)), len(descendants))

        def test_invalid_depth_descendants(self):
            """Test whether a list of descendants with invalid depth raises exception"""
            self.assertRaises(Exception, self.ctrl.descendants, depth='qwerty')

        def test_default_depth_with_criteria_descendants(self):
            """Test whether a list of descendants with default depth and same criteria of the element is equal"""
            self.assertEqual(
                len(self.ctrl.descendants(depth=None, control_type="RadioButton")),
                len(self.ctrl.descendants(control_type="RadioButton")),
            )

        def test_default_and_specified_depth_level_with_criteria_descendants(self):
            """Test whether specifying a depth level will find fewer elements than without specifying it"""
            self.assertLess(
                len(self.ctrl.descendants(control_type="Text", depth=2)),
                len(self.ctrl.descendants(control_type="Text")),
            )

        def test_depth_level_one_with_criteria_descendants(self):
            """Test whether a list of descendants with depth=1 and same criteria of the element is equal to children"""
            self.assertEqual(
                self.ctrl.children(control_type="ToolBar"), self.ctrl.descendants(control_type="ToolBar", depth=1)
            )

        def test_depth_level_more_than_one_with_criteria_descendants(self):
            """Test whether an element not found with smaller depth levels is found with larger levels"""
            # There is no element with `control_type='ScrollBar'` with depth level less than three
            nothing = next(iter(self.ctrl.descendants(control_type="Slider", depth=2)), None)
            self.assertIsNone(nothing)
            slider = next(iter(self.ctrl.descendants(control_type="Slider", depth=3)), None)
            self.assertIsNotNone(slider)
            self.assertIn(slider, self.ctrl.descendants())

        def test_descendants_generator(self):
            """Test whether descendant generator iterates over correct elements"""
            descendants = [desc for desc in self.ctrl.iter_descendants(depth=3)]
            self.assertSequenceEqual(self.ctrl.descendants(depth=3), descendants)


    class UIAElementInfoRawViewWalkerTests(UIAElementInfoTests):

        """Unit tests for the UIAElementInfo class with enabled RawViewWalker implementation"""

        def setUp(self):
            self.default_use_raw_view_walker = UIAElementInfo.use_raw_view_walker
            UIAElementInfo.use_raw_view_walker = True
            super(UIAElementInfoRawViewWalkerTests, self).setUp()

        def tearDown(self):
            UIAElementInfo.use_raw_view_walker = self.default_use_raw_view_walker
            super(UIAElementInfoRawViewWalkerTests, self).tearDown()

        def test_use_findall_children(self):
            """Test use FindAll inside children method"""
            with mock.patch.object(self.ctrl._element, 'FindAll', wraps=self.ctrl._element.FindAll) as mock_findall:
                UIAElementInfo.use_raw_view_walker = False
                self.ctrl.children()
                self.assertEqual(mock_findall.call_count, 1)

                UIAElementInfo.use_raw_view_walker = True
                self.ctrl.children()
                self.assertEqual(mock_findall.call_count, 1)

        def test_use_findall_descendants(self):
            """Test use FindAll inside descendants method"""
            with mock.patch.object(self.ctrl._element, 'FindAll', wraps=self.ctrl._element.FindAll) as mock_findall:
                UIAElementInfo.use_raw_view_walker = False
                self.ctrl.descendants(depth=1)
                self.assertEqual(mock_findall.call_count, 1)

                UIAElementInfo.use_raw_view_walker = True
                self.ctrl.descendants(depth=1)
                self.assertEqual(mock_findall.call_count, 1)

        def test_use_create_tree_walker_iter_children(self):
            """Test use CreateTreeWalker inside iter_children method"""
            with mock.patch.object(IUIA().iuia, 'CreateTreeWalker', wraps=IUIA().iuia.CreateTreeWalker) as mock_create:
                UIAElementInfo.use_raw_view_walker = False
                next(self.ctrl.iter_children())
                self.assertEqual(mock_create.call_count, 1)

                UIAElementInfo.use_raw_view_walker = True
                next(self.ctrl.iter_children())
                self.assertEqual(mock_create.call_count, 1)

        def test_use_create_tree_walker_iter_descendants(self):
            """Test use CreateTreeWalker inside iter_descendants method"""
            with mock.patch.object(IUIA().iuia, 'CreateTreeWalker', wraps=IUIA().iuia.CreateTreeWalker) as mock_create:
                UIAElementInfo.use_raw_view_walker = False
                next(self.ctrl.iter_descendants(depth=3))
                self.assertEqual(mock_create.call_count, 1)

                UIAElementInfo.use_raw_view_walker = True
                next(self.ctrl.iter_descendants(depth=3))
                self.assertEqual(mock_create.call_count, 1)

if __name__ == "__main__":
    if UIA_support:
        unittest.main()
