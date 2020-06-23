import logging
import time

from pywinauto.application import Application

logging.basicConfig(level='INFO')
str_file_path = r"C:\Program Files\FileZilla FTP Client\filezilla.exe"
test_data = {
    "host": u"192.168.121.138",
    "username": u"root",
    "password": u"tsl0615",
    "port": u"22",
}
"""
when you use the inspect.exe, there are some meaning:
Name            -> title
AutomationId    -> auto_id
ClassName       -> control_type

looking for handle from the top level window to child, please use the function:
.child_window(title="<Name>", auto_id="<AutomationId>", control_type="<ClassName>")
"""


def test(win_filezilla):
    win_panel = win_filezilla.child_window(title=u"panel", auto_id="-31808", control_type="Pane")
    win_panel.print_control_identifiers(depth=2)
    win_panel.child_window(title=u"主机(H):", auto_id="-31805", control_type="Edit").type_keys(
        test_data['host'], with_spaces=True)  # host
    win_panel.child_window(title="用户名(U):", auto_id="-31803", control_type="Edit").type_keys(
        test_data['username'], with_spaces=True)  # username
    win_panel.child_window(title="密码(W):", auto_id="-31801", control_type="Edit").type_keys(
        test_data['password'], with_spaces=True)  # password
    win_panel.child_window(title="端口(P):", auto_id="-31799", control_type="Edit").type_keys(
        test_data['port'], with_spaces=True)  # port
    win_panel.child_window(title="快速连接(Q)", auto_id="-31929", control_type="Button").click()  # quick connect


if __name__ == '__main__':
    execute_file_path = str_file_path
    Application().start(execute_file_path)
    app = Application().connect(path=execute_file_path)
    win_filezilla = app.window(title=u'FileZilla')
    try:
        test(win_filezilla)
        time.sleep(10)
        win_filezilla.close()
    except Exception as e:
        win_filezilla.close()
        # raise e
