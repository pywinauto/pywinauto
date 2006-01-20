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

import elementtree
from elementtree.ElementTree import Element, SubElement, ElementTree
import ctypes
import re
import PIL.Image
import controls



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
        structElem = SubElement(element, name)
        #clsModule = value.__class__.__module__
        clsName = value.__class__.__name__
        structElem.set("__type__", "%s" % clsName)

        # iterate over the fields in the structure
        for propName in value._fields_:
            propName = propName[0]
            itemVal = getattr(value, propName)

            if isinstance(itemVal, (int, long)):
                propName += "_LONG"
                itemVal = unicode(itemVal)

            structElem.set(propName, _EscapeSpecials(itemVal))

    elif isinstance(value, PIL.Image.Image):
        try:
            # if the image is too big then don't try to
            # write it out - it would probably product a MemoryError
            # anyway
            if value.size[0] * value.size[1] > (5000*5000):
                raise MemoryError

            imageData = value.tostring().encode("bz2").encode("base64")
            _SetNodeProps(
                element,
                name + "_IMG",
                {"mode": value.mode, "size":value.size, "data":imageData})

        # a system error is raised from time to time when we try to grab
        # the image of a control that has 0 height or width
        except (SystemError, MemoryError):
            pass


    elif isinstance(value, (list, tuple)):
        # add the element to hold the values
        #listElem = SubElement(element, name)

        # remove the s at the end (if there)
        #name = name.rstrip('s')

        for i, attrVal in enumerate(value):
            _SetNodeProps(element, "%s_%05d"%(name, i), attrVal)

    elif isinstance(value, dict):
        dictElem = SubElement(element, name)

        for n, val in value.items():
            _SetNodeProps(dictElem, n, val)

    else:
        if isinstance(value, (int, long)):
            name += "_LONG"

        element.set(name, _EscapeSpecials(value))


#-----------------------------------------------------------------------------
def WriteDialogToFile(fileName, props):
    """Write the props to the file

    props can be either a dialog of a dictionary
    """
    # if we are passed in a wrapped handle then
    # get the properties
    try:
        props[0].keys()
    except AttributeError:
        props = controls.GetDialogPropsFromHandle(props)

    # build a tree structure
    root = Element("DIALOG")
    root.set("_version_", "2.0")
    for ctrl in props:
        ctrlElem = SubElement(root, "CONTROL")
        for name, value in sorted(ctrl.items()):
            _SetNodeProps(ctrlElem, name, value)

    # wrap it in an ElementTree instance, and save as XML
    tree = ElementTree(root)
    tree.write(fileName, encoding="utf-8")



#-----------------------------------------------------------------------------
def _EscapeSpecials(s):
    "Ensure that some characters are escaped before writing to XML"

    # ensure it is unicode
    s = unicode(s)

    # escape backslashs
    s = s.replace('\\', r'\\')

    # escape non printable characters (chars below 30)
    for i in range(0, 31):
        s = s.replace(unichr(i), "\\%02d"%i)

    return s


#-----------------------------------------------------------------------------
def _UnEscapeSpecials(s):
    "Replace escaped characters with real character"

    # Unescape all the escape characters
    for i in range(0, 31):
        s = s.replace("\\%02d"%i, unichr(i))

    # convert doubled backslashes to a single backslash
    s = s.replace(r'\\', '\\')

    return unicode(s)



#-----------------------------------------------------------------------------
def _XMLToStruct(element, structType = None):
    """Convert an ElementTree to a ctypes Struct

    If structType is not specified then element['__type__']
    will be used for the ctypes struct type"""

    # handle if we are passed in an element or a dictionary
    if isinstance(element, elementtree.ElementTree._ElementInterface):
        attribs = element.attrib
    else:
        attribs = element

    # if the type has not been passed in
    if not structType:
        # get the type and create an instance of the type
        struct = globals()[attribs["__type__"]]()
    else:
        # create an instance of the type
        struct = globals()[structType]()

    # get the attribute and set them upper case
    structAttribs = dict([(at.upper(), at) for at in dir(struct)])

    # for each of the attributes in the element
    for propName in attribs:

        # get teh value
        val = attribs[propName]

        # if the value ends with "_long"
        if propName.endswith("_LONG"):
            # get an long attribute out of the value
            val = long(val)
            propName = propName[:-5]

        # if the value is a string
        elif isinstance(val, basestring):
            # make sure it if Unicode
            val = unicode(val)

        # now we can have all upper case attribute name
        # but structure name will not be upper case
        if propName.upper() in structAttribs:
            propName = structAttribs[propName.upper()]

            # set the appropriate attribute of the Struct
            setattr(struct, propName, val)

    # reutrn the struct
    return struct



#====================================================================
def _OLD_XMLToTitles(element):
    "For OLD XML files convert the titles as a list"
    # get all the attribute names
    titleNames = element.keys()

    # sort them to make sure we get them in the right order
    titleNames.sort()

    # build up the array
    titles = []
    for name in titleNames:
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
def _ExtractProperties(properties, propName, propValue):
    """Hmmm - confusing - can't remember exactly how
    all these similar functions call each other"""

    # get the base property name and number if it in the form
    #  "PROPNAME_00001" = ('PROPNAME', 1)
    propName, reqdIndex = _SplitNumber(propName)

    # if there is no required index, and the property
    # was not already set - then just set it

    # if this is an indexed member of a list
    if reqdIndex == None:
        # Have we hit a property with this name already
        if propName in properties:
            # try to append current value to the property
            try:
                properties[propName].append(propValue)

            # if that fails then we need to make sure that
            # the curruen property is a list and then
            # append it
            except AttributeError:
                newVal = [properties[propName], propValue]
                properties[propName] = newVal
        # No index, no previous property with that name
        #  - just set the property
        else:
            properties[propName] = propValue

    # OK - so it HAS an index
    else:

        # make sure that the property is a list
        properties.setdefault(propName, [])

        # make sure that the list has enough elements
        while 1:
            if len(properties[propName]) <= reqdIndex:
                properties[propName].append('')
            else:
                break

        # put our value in at the right index
        properties[propName][reqdIndex] = propValue


#====================================================================
def _GetAttributes(element):
    "Get the attributes from an element"

    properties = {}

    # get all the attributes
    for attribName, val in element.attrib.items():

        # if it is 'Long' element convert it to an long
        if attribName.endswith("_LONG"):
            val = long(val)
            attribName = attribName[:-5]

        else:
            # otherwise it is a string - make sure we get it as a unicode string
            val = _UnEscapeSpecials(val)

        _ExtractProperties(properties, attribName, val)

    return properties


#====================================================================
number = re.compile(r"^(.*)_(\d{5})$")
def _SplitNumber(propName):
    """Return (string, number) for a propname in the format string_number

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
    found = number.search(propName)

    if not found:
        return propName, None

    return found.group(1), int(found.group(2))



#====================================================================
def _ReadXMLStructure(controlElement):
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
    properties = _GetAttributes(controlElement)

    for elem in controlElement:
        # if it is a ctypes structure
        if "__type__" in elem.attrib:
            # create a new instance of the correct type

            # grab the data
            propVal = _XMLToStruct(elem)

        elif elem.tag.endswith("_IMG"):
            elem.tag = elem.tag[:-4]

            # get image Attribs
            img = _GetAttributes(elem)
            data = img['data'].decode('base64').decode('bz2')
            propVal = PIL.Image.fromstring(img['mode'], img['size'], data)

        else:
            propVal = _ReadXMLStructure(elem)

        _ExtractProperties(properties, elem.tag, propVal)

    return properties




#====================================================================
def ReadPropertiesFromFile(filename):
    """Return an list of controls from XML file filename"""

    # parse the file
    parsed = ElementTree().parse(filename)

    # Return the list that has been stored under 'CONTROL'
    props =  _ReadXMLStructure(parsed)['CONTROL']

    # it is an old XML so let's fix it up a little
    if not parsed.attrib.has_key("_version_"):

        # find each of the control elements
        for ctrlProp in props:

            ctrlProp['Fonts'] = [_XMLToStruct(ctrlProp['FONT'], "LOGFONTW"), ]

            ctrlProp['Rectangle'] = _XMLToStruct(ctrlProp["RECTANGLE"], "RECT")

            ctrlProp['ClientRects'] = [
                _XMLToStruct(ctrlProp["CLIENTRECT"], "RECT"),]

            ctrlProp['Texts'] = _OLD_XMLToTitles(ctrlProp["TITLES"])

            ctrlProp['Class'] = ctrlProp['CLASS']
            ctrlProp['ContextHelpID'] = ctrlProp['HELPID']
            ctrlProp['ControlID'] = ctrlProp['CTRLID']
            ctrlProp['ExStyle'] = ctrlProp['EXSTYLE']
            ctrlProp['FriendlyClassName'] = ctrlProp['FRIENDLYCLASS']
            ctrlProp['IsUnicode'] = ctrlProp['ISUNICODE']
            ctrlProp['IsVisible'] = ctrlProp['ISVISIBLE']
            ctrlProp['Style'] = ctrlProp['STYLE']
            ctrlProp['UserData'] = ctrlProp['USERDATA']

            for propName in [
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
                del(ctrlProp[propName])

    return props


#====================================================================
def _unittests():
    "Perform some simple unit testing"

    import sys

    props = ReadPropertiesFromFile(sys.argv[1])
    WriteDialogToFile(sys.argv[1] + "__", props)

    import pprint
    pprint.pprint(props)


#====================================================================
if __name__ == "__main__":
    _unittests()


