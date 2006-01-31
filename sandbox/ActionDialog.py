#
##=========================================================================
#class ActionDialog(object):
#    """ActionDialog wraps the dialog you are interacting with
#
#    It provides support for finding controls using attribute access,
#    item access and the _control(...) method.
#
#    You can dump information from a dialgo to XML using the write_() method
#
#    A screenshot of the dialog can be taken using the underlying wrapped
#    HWND ie. my_action_dlg.wrapped_win.CaptureAsImage().save("dlg.png").
#    This is only available if you have PIL installed (fails silently
#    otherwise).
#    """
#    def __init__(self, hwnd, app = None, props = None):
#        """Initialises an ActionDialog object
#
#        ::
#           hwnd (required) The handle of the dialog
#           app An instance of an Application Object
#           props future use (when we have an XML file for reference)
#
#        """
#
#        #self.wrapped_win = controlactions.add_actions(
#        #    controls.WrapHandle(hwnd))
#        self.wrapped_win = controls.WrapHandle(hwnd)
#
#        self.app = app
#
#        dlg_controls = [self.wrapped_win, ]
#        dlg_controls.extend(self.wrapped_win.Children)
#
#    def __getattr__(self, key):
#        "Attribute access - defer to item access"
#        return self[key]
#
#    def __getitem__(self, attr):
#        "find the control that best matches attr"
#        # if it is an integer - just return the
#        # child control at that index
#        if isinstance(attr, (int, long)):
#            return self.wrapped_win.Children[attr]
#
#        # so it should be a string
#        # check if it is an attribute of the wrapped win first
#        try:
#            return getattr(self.wrapped_win, attr)
#        except (AttributeError, UnicodeEncodeError):
#            pass
#
#        # find the control that best matches our attribute
#        ctrl = findbestmatch.find_best_control_match(
#            attr, self.wrapped_win.Children)
#
#        # add actions to the control and return it
#        return ctrl
#
#    def write_(self, filename):
#        "Write the dialog an XML file (requires elementtree)"
#        if self.app and self.app.xmlpath:
#            filename = os.path.join(self.app.xmlpath, filename + ".xml")
#
#        controls = [self.wrapped_win]
#        controls.extend(self.wrapped_win.Children)
#        props = [ctrl.GetProperties() for ctrl in controls]
#
#        XMLHelpers.WriteDialogToFile(filename, props)
#
#    def control_(self, **kwargs):
#        "Find the control that matches the arguments and return it"
#
#        # add the restriction for this particular process
#        kwargs['parent'] = self.wrapped_win
#        kwargs['process'] = self.app.process
#        kwargs['top_level_only'] = False
#
#        # try and find the dialog (waiting for a max of 1 second
#        ctrl = findwindows.find_window(**kwargs)
#        #win = ActionDialog(win, self)
#
#        return controls.WrapHandle(ctrl)
#
#
#
#
##=========================================================================
#def _WalkDialogControlAttribs(app, attr_path):
#    "Try and resolve the dialog and 2nd attribute, return both"
#    if len(attr_path) != 2:
#        raise RuntimeError("Expecting only 2 items in the attribute path")
#
#    # get items to select between
#    # default options will filter hidden and disabled controls
#    # and will default to top level windows only
#    wins = findwindows.find_windows(process = app.process)
#
#    # wrap each so that find_best_control_match works well
#    wins = [controls.WrapHandle(win) for win in wins]
#
#    # if an integer has been specified
#    if isinstance(attr_path[0], (int, long)):
#        dialogWin  = wins[attr_path[0]]
#    else:
#        # try to find the item
#        dialogWin = findbestmatch.find_best_control_match(attr_path[0], wins)
#
#    # already wrapped
#    dlg = ActionDialog(dialogWin, app)
#
#    # for each of the other attributes ask the
#    attr_value = dlg
#    for attr in attr_path[1:]:
#        try:
#            attr_value = getattr(attr_value, attr)
#        except UnicodeEncodeError:
#            attr_value = attr_value[attr]
#
#    return dlg, attr_value
#
#
##=========================================================================
#class _DynamicAttributes(object):
#    "Class that builds attributes until they are ready to be resolved"
#
#    def __init__(self, app):
#        "Initialize the attributes"
#        self.app = app
#        self.attr_path = []
#
#    def __getattr__(self, attr):
#        "Attribute access - defer to item access"
#        return self[attr]
#
#    def __getitem__(self, attr):
#        "Item access[] for getting dialogs and controls from an application"
#
#        # do something with this one
#        # and return a copy of ourselves with some
#        # data related to that attribute
#
#        self.attr_path.append(attr)
#
#        # if we have a lenght of 2 then we have either
#        #   dialog.attribute
#        # or
#        #   dialog.control
#        # so go ahead and resolve
#        if len(self.attr_path) == 2:
#            dlg, final = _wait_for_function_success(
#                _WalkDialogControlAttribs, self.app, self.attr_path)
#
#            # seing as we may already have a reference to the dialog
#            # we need to strip off the control so that our dialog
#            # reference is not messed up
#            self.attr_path = self.attr_path[:-1]
#
#            return final
#
#        # we didn't hit the limit so continue collecting the
#        # next attribute in the chain
#        return self
#
#
##=========================================================================
#def _wait_for_function_success(func, *args, **kwargs):
#    """Retry the dialog up to timeout trying every time_interval seconds
#
#    timeout defaults to 1 second
#    time_interval defaults to .09 of a second """
#    if kwargs.has_key('time_interval'):
#        time_interval = kwargs['time_interval']
#        del kwargs['time_interval']
#    else:
#        time_interval = window_retry_interval
#
#    if kwargs.has_key('timeout'):
#        timeout = kwargs['timeout']
#        del kwargs['timeout']
#    else:
#        timeout = window_find_timeout
#
#
#    # keep going until we either hit the return (success)
#    # or an exception is raised (timeout)
#    while 1:
#        try:
#            return func(*args, **kwargs)
#        except:
#            if timeout > 0:
#                time.sleep (time_interval)
#                timeout -= time_interval
#            else:
#                raise
#
#
#
