from ...handleprops import processid
from ...handleprops import is64bitprocess
from ...timings import TimeoutError as WaitError
from ... import sysinfo
from socket import socket
from socket import AF_INET
from socket import SOCK_DGRAM
from . import cfuncs
import ctypes
import os
import six

# Relative path, would be changed after adding to pywinauto
dll_path = "./pywinauto/recorder/win32/dll_to_inject/"
# TODO: add timeout to pywinauto timings and replace
remote_call_timeout = 1000
remote_call_error_str = "Couldn't create remote thread, dll not injected, inject and try again!"
remote_call_injection_error_str = "Couldn't create remote thread"
pipe_name = "\\\\.\\pipe\\pywinauto_recorder_pipe"

def byte_string(in_string):
    if isinstance(in_string, six.binary_type):
        return in_string
    else:
        if isinstance(in_string, six.text_type):
            return in_string.encode('utf-8')
        else:
            return str(in_string).encode('utf-8')

def unicode_string(in_string):
    if isinstance(in_string, six.text_type):
        return in_string
    else:
        if isinstance(in_string, six.binary_type):
            return in_string.decode('utf-8')
        else:
            return str(in_string).decode('utf-8')

class Injector(object):

    """Class for injections dll and set hook on windows messages"""

    def __init__(self, app, is_unicode = False, approved_messages_list = []):
        """Constructor inject dll, set socket and hook (one application - one class instanse)"""
        self.pid = processid(app.handle)
        self._check_compatibility()
        self.approved_messages_list = [len(approved_messages_list)] + approved_messages_list
        self.app        = app
        self.is_unicode = is_unicode
        self.h_process  = self._get_process_handle(self.pid)
        self.dll_path   = self._get_dll_path()
        self.h_pipe     = self._init_pipe()
        self._inject_dll_to_process()
        self._remote_call_int_arr_param_func("SetApprovedList", self.approved_messages_list)
        self._remote_call_void_func("Initialize")
        self._connect()

    def _init_pipe(self):
        pipe_flags = cfuncs.PIPE_TYPE_MESSAGE | cfuncs.PIPE_READMODE_MESSAGE | cfuncs.PIPE_WAIT
        h_pipe = ctypes.windll.kernel32.CreateNamedPipeA(pipe_name,
                                                         cfuncs.PIPE_ACCESS_DUPLEX,
                                                         pipe_flags,
                                                         cfuncs.PIPE_UNLIMITED_INSTANCES,
                                                         cfuncs.BUFSIZE,
                                                         cfuncs.BUFSIZE,
                                                         cfuncs.NMPWAIT_USE_DEFAULT_WAIT,
                                                         None
                                                        )
        if (h_pipe == cfuncs.INVALID_HANDLE_VALUE):
            return None

        if ctypes.windll.kernel32.GetLastError() == cfuncs.ERROR_PIPE_CONNECTED:
            return None

        return h_pipe

    def _connect(self):
        connected = ctypes.windll.kernel32.ConnectNamedPipe(self.h_pipe, None)
        if connected == 0:
            raise RuntimeError("Could not connect to application pipe")

    def _get_dll_path(self):
        dll_name = "pywinmsg{}.dll".format("64" if is64bitprocess(self.pid) else "32")
        return unicode_string(os.path.abspath(os.path.join(dll_path, dll_name)))

    def _check_compatibility(self):
        if not sysinfo.is_x64_Python() == is64bitprocess(self.pid):
            raise RuntimeError("Application and Python must be both 32-bit or both 64-bit")

    def close_pipe(self):
        if not self.h_pipe:
            return
        ctypes.windll.kernel32.FlushFileBuffers(self.h_pipe)
        ctypes.windll.kernel32.DisconnectNamedPipe(self.h_pipe)
        ctypes.windll.kernel32.CloseHandle(self.h_pipe)

    def read_massage(self):
        if not self.h_pipe:
            return None
        msg = ctypes.wintypes.MSG()
        bytes_cnt = ctypes.c_ulong(0)
        status = ctypes.windll.kernel32.ReadFile(self.h_pipe, msg, ctypes.sizeof(msg), ctypes.byref(bytes_cnt), None)
        if status == 1 or bytes_cnt.value != 0:
            return msg
        return None

    @property
    def application(self):
        """Return hooked application"""
        return self.app

    @staticmethod
    def _get_process_handle(pid):
        return cfuncs.OpenProcess(cfuncs.PROCESS_ALL_ACCESS, False, pid)

    def _create_remote_thread(self, proc_address, arg_address, call_err_text = remote_call_error_str):
        thread_handle = cfuncs.CreateRemoteThread(self.h_process, None, 0, proc_address, arg_address, 0, None)
        if not thread_handle:
            raise RuntimeError(call_err_text)
        return thread_handle

    def _virtual_alloc_for(self, buffer):
        address = cfuncs.VirtualAllocEx(self.h_process, 0, ctypes.sizeof(buffer), cfuncs.VIRTUAL_MEM, cfuncs.PAGE_READWRITE)
        if not cfuncs.WriteProcessMemory(self.h_process, address, ctypes.byref(buffer), ctypes.sizeof(buffer), 0):
            raise AttributeError("Couldn't write data to process memory, check python acceess.")
        return address

    def _inject_dll_to_process(self):
        # Convert dll path to unicode c_str
        c_dll_path = ctypes.create_unicode_buffer(self.dll_path)
        arg_address = self._virtual_alloc_for(c_dll_path)

        # Get LoadLibraryW Address
        h_kernel32 = cfuncs.GetModuleHandleW(unicode_string("kernel32.dll"))
        h_loadlib = cfuncs.GetProcAddress(h_kernel32, byte_string("LoadLibraryW"))

        # Now call CreateRemoteThread with entry point set to LoadLibraryW and pointer to DLL path as param
        thread_handle = self._create_remote_thread(h_loadlib, arg_address, remote_call_injection_error_str)

        ret = cfuncs.WaitForSingleObject(thread_handle, ctypes.wintypes.DWORD(remote_call_timeout))
        if ret == cfuncs.WAIT_TIMEOUT:
            raise WaitError("Injection time out")

    def _get_dll_proc_address(self, proc_name):
        lib = cfuncs.LoadLibraryW(self.dll_path)
        return cfuncs.GetProcAddress(lib, byte_string(proc_name))

    def _remote_call_void_func(self, func_name):
        proc_address = self._get_dll_proc_address(func_name)
        if not cfuncs.CreateRemoteThread(self.h_process, None, 0, proc_address, 0, 0, None):
            raise RuntimeError(remote_call_error_str)

    def _remote_call_int_param_func(self, func_name, param):
        arg_address = self._virtual_alloc_for(ctypes.c_int32(param))
        proc_address = self._get_dll_proc_address(func_name)
        self._create_remote_thread(proc_address, arg_address)

    def _remote_call_int_arr_param_func(self, func_name, param):
        arg_address = self._virtual_alloc_for((ctypes.c_int * len(param))(*param))
        proc_address = self._get_dll_proc_address(func_name)
        self._create_remote_thread(proc_address, arg_address)
