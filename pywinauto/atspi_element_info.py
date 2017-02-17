import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi
from .element_info import ElementInfo


class POINT():
    _pack_ = 4
    _fields_ = [
        ('x', int),
        ('y', int),
    ]


class RECT():

    """Wrap the RECT structure and add extra functionality"""

    _fields_ = [
        ('left', int),
        ('top', int),
        ('right', int),
        ('bottom', int),
    ]

    # ----------------------------------------------------------------
    def __init__(self, otherRect_or_left=0, top=0, right=0, bottom=0):
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
        pt.x = self.left + int(float(self.width()) / 2.)
        pt.y = self.top + int(float(self.height()) / 2.)
        return pt


class AtpsiElementInfo(ElementInfo):

    """Wrapper for window handler"""

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = Atspi.get_desktop(0)
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
        return self._handle.get_role_name()

    @property
    def parent(self):
        """Return the parent of the element"""
        return self._handle.get_parent()

    def children(self, **kwargs):
        """Return children of the element"""
        len = self._handle.get_child_count()
        childrens = []
        for i in range(len):
            childrens.append(self._handle.get_child_at_index(i))
        return childrens

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        raise NotImplementedError()

    @property
    def rectangle(self):
        """Return rectangle of element"""
        # component = self._handle.queryComponent()
        rect = RECT()
        position = self._handle.get_position(0)
        size = self._handle.get_size()
        rect.left = position.x
        rect.top = position.y
        rect.right = rect.left + size.x
        rect.bottom = rect.top + size.y
        return rect

    def dump_window(self):
        """Dump an element to a set of properties"""
        raise NotImplementedError()
