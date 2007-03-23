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

"""Module containing operations for reading and writing dialogs as XML
"""

__revision__ = "$Revision$"


# how should we read in the XML file
# NOT USING MS Components (requirement on machine)
# maybe using built in XML
# maybe using elementtree
# others?

#import elementtree
try:
    # Python 2.5 (thanks to Daisuke Yamashita)
    from xml.etree.ElementTree import Element, SubElement, ElementTree
    from xml.etree.cElementTree import Element, SubElement, ElementTree 
except ImportError:
    from elementtree.ElementTree import Element, SubElement, ElementTree
    from cElementTree import Element, SubElement, ElementTree
    
import ctypes
import re
import PIL.Image
import controls

# reported that they are not used - but in fact they are
# through a search of globals()
from win32structures import LOGFONTW, RECT

class XMLParsingError(RuntimeError):
    "Wrap parsing Exceptions"
    pass



#DONE: Make the dialog reading function not actually know about the
# types of each element (so that we can read the control properties
# without having to know each and every element type)
# probably need to store info on what type things are.
#
# - if it is a ctypes struct then there is a __type__ field
#   which says what kind of stuct it is
# - If it is an image then a "_IMG" is appeded to the the element tag
# - if it is a long then _LONG is appended to attribute name
# everything else is considered a string!


#-----------------------------------------------------------------------------
def _SetNodeProps(element, name, value):
    "Set the properties of the node based on the type of object"

    # if it is a ctypes structure
    if isinstance(value, ctypes.Structure):

        # create an element for the structure
        struct_elem = SubElement(element, name)
        #clsModule = value.__class__.__module__
        cls_name = value.__class__.__name__
        struct_elem.set("__type__", "%s" % cls_name)

        # iterate over the fields in the structure
        for prop_name in value._fields_:
            prop_name = prop_name[0]
            item_val = getattr(value, prop_name)

            if isinstance(item_val, (int, long)):
                prop_name += "_LONG"
                item_val = unicode(item_val)

            struct_elem.set(prop_name, _EscapeSpecials(item_val))

    elif isinstance(value, PIL.Image.Image):
        try:
            # if the image is too big then don't try to
            # write it out - it would probably product a MemoryError
            # anyway
            if value.size[0] * value.size[1] > (5000*5000):
                raise MemoryError

            image_data = value.tostring().encode("bz2").encode("base64")
            _SetNodeProps(
                element,
                name + "_IMG",
                {
                    "mode": value.mode,
                    "size_x":value.size[0],
                    "size_y":value.size[1],
                    "data":image_data
                })

        # a system error is raised from time to time when we try to grab
        # the image of a control that has 0 height or width
        except (SystemError, MemoryError):
            pass


    elif isinstance(value, (list, tuple)):
        # add the element to hold the values
        # we do this to be able to support empty lists
        listelem = SubElement(element, name + "_LIST")

        for i, attrval in enumerate(value):
            _SetNodeProps(listelem, "%s_%05d"%(name, i), attrval)

    elif isinstance(value, dict):
        dict_elem = SubElement(element, name)

        for item_name, val in value.items():
            _SetNodeProps(dict_elem, item_name, val)

    else:
        if isinstance(value, bool):
            value = long(value)

        if isinstance(value, (int, long)):
            name += "_LONG"

        element.set(name, _EscapeSpecials(value))


#-----------------------------------------------------------------------------
def WriteDialogToFile(filename, props):
    """Write the props to the file

    props can be either a dialog of a dictionary
    """
    # if we are passed in a wrapped handle then
    # get the properties
    try:
        props[0].keys()
    except (TypeError, AttributeError):
        props = controls.GetDialogPropsFromHandle(props)

    # build a tree structure
    root = Element("DIALOG")
    root.set("_version_", "2.0")
    for ctrl in props:
        ctrlelem = SubElement(root, "CONTROL")
        for name, value in sorted(ctrl.items()):
            _SetNodeProps(ctrlelem, name, value)

    # wrap it in an ElementTree instance, and save as XML
    tree = ElementTree(root)
    tree.write(filename, encoding="utf-8")



#-----------------------------------------------------------------------------
def _EscapeSpecials(string):
    "Ensure that some characters are escaped before writing to XML"

    # ensure it is unicode
    string = unicode(string)

    # escape backslashs
    string = string.replace('\\', r'\\')

    # escape non printable characters (chars below 30)
    for i in range(0, 32):
        string = string.replace(unichr(i), "\\%02d"%i)

    return string


#-----------------------------------------------------------------------------
def _UnEscapeSpecials(string):
    "Replace escaped characters with real character"

    # Unescape all the escape characters
    for i in range(0, 32):
        string = string.replace("\\%02d"%i, unichr(i))

    # convert doubled backslashes to a single backslash
    string = string.replace(r'\\', '\\')

    return unicode(string)



#-----------------------------------------------------------------------------
def _XMLToStruct(element, struct_type = None):
    """Convert an ElementTree to a ctypes Struct

    If struct_type is not specified then element['__type__']
    will be used for the ctypes struct type"""


    # handle if we are passed in an element or a dictionary
    try:
        attribs = element.attrib
    except AttributeError:
        attribs = element

    # if the type has not been passed in
    if not struct_type:
        # get the type and create an instance of the type
        struct = globals()[attribs["__type__"]]()
    else:
        # create an instance of the type
        struct = globals()[struct_type]()

    # get the attribute and set them upper case
    struct_attribs = dict([(at.upper(), at) for at in dir(struct)])

    # for each of the attributes in the element
    for prop_name in attribs:

        # get the value
        val = attribs[prop_name]

        # if the value ends with "_long"
        if prop_name.endswith("_LONG"):
            # get an long attribute out of the value
            val = long(val)
            prop_name = prop_name[:-5]

        # if the value is a string
        elif isinstance(val, basestring):
            # make sure it if Unicode
            val = unicode(val)

        # now we can have all upper case attribute name
        # but structure name will not be upper case
        if prop_name.upper() in struct_attribs:
            prop_name = struct_attribs[prop_name.upper()]

            # set the appropriate attribute of the Struct
            setattr(struct, prop_name, val)

    # reutrn the struct
    return struct



#====================================================================
def _OLD_XMLToTitles(element):
    "For OLD XML files convert the titles as a list"
    # get all the attribute names
    title_names = element.keys()

    # sort them to make sure we get them in the right order
    title_names.sort()

    # build up the array
    titles = []
    for name in title_names:
        val = element[name]
        val = val.replace('\\n', '\n')
        val = val.replace('\\x12', '\x12')
        val = val.replace('\\\\', '\\')

        titles.append(unicode(val))

    return titles


#====================================================================
# TODO: this function should be broken up into smaller functions
#       for each type of processing e.g.
#       ElementTo
def _ExtractProperties(properties, prop_name, prop_value):
    """Hmmm - confusing - can't remember exactly how
    all these similar functions call each other"""

    # get the base property name and number if it in the form
    #  "PROPNAME_00001" = ('PROPNAME', 1)
    prop_name, reqd_index = _SplitNumber(prop_name)

    # if there is no required index, and the property
    # was not already set - then just set it

    # if this is an indexed member of a list
    if reqd_index == None:
        # Have we hit a property with this name already
        if prop_name in properties:
            # try to append current value to the property
            try:
                properties[prop_name].append(prop_value)

            # if that fails then we need to make sure that
            # the curruen property is a list and then
            # append it
            except AttributeError:
                new_val = [properties[prop_name], prop_value]
                properties[prop_name] = new_val
        # No index, no previous property with that name
        #  - just set the property
        else:
            properties[prop_name] = prop_value

    # OK - so it HAS an index
    else:

        # make sure that the property is a list
        properties.setdefault(prop_name, [])

        # make sure that the list has enough elements
        while 1:
            if len(properties[prop_name]) <= reqd_index:
                properties[prop_name].append('')
            else:
                break

        # put our value in at the right index
        properties[prop_name][reqd_index] = prop_value


#====================================================================
def _GetAttributes(element):
    "Get the attributes from an element"

    properties = {}

    # get all the attributes
    for attrib_name, val in element.attrib.items():

        # if it is 'Long' element convert it to an long
        if attrib_name.endswith("_LONG"):
            val = long(val)
            attrib_name = attrib_name[:-5]

        else:
            # otherwise it is a string - make sure we get it as a unicode string
            val = _UnEscapeSpecials(val)

        _ExtractProperties(properties, attrib_name, val)

    return properties


#====================================================================
number = re.compile(r"^(.*)_(\d{5})$")
def _SplitNumber(prop_name):
    """Return (string, number) for a prop_name in the format string_number

    The number part has to be 5 digits long
    None is returned if there is no _number part

    e.g.
    >>> _SplitNumber("NoNumber")
    ('NoNumber', None)
    >>> _SplitNumber("Anumber_00003")
    ('Anumber', 3)
    >>> _SplitNumber("notEnoughDigits_0003")
    ('notEnoughDigits_0003', None)
    """
    found = number.search(prop_name)

    if not found:
        return prop_name, None

    return found.group(1), int(found.group(2))



#====================================================================
def _ReadXMLStructure(control_element):
    """Convert an element into nested Python objects

    The values will be returned in a dictionary as following:

     - the attributes will be items of the dictionary
       for each subelement

       + if it has a __type__ attribute then it is converted to a
         ctypes structure
       + if the element tag ends with _IMG then it is converted to
         a PIL image

     - If there are elements with the same name or attributes with
       ordering e.g. texts_00001, texts_00002 they will be put into a
       list (in the correct order)
    """

    # get the attributes for the current element
    properties = _GetAttributes(control_element)

    for elem in control_element:
        # if it is a ctypes structure
        if "__type__" in elem.attrib:
            # create a new instance of the correct type

            # grab the data
            propval = _XMLToStruct(elem)

        elif elem.tag.endswith("_IMG"):
            elem.tag = elem.tag[:-4]

            # get image Attribs
            img = _GetAttributes(elem)
            data = img['data'].decode('base64').decode('bz2')

            propval = PIL.Image.fromstring(
                img['mode'],
                (img['size_x'], img['size_y']),
                data)

        elif elem.tag.endswith("_LIST"):
            # All this is just to handle the edge case of
            # an empty list
            elem.tag = elem.tag[:-5]

            # read the structure
            propval = _ReadXMLStructure(elem)

            # if it was empty then convert the returned dict
            # to a list
            if propval == {}:
                propval = list()

            # otherwise extract the list out of the returned dict
            else:
                propval = propval[elem.tag]

        else:
            propval = _ReadXMLStructure(elem)

        _ExtractProperties(properties, elem.tag, propval)

    return properties




#====================================================================
def ReadPropertiesFromFile(filename):
    """Return an list of controls from XML file filename"""

    # parse the file
    parsed = ElementTree().parse(filename)

    # Return the list that has been stored under 'CONTROL'
    props =  _ReadXMLStructure(parsed)['CONTROL']
    if not isinstance(props, list):
        props = [props]


    # it is an old XML so let's fix it up a little
    if not parsed.attrib.has_key("_version_"):

        # find each of the control elements
        for ctrl_prop in props:

            ctrl_prop['Fonts'] = [_XMLToStruct(ctrl_prop['FONT'], "LOGFONTW"), ]

            ctrl_prop['Rectangle'] = \
                _XMLToStruct(ctrl_prop["RECTANGLE"], "RECT")

            ctrl_prop['ClientRects'] = [
                _XMLToStruct(ctrl_prop["CLIENTRECT"], "RECT"),]

            ctrl_prop['Texts'] = _OLD_XMLToTitles(ctrl_prop["TITLES"])

            ctrl_prop['Class'] = ctrl_prop['CLASS']
            ctrl_prop['ContextHelpID'] = ctrl_prop['HELPID']
            ctrl_prop['ControlID'] = ctrl_prop['CTRLID']
            ctrl_prop['ExStyle'] = ctrl_prop['EXSTYLE']
            ctrl_prop['FriendlyClassName'] = ctrl_prop['FRIENDLYCLASS']
            ctrl_prop['IsUnicode'] = ctrl_prop['ISUNICODE']
            ctrl_prop['IsVisible'] = ctrl_prop['ISVISIBLE']
            ctrl_prop['Style'] = ctrl_prop['STYLE']
            ctrl_prop['UserData'] = ctrl_prop['USERDATA']

            for prop_name in [
                'CLASS',
                'CLIENTRECT',
                'CTRLID',
                'EXSTYLE',
                'FONT',
                'FRIENDLYCLASS',
                'HELPID',
                'ISUNICODE',
                'ISVISIBLE',
                'RECTANGLE',
                'STYLE',
                'TITLES',
                'USERDATA',
                ]:
                del(ctrl_prop[prop_name])

    return props


