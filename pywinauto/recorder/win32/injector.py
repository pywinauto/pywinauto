from ...handleprops import processid
from ...handleprops import is64bitprocess
from ...timings import TimeoutError as WaitError
from ... import win32defines
from ... import win32functions
from ... import win32structures
from ... import sysinfo
import ctypes
import six
import os

# Relative path, would be changed after adding to pywinauto
dll_path = "./pywinauto/recorder/win32/dll_to_inject/"
# TODO: add timeout to pywinauto timings and replace
remote_call_timeout = 1000
remote_call_error_str = "Couldn't create remote thread, dll not injected, inject and try again!"
remote_call_injection_error_str = "Couldn't create remote thread"
pipe_name = "\\\\.\\pipe\\pywinauto_recorder_pipe"
pipe_buffer_size = 1024

GetProcAddress = ctypes.windll.kernel32.GetProcAddress
GetProcAddress.restype = ctypes.c_void_p
GetProcAddress.argtypes = (ctypes.c_void_p, ctypes.c_char_p)

def byte_string(in_string):
    if isinstance(in_string, six.binary_type):
        return in_string
    if isinstance(in_string, six.text_type):
        return in_string.encode('utf-8')
    else:
        return str(in_string).encode('utf-8')

def unicode_string(in_string):
    if isinstance(in_string, six.text_type):
        return in_string
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
        pipe_flags = win32defines.PIPE_TYPE_MESSAGE | win32defines.PIPE_READMODE_MESSAGE | win32defines.PIPE_WAIT
        h_pipe = ctypes.windll.kernel32.CreateNamedPipeA(byte_string(pipe_name),
                                                         win32defines.PIPE_ACCESS_DUPLEX,
                                                         pipe_flags,
                                                         win32defines.PIPE_UNLIMITED_INSTANCES,
                                                         pipe_buffer_size,
                                                         pipe_buffer_size,
                                                         win32defines.NMPWAIT_USE_DEFAULT_WAIT,
                                                         None
                                                        )
        if (h_pipe == win32defines.INVALID_HANDLE_VALUE):
            return None

        if ctypes.windll.kernel32.GetLastError() == win32defines.ERROR_PIPE_CONNECTED:
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
        process_all_access =  win32defines.PROCESS_VM_OPERATION | win32defines.PROCESS_VM_READ | win32defines.PROCESS_VM_WRITE
        return win32functions.OpenProcess(process_all_access, False, pid)

    def _create_remote_thread(self, proc_address, arg_address, call_err_text = remote_call_error_str):
        CreateRemoteThread = ctypes.windll.kernel32.CreateRemoteThread
        c_function_adress = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)
        thread_handle = CreateRemoteThread(self.h_process, None, 0, c_function_adress(proc_address), arg_address, 0, None)
        if not thread_handle:
            raise RuntimeError(call_err_text)
        return thread_handle

    def _virtual_alloc_for(self, buffer):
        virtual_mem = win32defines.MEM_RESERVE | win32defines.MEM_COMMIT
        address = ctypes.c_void_p(win32functions.VirtualAllocEx(self.h_process, 0, ctypes.sizeof(buffer), virtual_mem, win32defines.PAGE_READWRITE))
        if not win32functions.WriteProcessMemory(self.h_process, address, ctypes.byref(buffer), ctypes.sizeof(buffer), 0):
            raise AttributeError("Couldn't write data to process memory, check python acceess.")
        return address

    def _inject_dll_to_process(self):
        # Convert dll path to unicode c_str
        c_dll_path = ctypes.create_unicode_buffer(self.dll_path)
        arg_address = self._virtual_alloc_for(c_dll_path)

        # Get LoadLibraryW Address
        GetModuleHandleW = ctypes.windll.kernel32.GetModuleHandleW
        GetModuleHandleW.restype = ctypes.c_void_p
        h_kernel32 = GetModuleHandleW(ctypes.c_wchar_p(unicode_string("kernel32.dll")))
        h_loadlib = GetProcAddress(h_kernel32, byte_string("LoadLibraryW"))

        # Now call CreateRemoteThread with entry point set to LoadLibraryW and pointer to DLL path as param
        thread_handle = self._create_remote_thread(h_loadlib, arg_address, remote_call_injection_error_str)

        ret = win32functions.WaitForSingleObject(thread_handle, remote_call_timeout)
        if ret == win32defines.WAIT_TIMEOUT:
            raise WaitError("Injection time out")

    def _get_dll_proc_address(self, proc_name):
        LoadLibraryW = ctypes.windll.kernel32.LoadLibraryW
        LoadLibraryW.restype = ctypes.c_void_p
        lib = LoadLibraryW(self.dll_path)
        return GetProcAddress(lib, byte_string(proc_name))

    def _remote_call_void_func(self, func_name):
        proc_address = self._get_dll_proc_address(func_name)
        self._create_remote_thread(proc_address, 0, remote_call_error_str)

    def _remote_call_int_param_func(self, func_name, param):
        arg_address = self._virtual_alloc_for(ctypes.c_int32(param))
        proc_address = self._get_dll_proc_address(func_name)
        self._create_remote_thread(proc_address, arg_address)

    def _remote_call_int_arr_param_func(self, func_name, param):
        arg_address = self._virtual_alloc_for((ctypes.c_int * len(param))(*param))
        proc_address = self._get_dll_proc_address(func_name)
        self._create_remote_thread(proc_address, arg_address)
