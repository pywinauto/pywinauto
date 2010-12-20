# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"""Wrap"""

__revision__ = "$Rev: 439 $"

try:
    import pywinauto
except ImportError:
    import sys
    sys.path.append("..")

from pywinauto.win32structures import RECT, LOGFONTW


#====================================================================
class func_wrapper(object):
    "Little class to allow attribute access to return a callable object"
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        "Return the saved value"
        return self.value


#====================================================================
class ControlProps(dict):
    "Wrap controls read from a file to resemble hwnd controls"

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        self.ref = None
        #self.MenuItems = []

    def __getattr__(self, attr):
        # if the key is not in the dictionary but the plural is
        if attr not in self and attr + "s" in self:
            # return the first element of the possible list item
            return func_wrapper(self[attr+'s'][0])

        return func_wrapper(self[attr])

    #def FriendlyClassName(self):
    #    print "sdafafasdfafasdfasdf",
    #    try:
    #        print "---", self['FriendlyClassName']
    #    except Exception, e:
    #        print "fffffffffffffffffffff"
    #        print `e`
    #    return self['FriendlyClassName']

    def WindowText(self):
        return self['Texts'][0]

    def HasStyle(self, style):
        return self['Style'] & style == style

    def HasExStyle(self, exstyle):
        return self['ExStyle'] & exstyle == exstyle


#====================================================================
def GetMenuBlocks(ctrls):
    allMenuBlocks = []
    for ctrl in ctrls:
        if ctrl.has_key('MenuItems'):
            # we need to get all the separate menu blocks!
            menuBlocks = MenuBlockAsControls(ctrl.MenuItems())
            allMenuBlocks.extend(menuBlocks)

    return allMenuBlocks


#====================================================================
def MenuBlockAsControls(menuItems, parentage = []):

    blocks = []

    curBlock = []
    for item in menuItems:

        # do a bit of conversion first :-)
        itemAsCtrl = MenuItemAsControl(item)

        # update the FriendlyClassName to contain the 'path' to
        # this particular item
        # TODO: CHECK - as itemPath is currently unused!
        if parentage:
            itemPath = "%s->%s" % ("->".join(parentage), item['Text'])
        else:
            itemPath = item['Text']

        #append the item to the current menu block
        curBlock.append(itemAsCtrl)

        # If the item has a sub menu
        if item.has_key('MenuItems'):

            # add the current item the path
            parentage.append(item['Text'])

            # Get the block for the SubMenu, and add it to the list of
            # blocks we have found
            blocks.extend(
                MenuBlockAsControls(
                    item['MenuItems']['MenuItems'], parentage))

            # and seeing as we are dong with that sub menu remove the current
            # item from the path
            del(parentage[-1])

    # add the current block to the list of blocks
    blocks.append(curBlock)

    return blocks


#====================================================================
def MenuItemAsControl(menuItem):
    "Make a menu item look like a control for tests"

    itemAsCtrl = ControlProps()

    itemAsCtrl["Texts"] = [menuItem['Text'], ]
    itemAsCtrl["ControlID"] = menuItem['ID']
    itemAsCtrl["Type"] = menuItem['Type']
    itemAsCtrl["State"] = menuItem['State']

    itemAsCtrl["Class"] = "MenuItem"
    itemAsCtrl["FriendlyClassName"] = "MenuItem"

    # as most of these don't matter - just set them up with default stuff
    itemAsCtrl["Rectangle"] = RECT(0, 0, 999, 999)
    itemAsCtrl["Fonts"] = [LOGFONTW(), ]
    itemAsCtrl["ClientRects"] = [RECT(0, 0, 999, 999), ]
    itemAsCtrl["ContextHelpID"] = 0
    itemAsCtrl["UserData"]  = 0
    itemAsCtrl["Style"] = 0
    itemAsCtrl["ExStyle"] = 0
    itemAsCtrl["IsVisible"] = 1

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
    if  [ctrl.ControlID() for ctrl in controls] == \
        [ctrl.ControlID() for ctrl in refControls]:

        toRet += allIDsSameFlag

    # check if the control classes match
    if [ctrl.Class() for ctrl in controls] == \
       [ctrl.Class() for ctrl in refControls]:

        toRet += allClassesSameFlag

    return toRet



##====================================================================
#class ControlProps(dict):
#    #----------------------------------------------------------------
#    def __init__(self, props = {}):
#        # default to having menuItems for all things
#        self.MenuItems = []
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
#    # for plurals (e.g. if self.Fonts = [4, 2] then self.Font = 4)
#    def __getattr__(self, key):
#
#        # if the key is not in the dictionary but the plural is
#        if key not in self and key + "s" in self:
#
#            # try to get the first element of the possible list item
#            try:
#                return self[key + "s"][0]
#            except TypeError, e:
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
#    def HasStyle(self, flag):
#        return self.Style & flag == flag
#
#    #----------------------------------------------------------------
#    def HasExStyle(self, flag):
#        return self.ExStyle & flag == flag
#
#
