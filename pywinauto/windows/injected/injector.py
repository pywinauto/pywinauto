import json
import os
import time
import sys
from pywinauto.application import Application

from ctypes import windll, c_int, c_ulong, byref

from .channel import Pipe

PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF )
VIRTUAL_MEM = ( 0x1000 | 0x2000 )

kernel32 = windll.kernel32


def inject(pid):
    dll_path = (os.path.dirname(__file__) + os.sep + r'x64\bootstrap.dll').encode('utf-8')
    #dll_path = rb'D:\repo\pywinauto\dotnetguiauto\Debug\bootstrap.dll'

    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
    #print(f'{h_process=}')
    if not h_process:
        #print('')
        sys.exit(-1)

    arg_address = kernel32.VirtualAllocEx(h_process, 0, len(dll_path), VIRTUAL_MEM, PAGE_READWRITE)
    #print(f'{hex(arg_address)=}')

    written = c_int(0)
    kernel32.WriteProcessMemory(h_process, arg_address, dll_path, len(dll_path), byref(written))
    #print(f'{written=}')

    h_kernel32 = kernel32.GetModuleHandleA(b"kernel32.dll")
    #print(f'{h_kernel32=}')
    h_loadlib = kernel32.GetProcAddress(h_kernel32, b"LoadLibraryA")
    #print(f'{h_loadlib=}')

    thread_id = c_ulong(0)

    if not kernel32.CreateRemoteThread(
        h_process,
        None,
        0,
        h_loadlib,
        arg_address,
        0,
        byref(thread_id)
    ):
        #print('err inject')
        sys.exit(-2)

    #print(f'{thread_id=}')

def create_pipe(pid):
    pipe = Pipe(f'pywinauto_{pid}')
    if pipe.connect(n_attempts=1):
        return pipe
    else:
        inject(pid)
        #print('Inject successful, connecting to the server...')
        pipe.connect()
        return pipe

if __name__ == '__main__':
    app = Application().connect(path='WpfApplication1.exe')
    inject(app.process)
    #print('Inject successful, connecting to the server...')

    pipe = Pipe(f'pywinauto_{app.process}')
    pipe.connect()

    #command = f"{json.dumps({'action': 'getChildren'})}\n"
    #pipe.send_and_recv(command)

    #command = f"{json.dumps({'action': 'getChildren', 'element_id': 1})}\n"
    #pipe.send_and_recv(command)

    # command = f"{json.dumps({'action': 'getChildren', 'element_id': 2})}\n"
    # pipe.send_and_recv(command)
    # 
    # command = f"{json.dumps({'action': 'getChildren', 'element_id': 3})}\n"
    # pipe.send_and_recv(command)
    # 
    # command = f"{json.dumps({'action': 'getChildren', 'element_id': 4})}\n"
    # pipe.send_and_recv(command)
    # 
    # command = f"{json.dumps({'action': 'getChildren', 'element_id': 6})}\n"
    # pipe.send_and_recv(command)
    # 
    # command = f"{json.dumps({'action': 'getChildren', 'element_id': 8})}\n"
    # pipe.send_and_recv(command)
    # 
    # command = f"{json.dumps({'action': 'getChildren', 'element_id': 9})}\n"
    # pipe.send_and_recv(command)
    
    while True:
        action = input('Enter child ID or action: ')
        if action.isnumeric():
            currentElement = action
            command = f"{json.dumps({'action': 'GetChildren', 'element_id': int(action)})}\n"
            pipe.transact(command)
        elif action == 'name':
            command = f"{json.dumps({'action': 'GetProperty', 'element_id': int(currentElement), 'name': 'Name'})}\n"
            pipe.transact(command)
        elif action == 'q':
            break       
        else:
            print('err')

    pipe.close()
    #app.kill()
