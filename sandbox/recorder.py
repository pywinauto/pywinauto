from pywinauto.application import Application


import pythoncom, pyHook


mouse_mapping = {
    'mouse move': None,
    'mouse right down': True,
    'mouse right up': ("RightClickInput"),
    'mouse left down': True,
    'mouse left up': None,
    'mouse wheel': None,
    }

last_message = None
last_event_time = 0
def OnMouseEvent(event):
    global last_event_time
    # if this is the first action - remember the start time of the script
    if not last_event_time:
        last_event_time = event.Time
    app = Application()

    # wrap the window that is coming from the event
    if event.Window:
        wrapped = app.window_(handle = event.Window)
    else:
        wrapped = None

    # if there was no previous message
    global last_message
    if last_message is None:
        last_message = event.MessageName
        return True


    # get the button pressed
    button = ""
    if "right" in event.MessageName and "right" in last_message:
        button = "Right"
    elif "left" in event.MessageName and "left" in last_message:
        button = "Left"

    toplevel = ""
    if wrapped and not wrapped.IsDialog():
        toplevel = '.Window_(title = "%s", class_name = "%s")' %(
            wrapped.TopLevelParent().WindowText(), wrapped.TopLevelParent().Class())

    if "up" in event.MessageName and "down" in last_message:
        print "time.sleep(%d)"% (event.Time - last_event_time)
        print 'app%s.Window_(title = "%s", class_name = "%s").%sClickInput()'%(
            toplevel,
            wrapped.WindowText(),
            wrapped.Class(),
            button)

    last_event_time = event.Time
    last_message = event.MessageName


  # called when mouse events are received
  #print 'MessageName:',event.MessageName
#  print 'Message:',event.Message
#  print 'Time:',event.Time
  #print 'Window:',event.Window
#  print 'WindowName:',event.WindowName
#  print 'Position:',event.Position
#  print 'Wheel:',event.Wheel
#  print 'Injected:',event.Injected
#  print '---'

  # return True to pass the event to other handlers
    return True

def OnKeyboardEvent(event):
    global last_event_time

    # if this is the first action - remember the start time of the script
    if not last_event_time:
        last_event_time = event.Time

    #print dir(event)

    app = Application()

    if event.Window:
        wrapped = app.window_(handle = event.Window)
    else:
        pass

    global last_message
    if last_message is None:
        last_message = event.MessageName
        return True

    if "down" in event.MessageName:
        print "time.sleep(%d)"% (event.Time - last_event_time)
        print 'app.Window_(title = "%s", class_name = "%s").Typekeys("%s")'%(
            wrapped.WindowText(),
            wrapped.Class(),
            `event.Key`)

    last_event_time = event.Time
    print 'MessageName:',event.MessageName


#  print 'Message:',event.Message
#  print 'Time:',event.Time
#  print 'Window:',event.Window
#  print 'WindowName:',event.WindowName
    win = event.WindowName
#  print 'Ascii:', event.Ascii, chr(event.Ascii)
#  print 'Key:', event.Key
#  print 'KeyID:', event.KeyID
#  print 'ScanCode:', event.ScanCode
#  print 'Extended:', event.Extended
#  print 'Injected:', event.Injected
#  print 'Alt', event.Alt
#  print 'Transition', event.Transition
#  print '---'

  # return True to pass the event to other handlers
    return True

# create a hook manager
hm = pyHook.HookManager()

# watch for all mouse events
hm.MouseAll = OnMouseEvent
# set the hook
hm.HookMouse()

# watch for all mouse events
hm.KeyAll = OnKeyboardEvent
# set the hook
hm.HookKeyboard()


# wait forever
pythoncom.PumpMessages()


