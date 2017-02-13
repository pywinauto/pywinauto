import pyatspi
from .element_info import ElementInfo


class RECT():

    """Wrap the RECT structure and add extra functionality"""

    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/windef.h 287
        ('left', int),
        ('top', int),
        ('right', int),
        ('bottom', int),
    ]

    # ----------------------------------------------------------------
    def __init__(self, otherRect_or_left = 0, top = 0, right = 0, bottom = 0):
        """Provide a constructor for RECT structures

        A RECT can be constructed by:
        - Another RECT (each value will be copied)
        - Values for left, top, right and bottom

        e.g. my_rect = RECT(otherRect)
        or   my_rect = RECT(10, 20, 34, 100)
        """
        if isinstance(otherRect_or_left, RECT):
            self.left = otherRect_or_left.left
            self.right = otherRect_or_left.right
            self.top = otherRect_or_left.top
            self.bottom = otherRect_or_left.bottom
        else:
            #if not isinstance(otherRect_or_left, (int, long)):
            #    print type(self), type(otherRect_or_left), otherRect_or_left
            self.left = otherRect_or_left
            self.right = right
            self.top = top
            self.bottom = bottom


#    # ----------------------------------------------------------------
#    def __eq__(self, otherRect):
#        "return true if the two rectangles have the same coordinates"
#
#        try:
#            return \
#                self.left == otherRect.left and \
#                self.top == otherRect.top and \
#                self.right == otherRect.right and \
#                self.bottom == otherRect.bottom
#        except AttributeError:
#            return False

    # ----------------------------------------------------------------
    def __str__(self):
        """Return a string representation of the RECT"""
        return "(L%d, T%d, R%d, B%d)" % (
            self.left, self.top, self.right, self.bottom)

    # ----------------------------------------------------------------
    def __repr__(self):
        """Return some representation of the RECT"""
        return "<RECT L%d, T%d, R%d, B%d>" % (
            self.left, self.top, self.right, self.bottom)

    # ----------------------------------------------------------------
    def __sub__(self, other):
        """Return a new rectangle which is offset from the one passed in"""
        newRect = RECT()

        newRect.left = self.left - other.left
        newRect.right = self.right - other.left

        newRect.top = self.top - other.top
        newRect.bottom = self.bottom - other.top

        return newRect

    # ----------------------------------------------------------------
    def __add__(self, other):
        """Allow two rects to be added using +"""
        newRect = RECT()

        newRect.left = self.left + other.left
        newRect.right = self.right + other.left

        newRect.top = self.top + other.top
        newRect.bottom = self.bottom + other.top

        return newRect

    # ----------------------------------------------------------------
    def width(self):
        """Return the width of the  rect"""
        return self.right - self.left

    # ----------------------------------------------------------------
    def height(self):
        """Return the height of the rect"""
        return self.bottom - self.top

    # ----------------------------------------------------------------
    def mid_point(self):
        """Return a POINT structure representing the mid point"""
        pt = POINT()
        pt.x = self.left + int(float(self.width())/2.)
        pt.y = self.top + int(float(self.height())/2.)
        return pt


class AtpsiElementInfo(ElementInfo):

    """Wrapper for window handler"""

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = pyatspi.Registry.getDesktop(0)
        else:
            self._handle = handle

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def rich_text(self):
        """Return the text of the window"""
        return self._handle.get_name()

    @property
    def control_id(self):
        """Return the ID of the window"""
        return self._handle.get_id()

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return self._handle.get_process_id()

    @property
    def class_name(self):
        """Return the class name of the element"""
        return self._handle.get_toolkit_name()

    @property
    def enabled(self):
        """Return True if the element is enabled"""
        raise NotImplementedError()

    @property
    def visible(self):
        """Return True if the element is visible"""
        raise NotImplementedError()

    @property
    def parent(self):
        """Return the parent of the element"""
        return self._handle.parent

    def children(self, **kwargs):
        """Return children of the element"""
        return [children for children in self._handle]

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        raise NotImplementedError()

    @property
    def rectangle(self):
        """Return rectangle of element"""
        component = self._handle.queryComponent()
        rect = RECT()
        position = component.getPosition(pyatspi.CoordType(0))
        size = component.getSize()
        rect.left = position[0]
        rect.top = position[1]
        rect.right = rect.left + size[0]
        rect.bottom = rect.top + size[1]
        return rect

    def dump_window(self):
        """Dump an element to a set of properties"""
        raise NotImplementedError()
