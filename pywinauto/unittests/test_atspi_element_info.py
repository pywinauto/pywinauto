# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Tests for Linux AtspiElementInfo"""

import os
import sys
import subprocess
import time
import unittest
import re
import six
import mock
import ctypes

if sys.platform.startswith("linux"):
    sys.path.append(".")
    from pywinauto.linux.atspi_objects import AtspiAccessible
    from pywinauto.linux.atspi_objects import AtspiDocument
    from pywinauto.linux.atspi_objects import AtspiImage
    from pywinauto.linux.atspi_objects import _AtspiRect
    from pywinauto.linux.atspi_objects import RECT
    from pywinauto.linux.atspi_objects import _AtspiPoint
    from pywinauto.linux.atspi_objects import POINT
    from pywinauto.linux.atspi_objects import _AtspiCoordType
    from pywinauto.linux.atspi_objects import _GError
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.atspi_objects import IATSPI
    from pywinauto.linux.application import Application
    from pywinauto.linux.atspi_objects import GHashTable
    from pywinauto.linux.atspi_objects import _find_library

app_name = r"gtk_example.py"


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


if sys.platform.startswith("linux"):
    class AtspiPointTests(unittest.TestCase):

        """Unit tests for AtspiPoint class"""

        def test_indexation(self):
            p = POINT(1, 2)
            self.assertEqual(p[0], p.x)
            self.assertEqual(p[1], p.y)
            self.assertEqual(p[-2], p.x)
            self.assertEqual(p[-1], p.y)
            self.assertRaises(IndexError, lambda: p[2])
            self.assertRaises(IndexError, lambda: p[-3])

        def test_iteration(self):
            p = POINT(1, 2)
            self.assertEqual([1, 2], [i for i in p])

        def test_equal(self):
            p0 = POINT(1, 2)
            p1 = POINT(0, 2)
            self.assertNotEqual(p0, p1)
            p1.x = p0.x
            self.assertEqual(p0, p1)


    class AtspiElementInfoTests(unittest.TestCase):

        """Unit tests for the AtspiElementInfo class"""

        def get_app(self, name):
            for children in self.desktop_info.children():
                if children.name == name:
                    return children
            raise Exception("Application not found")

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.app = Application()
            self.app.start(_test_app())
            time.sleep(1)
            self.app_info = self.get_app(app_name)

        def tearDown(self):
            self.app.kill()

        def test_can_get_desktop(self):
            self.assertEqual(self.desktop_info.control_type, "DesktopFrame")

        def test_can_get_childrens(self):
            apps = [children.name for children in self.desktop_info.children()]
            self.assertTrue(app_name in apps)

        def test_can_get_name(self):
            self.assertEqual(self.desktop_info.name, "main")

        def test_can_get_parent(self):
            parent = self.app_info.parent
            self.assertEqual(parent.control_type, "DesktopFrame")

        def test_can_get_process_id(self):
            self.assertEqual(self.app_info.process_id, self.app.process)

        def test_can_get_class_name(self):
            self.assertEqual(self.app_info.class_name, "Application")

        def test_can_get_control_type_property(self):
            self.assertEqual(self.app_info.control_type, "Application")

        def test_can_get_control_type_of_all_app_descendants(self):
            print(self.app_info.descendants())
            for children in self.app_info.descendants():
                self.assertTrue(children.control_type in IATSPI().known_control_types.keys())

        def test_control_type_equal_class_name(self):
            for children in self.app_info.descendants():
                self.assertEqual(children.control_type, children.class_name)

        def test_can_get_description(self):
            # TODO find a way to add meaningful description to example application
            self.assertEqual(self.app_info.description(), "")

        def test_can_get_framework_id(self):
            dpkg_output = subprocess.check_output(["dpkg", "-s", "libgtk-3-0"]).decode(encoding='UTF-8')
            version_line = None
            for line in dpkg_output.split("\n"):
                if line.startswith("Version"):
                    version_line = line
                    break
            print(version_line)
            if version_line is None:
                raise Exception("Cant get system gtk version")
            version_pattern = "Version:\\s+(\\d+\\.\\d+\\.\\d+).*"
            r_version = re.compile(version_pattern, flags=re.MULTILINE)
            res = r_version.match(version_line)
            gtk_version = res.group(1)
            self.assertEqual(self.app_info.framework_id(), gtk_version)

        def test_can_get_framework_name(self):
            self.assertEqual(self.app_info.framework_name(), "gtk")

        def test_can_get_atspi_version(self):
            # TODO Get atspi version from loaded so
            version = self.app_info.atspi_version()
            self.assertTrue(version in ["2.0", "2.1"], msg="Unexpected AT-SPI version: {}".format(version))

        def test_can_get_rectangle(self):
            app_info = self.get_app(app_name)
            frame = app_info.children()[0]
            filler = frame.children()[0]
            rectangle = filler.rectangle
            self.assertEqual(rectangle.width(), 600)
            self.assertAlmostEqual(rectangle.height(), 450, delta=50)

        def test_can_compare_applications(self):
            app_info = self.get_app(app_name)
            app_info1 = self.get_app(app_name)
            assert app_info == app_info1

        def test_can_compare_desktop(self):
            desktop = AtspiElementInfo()
            desktop1 = AtspiElementInfo()
            assert desktop == desktop1

        def test_can_get_layer(self):
            self.assertEqual(self.desktop_info.get_layer(), 3)

        def test_can_get_order(self):
            self.assertEqual(self.desktop_info.get_order(), 0)

        def test_can_get_state_set(self):
            frame_info = self.app_info.children()[0]
            states = frame_info.get_state_set()
            self.assertIn('STATE_VISIBLE', states)

        def test_visible(self):
            frame_info = self.app_info.children()[0]
            self.assertTrue(frame_info.visible)

        def test_service_is_not_visible(self):
            desktop = AtspiElementInfo()
            service = None
            # we suppose the app running as a service doesn't have children
            for c in desktop.children():
                if not c.children():
                    service = c
                    break
            self.assertFalse(service.visible)

        def test_enabled(self):
            frame_info = self.app_info.children()[0]
            self.assertTrue(frame_info.enabled)


    class AtspiElementInfoDocumentMockedTests(unittest.TestCase):        """Mocked unit tests for the AtspiElementInfo.document related functionality"""

        def setUp(self):
            self.info = AtspiElementInfo()
            self.patch_get_role = mock.patch.object(AtspiAccessible, 'get_role')
            self.mock_get_role = self.patch_get_role.start()
            self.mock_get_role.return_value = known_control_types.index("Document_frame")

        def tearDown(self):
            self.patch_get_role.stop()

        def test_document_success(self):
            self.assertEqual(type(self.info.document), AtspiDocument)

        def test_document_fail_on_wrong_role(self):
            self.mock_get_role.return_value = known_control_types.index("Invalid")
            self.assertRaises(AttributeError, lambda: self.info.document)

        @mock.patch.object(AtspiDocument, 'get_locale')
        def test_document_get_locale_success(self, mock_get_locale):
            mock_get_locale.return_value = b"C"
            self.assertEqual(self.info.document_get_locale(), u"C")

        @mock.patch.object(AtspiDocument, '_get_locale')
        def test_document_get_locale_gerror_fail(self, mock_get_locale):
            gerror = _GError()
            gerror.code = 222
            gerror.message = b"Mocked GError message"

            def stub_get_locale(atspi_doc_ptr, gerr_pp):
                self.assertEqual(type(atspi_doc_ptr), AtspiAccessible.get_document.restype)
                self.assertEqual(type(gerr_pp), (ctypes.POINTER(ctypes.POINTER(_GError))))
                gerr_pp[0] = ctypes.pointer(gerror)
                return b"C"

            mock_get_locale.side_effect = stub_get_locale

            expected_err_msg = "GError with code: {0}, message: '{1}'".format(
                               gerror.code, gerror.message.decode(encoding='UTF-8'))
            six.assertRaisesRegex(self,
                                  ValueError,
                                  expected_err_msg,
                                  self.info.document_get_locale)

        @mock.patch.object(AtspiDocument, '_get_attribute_value')
        def test_document_get_attribute_value_success(self, mock_get_attribute_value):
            attrib = u"dummy attribute"
            mock_get_attribute_value.return_value = b"dummy val"
            self.assertEqual(self.info.document_get_attribute_value(attrib), u"dummy val")
            self.assertEqual(type(mock_get_attribute_value.call_args[0][1]), ctypes.c_char_p)

        @mock.patch.object(AtspiDocument, '_get_attributes')
        def test_document_get_attributes_success(self, mock_get_attributes):
            attrib = b"dummy attribute"
            mock_get_attributes.return_value = GHashTable.dic2ghash({attrib: b"dummy val"})
            res = self.info.document_get_attributes()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[attrib.decode('utf-8')], u"dummy val")

    class GHashTableTests(unittest.TestCase):

        """Tests manipulating native GHashTable"""

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_ghash2dic(self):
            """Test handling C-created ghash_table with string-based KV pairs"""
            ghash_table_p = GHashTable.dic2ghash({b"key1": b"val1", b"2key": b"value2"})

            dic = GHashTable.ghash2dic(ghash_table_p)
            print(dic)
            self.assertEqual(len(dic), 2)
            self.assertEqual(dic[u"key1"], u"val1")
            self.assertEqual(dic[u"2key"], u"value2")

        @mock.patch.object(subprocess, 'Popen')
        def test_findlibrary(self, mock_popen):
            """Test finding systemt libraries locations"""
            mock_popen.side_effect = IOError
            libs = ["lib0", "lib1", "default_lib"]
            res = _find_library(libs)
            self.assertEqual(res, libs[-1])

            libs = ["default_lib"]
            res = _find_library(libs)
            self.assertEqual(res, libs[-1])

            mock_popen.side_effect = None

            class MockProcess(object):
                def communicate(self):
                    return ["a a a l\nb b b lb\nc c  c lib1\nd d d lib0\n"]
            mock_popen.return_value = MockProcess()
            libs = ["lib0", "lib1", "default_lib"]
            res = _find_library(libs)
            self.assertEqual(res, "lib0")

    class AtspiElementInfoImageMockedTests(unittest.TestCase):

        """Mocked unit tests for the AtspiElementInfo.image related functionality"""

        def setUp(self):
            self.info = AtspiElementInfo()
            self.patch_get_role = mock.patch.object(AtspiAccessible, 'get_role')
            self.mock_get_role = self.patch_get_role.start()
            self.mock_get_role.return_value = IATSPI().known_control_types["Image"]

        def tearDown(self):
            self.patch_get_role.stop()

        def test_image_success(self):
            self.assertEqual(type(self.info.image), AtspiImage)

            # Icon role should be also handled by AtspiImage
            self.mock_get_role.return_value = IATSPI().known_control_types["Icon"]
            iconInfo = AtspiElementInfo()
            self.assertEqual(type(iconInfo.image), AtspiImage)

        def test_image_fail_on_wrong_role(self):
            self.mock_get_role.return_value = IATSPI().known_control_types["Invalid"]
            self.assertRaises(AttributeError, lambda: self.info.image)

        @mock.patch.object(AtspiImage, '_get_image_locale')
        def test_image_get_locale_success(self, mock_get_locale):
            mock_get_locale.return_value = b"I"
            self.assertEqual(self.info.image.get_locale(), b"I")

        @mock.patch.object(AtspiImage, '_get_image_description')
        def test_image_get_description_success(self, mock_get_description):
            mock_get_description.return_value = b"descr"
            self.assertEqual(self.info.image.get_description(), b"descr")

        @mock.patch.object(AtspiImage, '_get_image_extents')
        def test_image_get_image_extents_success(self, mock_get_extents):
            extents_rect = _AtspiRect(22, 11, 33, 44)
            mock_get_extents.return_value = ctypes.pointer(extents_rect)
            self.assertEqual(self.info.image.get_extents(), RECT(extents_rect))
            self.assertEqual(mock_get_extents.call_args[0][1],
                             _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW)

        @mock.patch.object(AtspiImage, '_get_image_position')
        def test_image_get_image_position_success(self, mock_get_position):
            pnt = _AtspiPoint()
            pnt.x = 55
            pnt.y = 66
            mock_get_position.return_value = ctypes.pointer(pnt)
            self.assertEqual(self.info.image.get_position(), POINT(pnt.x, pnt.y))
            self.assertEqual(mock_get_position.call_args[0][1],
                             _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW)


if __name__ == "__main__":
    unittest.main()
