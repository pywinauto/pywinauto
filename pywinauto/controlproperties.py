# GUI Application automation and testing library
# Copyright (C) 2006-2018 Mark Mc Mahon and Contributors
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

"""Wrap"""
from .win32structures import RECT, LOGFONTW
from . import deprecated


#====================================================================
class FuncWrapper(object):

    """Little class to allow attribute access to return a callable object"""

    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        """Return the saved value"""
        return self.value


#====================================================================
class ControlProps(dict):

    """Wrap controls read from a file to resemble hwnd controls"""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        self.ref = None
        #self.menu_items = []

    def __getattr__(self, attr):
        # if the key is not in the dictionary but the plural is
        if attr not in self and attr + "s" in self:
            # return the first element of the possible list item
            return FuncWrapper(self[attr+'s'][0])

        return FuncWrapper(self[attr])

    #def friendly_class_name(self):
    #    print "sdafafasdfafasdfasdf",
    #    try:
    #        print "---", self['friendly_class_name']
    #    except Exception as e:
    #        print "fffffffffffffffffffff"
    #        print `e`
    #    return self['friendly_class_name']

    def window_text(self):
        return self['texts'][0]
    # Non PEP-8 alias
    WindowText = deprecated(window_text)

    def has_style(self, style):
        return self['style'] & style == style
    # Non PEP-8 alias
    HasStyle = deprecated(has_style)

    def has_exstyle(self, exstyle):
        return self['exstyle'] & exstyle == exstyle
    # Non PEP-8 alias
    HasExStyle = deprecated(has_exstyle, deprecated_name="HasExStyle")


#====================================================================
def GetMenuBlocks(ctrls):
    allMenuBlocks = []
    for ctrl in ctrls:
        if 'menu_items' in ctrl.keys():
            # we need to get all the separate menu blocks!
            menuBlocks = MenuBlockAsControls(ctrl.menu_items())
            allMenuBlocks.extend(menuBlocks)

    return allMenuBlocks


#====================================================================
def MenuBlockAsControls(menuItems, parentage = None):

    if parentage is None:
        parentage = []
    blocks = []

    curBlock = []
    for item in menuItems:

        # do a bit of conversion first :-)
        itemAsCtrl = MenuItemAsControl(item)

        # update the friendly_class_name to contain the 'path' to
        # this particular item
        # TODO: CHECK - as itemPath is currently unused!
        if parentage:
            itemPath = "%s->%s" % ("->".join(parentage), item['text'])
        else:
            itemPath = item['text']

        #append the item to the current menu block
        curBlock.append(itemAsCtrl)

        # If the item has a sub menu
        if 'menu_items' in item.keys():

            # add the current item the path
            parentage.append(item['text'])

            # Get the block for the SubMenu, and add it to the list of
            # blocks we have found
            blocks.extend(
                MenuBlockAsControls(
                    item['menu_items']['menu_items'], parentage))

            # and seeing as we are dong with that sub menu remove the current
            # item from the path
            del(parentage[-1])

    # add the current block to the list of blocks
    blocks.append(curBlock)

    return blocks


#====================================================================
def MenuItemAsControl(menuItem):
    """Make a menu item look like a control for tests"""
    itemAsCtrl = ControlProps()

    itemAsCtrl["texts"] = [menuItem['text'], ]
    itemAsCtrl["control_id"] = menuItem['id']
    itemAsCtrl["type"] = menuItem['type']
    itemAsCtrl["state"] = menuItem['state']

    itemAsCtrl["class_name"] = "MenuItem"
    itemAsCtrl["friendly_class_name"] = "MenuItem"

    # as most of these don't matter - just set them up with default stuff
    itemAsCtrl["rectangle"] = RECT(0, 0, 999, 999)
    itemAsCtrl["fonts"] = [LOGFONTW(), ]
    itemAsCtrl["client_rects"] = [RECT(0, 0, 999, 999), ]
    itemAsCtrl["context_help_id"] = 0
    itemAsCtrl["user_data"]  = 0
    itemAsCtrl["style"] = 0
    itemAsCtrl["exstyle"] = 0
    itemAsCtrl["is_visible"] = 1

    return itemAsCtrl


#====================================================================
def SetReferenceControls(controls, refControls):
    """Set the reference controls for the controls passed in

    This does some minor checking as following:
     * test that there are the same number of reference controls as
       controls - fails with an exception if there are not
     * test if all the ID's are the same or not
    """

    # numbers of controls must be the same (though in future I could imagine
    # relaxing this constraint)

    if len(controls) != len(refControls):
        raise RuntimeError(
            "Numbers of controls on ref. dialog does not match Loc. dialog")

    # set the controls
    for i, ctrl in enumerate(controls):
        ctrl.ref = refControls[i]

    toRet = 1
    allIDsSameFlag = 2
    allClassesSameFlag = 4

    # find if all the control id's match
    if  [ctrl.control_id() for ctrl in controls] == \
            [ctrl.control_id() for ctrl in refControls]:

        toRet += allIDsSameFlag

    # check if the control classes match
    if [ctrl.class_name() for ctrl in controls] == \
       [ctrl.class_name() for ctrl in refControls]:

        toRet += allClassesSameFlag

    return toRet



##====================================================================
#class ControlProps(dict):
#    #----------------------------------------------------------------
#    def __init__(self, props = {}):
#        # default to having menuItems for all things
#        self.menu_items = []
#
#        self.update(props)
#        #for x in props:
#            #self[x] = props[x]
#
#        if hasattr(props, "handle"):
#            self.__dict__['handle'] = props.handle
#        else:
#            self.__dict__['handle'] = None
#
#        self.__dict__['ref'] = None
#
#    #----------------------------------------------------------------
#    # handles attribute access for dictionary items and
#    # for plurals (e.g. if self.fonts = [4, 2] then self.font = 4)
#    def __getattr__(self, key):
#
#        # if the key is not in the dictionary but the plural is
#        if key not in self and key + "s" in self:
#
#            # try to get the first element of the possible list item
#            try:
#                return self[key + "s"][0]
#            except TypeError as e:
#                pass
#
#        if key in self:
#            return self[key]
#
#        return self.__dict__[key]
#
#    #----------------------------------------------------------------
#    def __setattr__(self, key, value):
#        if key in self.__dict__:
#            self.__dict__[key] = value
#        else:
#            self[key] = value
#
#    #----------------------------------------------------------------
#    def has_style(self, flag):
#        return self.style & flag == flag
#
#    #----------------------------------------------------------------
#    def has_exstyle(self, flag):
#        return self.exstyle & flag == flag
#
#
