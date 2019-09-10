import win32con
import win32ui
from pywin.mfc import dialog


class ProgressBarDialog(dialog.Dialog):
    title = "Updating..."
    style = (win32con.DS_MODALFRAME | win32con.WS_POPUP | win32con.WS_VISIBLE | win32con.WS_CAPTION |
             win32con.DS_SETFONT | win32con.WS_EX_TOPMOST)
    cs = (win32con.WS_CHILD | win32con.WS_VISIBLE)
    dimensions = (0, 0, 215, 20)
    title_font = (8, "MS Sans Serif")

    def __init__(self, rect, *args, **kwargs):
        self.rect = rect
        if rect:
            self.dimensions = (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
        dialog.Dialog.__init__(self, [[self.title, self.dimensions, self.style, None, self.title_font], ])
        self.pbar = win32ui.CreateProgressCtrl()

    def OnInitDialog(self):
        rc = dialog.Dialog.OnInitDialog(self)
        self.pbar.CreateWindow(self.cs, (10, 10, 310 if not self.rect else self.dimensions[2] - 20, 24), self, 1001)
        return rc

    def show(self):
        self.CreateWindow()
        self.SetWindowPos(win32con.HWND_TOPMOST, self.dimensions,
                          win32con.SWP_SHOWWINDOW | (win32con.SWP_NOMOVE | win32con.SWP_NOSIZE) if not self.rect else 0)

    def close(self):
        self.OnCancel()

    def set_progress(self, value):
        self.pbar.SetPos(value)
