class ElementInfo(object):
    "Wrapper for element"
    @property
    def handle(self):
        "Return the handle of the element"
        raise NotImplementedError()

    @property
    def name(self):
        "Return the name of the element"
        raise NotImplementedError()

    @property
    def richText(self):
        "Return the text of the element"
        raise NotImplementedError()

    @property
    def controlId(self):
        "Return the ID of the control"
        raise NotImplementedError()

    @property
    def processId(self):
        "Return the ID of process that controls this element"
        raise NotImplementedError()

    @property
    def frameworkId(self):
        "Return the framework of the element"
        raise NotImplementedError()
    
    @property
    def className(self):
        "Return the class name of the element"
        raise NotImplementedError()

    @property
    def enabled(self):
        "Return True if the element is enabled"
        raise NotImplementedError()
        
    @property
    def visible(self):
        "Return True if the element is visible"
        raise NotImplementedError()
       
    @property
    def parent(self):
        "Return the parent of the element"
        raise NotImplementedError()

    @property
    def children(self):
        "Return children of the element"
        raise NotImplementedError()

    @property
    def descendants(self):
        "Return descendants of the element"
        raise NotImplementedError()

    @property
    def rectangle(self):
        "Return rectangle of element"
        raise NotImplementedError()

    def dumpWindow(self):
        "Dump an element to a set of properties"
        raise NotImplementedError()
