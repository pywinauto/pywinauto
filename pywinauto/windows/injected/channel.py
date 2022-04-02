import pywintypes
import time
import win32file
import win32pipe
import winerror
import sys


class BrokenPipeError(Exception):
    pass

class Pipe:
    def __init__(self, name):
        self.name = name
        self.handle = None

    def connect(self, n_attempts=100, delay=1):
        for i in range(n_attempts):
            try:
                self.handle = win32file.CreateFile(
                    r'\\.\pipe\{}'.format(self.name),
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                ret = win32pipe.SetNamedPipeHandleState(
                        self.handle,
                        win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                        None,
                        None,
                    )
                # if ret != winerror.S_OK:
                #     print('SetNamedPipeHandleState exit code is {}'.format(ret))

                #print(f'Connected to the pipe {self.name}, {self.handle=}')
                break
            except pywintypes.error as e:
                if e.args[0] == winerror.ERROR_FILE_NOT_FOUND:
                    #print("Attempt {}: connection failed, trying again".format(i + 1))
                    time.sleep(delay)
                else:
                    raise BrokenPipeError('Unexpected pipe error: {}'.format(e))
        if self.handle is not None:
            return True
        return False

    def transact(self, string):
        try:
            win32file.WriteFile(self.handle, string.encode('utf-8'))
            win32file.FlushFileBuffers(self.handle)
            resp = win32file.ReadFile(self.handle, 64 * 1024)
            #print('message: {}'.format(resp[1].decode(sys.getdefaultencoding())))
            return resp[1].decode(sys.getdefaultencoding())
        except pywintypes.error as e:
            if e.args[0] == winerror.ERROR_BROKEN_PIPE:
                raise BrokenPipeError("Broken pipe")
            else:
                raise BrokenPipeError('Unexpected pipe error: {}'.format(e))
            return ''

    def close(self):
        win32file.CloseHandle(self.handle)

