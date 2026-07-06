import ctypes
import threading
import time
from contextlib import ExitStack
from typing import Literal, Any

import ctypes
from ctypes import wintypes
KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)

from evaluator.sandbox.base import Sandbox

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD)
    ]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64)
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS), ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t)
    ]


class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb",              wintypes.DWORD),
        ("lpReserved",      wintypes.LPWSTR),
        ("lpDesktop",       wintypes.LPWSTR),
        ("lpTitle",         wintypes.LPWSTR),
        ("dwX",             wintypes.DWORD),
        ("dwY",             wintypes.DWORD),
        ("dwXSize",         wintypes.DWORD),
        ("dwYSize",         wintypes.DWORD),
        ("dwXCountChars",   wintypes.DWORD),
        ("dwYCountChars",   wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags",         wintypes.DWORD),
        ("wShowWindow",     wintypes.WORD),
        ("cbReserved2",     wintypes.WORD),
        ("lpReserved2",     wintypes.LPBYTE),
        ("hStdInput",       wintypes.HANDLE),
        ("hStdOutput",      wintypes.HANDLE),
        ("hStdError",       wintypes.HANDLE)
    ]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL),
    ]


# declaring ABI arguments

KERNEL32.GetProcessHandleCount.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.DWORD)
    ]
KERNEL32.GetProcessHandleCount.restype = wintypes.BOOL

KERNEL32.TerminateProcess.argtypes = [
    wintypes.HANDLE,
    wintypes.UINT
]
KERNEL32.TerminateProcess.restype = wintypes.BOOL

LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)

KERNEL32.CreateJobObjectW.argtypes = [
    LPSECURITY_ATTRIBUTES,
    wintypes.LPCWSTR
]
KERNEL32.CreateJobObjectW.restype = wintypes.HANDLE

KERNEL32.CreateProcessW.argtypes = [
    wintypes.LPCWSTR, wintypes.LPWSTR,  wintypes.LPVOID,
    wintypes.LPVOID,  wintypes.BOOL,    wintypes.DWORD,
    wintypes.LPVOID,  wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFO),
    ctypes.POINTER(PROCESS_INFORMATION)
]

KERNEL32.WriteFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPCVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID
]
KERNEL32.WriteFile.restype = wintypes.BOOL

KERNEL32.PeekNamedPipe.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(wintypes.DWORD)
]
KERNEL32.PeekNamedPipe.restype = wintypes.BOOL

KERNEL32.WaitForSingleObject.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD
]
KERNEL32.WaitForSingleObject.restype = wintypes.DWORD

JOBOBJECTINFOCLASS = ctypes.c_int

KERNEL32.SetInformationJobObject.argtypes = [
    wintypes.HANDLE,
    JOBOBJECTINFOCLASS,
    wintypes.LPVOID,
    wintypes.DWORD
]
KERNEL32.SetInformationJobObject.restype = wintypes.BOOL

KERNEL32.CreatePipe.argtypes = [
    ctypes.POINTER(wintypes.HANDLE),
    ctypes.POINTER(wintypes.HANDLE),
    LPSECURITY_ATTRIBUTES,
    wintypes.DWORD
]
KERNEL32.CreatePipe.restype = wintypes.BOOL

KERNEL32.SetHandleInformation.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD
]
KERNEL32.SetHandleInformation.restype = wintypes.BOOL

KERNEL32.CloseHandle.argtypes = [wintypes.HANDLE]
KERNEL32.CloseHandle.restype = wintypes.BOOL

KERNEL32.AssignProcessToJobObject.argtypes = [
    wintypes.HANDLE,
    wintypes.HANDLE
]
KERNEL32.AssignProcessToJobObject.restype = wintypes.BOOL

KERNEL32.ResumeThread.argtypes = [wintypes.HANDLE]
KERNEL32.ResumeThread.restype = wintypes.DWORD

KERNEL32.ReadFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID
]
KERNEL32.ReadFile.restype = wintypes.BOOL

class WindowsProcessAPI(Sandbox):
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000

    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    CREATE_SUSPENDED = 0x00000004
    STARTF_USESTDHANDLES = 0x00000100
    HANDLE_FLAG_INHERIT = 1

    @classmethod
    def _check_time(cls, start_time: float, time_limit: int) -> bool:
        current_time = time.monotonic()
        running_time = current_time - start_time
        return True if running_time > time_limit else False
    
    @classmethod
    def _check_handle(cls, pi: PROCESS_INFORMATION, handle_limit: int) -> bool:
        handle_count = wintypes.DWORD()
        KERNEL32.GetProcessHandleCount(
            pi.hProcess,
            ctypes.byref(handle_count)
        )
        return True if handle_count.value > handle_limit else False
    
    @classmethod
    def _watchdog(cls,
                  pi: PROCESS_INFORMATION,
                  time_limit: int,
                  handle_limit: int,
                  event: threading.Event):
        """
        Check, if ammount of handles is not larger than limit
        of process is executing longer then time limit.
        If yes, process will will be killed.
        Meant to be executed in parallel.
        """

        start_time = time.monotonic()

        while not event.is_set():
            is_time_over = cls._check_time(start_time, time_limit)
            is_handle_over = cls._check_handle(pi, handle_limit)

            if is_time_over or is_handle_over:
                success = KERNEL32.TerminateProcess(pi.hProcess, 1)
                cls.check_os_error(success)

            event.wait(0.05)

    @classmethod
    def _create_pipe(cls,
                     r_handle: wintypes.HANDLE,
                     w_handle: wintypes.HANDLE,
                     inherit: Literal['r', 'w', 'rw']) -> None:
        """Create pipe from handles. Needs to be closed manually"""

        success = KERNEL32.CreatePipe(ctypes.byref(r_handle), ctypes.byref(w_handle), None, 0)
        cls.check_os_error(success)

        if inherit == 'r':
            success = KERNEL32.SetHandleInformation(r_handle, cls.HANDLE_FLAG_INHERIT, 1)
            cls.check_os_error(success)
            success = KERNEL32.SetHandleInformation(w_handle, cls.HANDLE_FLAG_INHERIT, 0)
            cls.check_os_error(success)
        elif inherit == 'w':
            success = KERNEL32.SetHandleInformation(r_handle, cls.HANDLE_FLAG_INHERIT, 0)
            cls.check_os_error(success)
            success = KERNEL32.SetHandleInformation(w_handle, cls.HANDLE_FLAG_INHERIT, 1)
            cls.check_os_error(success)
        elif inherit == 'rw':
            success = KERNEL32.SetHandleInformation(r_handle, cls.HANDLE_FLAG_INHERIT, 1)
            cls.check_os_error(success)
            success = KERNEL32.SetHandleInformation(w_handle, cls.HANDLE_FLAG_INHERIT, 1)
            cls.check_os_error(success)
        else:
            raise SyntaxError('inherit literal does not exist')

    @classmethod
    def _read_pipe(cls, buffer: bytes, r_handle: wintypes.HANDLE, output_size: int=8192) -> bytes:
        """Accumulate new read bytes to buffer. Meant to be executed in reading loop"""

        available_out = wintypes.DWORD()
        KERNEL32.PeekNamedPipe(r_handle, None, 0, None, ctypes.byref(available_out), None)
        if available_out.value > 0:
            out_buffer = ctypes.create_string_buffer(output_size)
            out_size = wintypes.DWORD()
            success = KERNEL32.ReadFile(r_handle, out_buffer, output_size, ctypes.byref(out_size), None)
            if success and out_size.value > 0:
                buffer += out_buffer.raw[:out_size.value]

        return buffer
    
    @classmethod
    def _safe_close(cls, handle: wintypes.HANDLE) -> None:
        """
        better alternative to closing handles to avoid undefined state.
        Checks if handle value is valid. If not, closing is skipped.

        ONLY for wintypes.HANDLE() objects. Handles evalved to int will not work.
        """

        if handle.value is not None:
            success = KERNEL32.CloseHandle(handle)
            cls.check_os_error(success)
            handle.value = None

    @classmethod
    def check_os_error(cls, success: Any) -> None:
        """raise exception, if OS error occures. Else do nothing"""

        if not success:
            err = ctypes.get_last_error()
            raise ctypes.WinError(err)

    @classmethod
    def create_process(cls,
                       cmd: list[str],
                       input: str,
                       time_limit:int=5,
                       memory_limit:int=100) -> Sandbox.Output | Sandbox.Error:
        """
        Execute command in separated process with given input and
        returns output or error wrapped in coresponding objects

        optional arguments are time_limit and memory_limit
        (time_limit is setted to user-space time and CPU time)
        """

        with ExitStack() as stack:
            job = KERNEL32.CreateJobObjectW(None, "sandbox_limits")
            stack.callback(KERNEL32.CloseHandle, job)

            info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()

            info.BasicLimitInformation.LimitFlags = (
                cls.JOB_OBJECT_LIMIT_PROCESS_MEMORY    |
                cls.JOB_OBJECT_LIMIT_PROCESS_TIME      |
                cls.JOB_OBJECT_LIMIT_ACTIVE_PROCESS    |
                cls.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            )
            info.ProcessMemoryLimit = memory_limit * 1024 * 1024 # 100 MB (default)
            info.BasicLimitInformation.PerProcessUserTimeLimit = time_limit * 10_000_000 # 5 seconds (default)
            info.BasicLimitInformation.ActiveProcessLimit = 1 # 1

            success = KERNEL32.SetInformationJobObject(
                job,
                cls.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                ctypes.byref(info),
                ctypes.sizeof(info)
            )
            cls.check_os_error(success)

            stdin_r = wintypes.HANDLE()
            stack.callback(cls._safe_close, stdin_r)
            stdin_w = wintypes.HANDLE()
            stack.callback(cls._safe_close, stdin_w)
            cls._create_pipe(stdin_r, stdin_w, 'r')

            stdout_r = wintypes.HANDLE()
            stack.callback(cls._safe_close, stdout_r)
            stdout_w = wintypes.HANDLE()
            stack.callback(cls._safe_close, stdout_w)
            cls._create_pipe(stdout_r, stdout_w, 'w')

            stderr_r = wintypes.HANDLE()
            stack.callback(cls._safe_close, stderr_r)
            stderr_w = wintypes.HANDLE()
            stack.callback(cls._safe_close, stderr_w)
            cls._create_pipe(stderr_r, stderr_w, 'w')

            si = STARTUPINFO()
            si.cb = ctypes.sizeof(si)

            si.dwFlags = cls.STARTF_USESTDHANDLES
            si.hStdInput, si.hStdOutput, si.hStdError = stdin_r, stdout_w, stderr_w

            pi = PROCESS_INFORMATION()

            joined_cmd = ' '.join(cmd)
            success = KERNEL32.CreateProcessW(
                None,
                ctypes.create_unicode_buffer(joined_cmd),
                None,
                None,
                True,
                cls.CREATE_SUSPENDED,
                None,
                None,
                ctypes.byref(si),
                ctypes.byref(pi)
            )
            cls.check_os_error(success)

            stack.callback(KERNEL32.CloseHandle, pi.hProcess)
            stack.callback(KERNEL32.CloseHandle, pi.hThread)

            cls._safe_close(stdin_r)
            cls._safe_close(stdout_w)
            cls._safe_close(stderr_w)

            success = KERNEL32.AssignProcessToJobObject(job, pi.hProcess)
            cls.check_os_error(success)

            handle_limit = 81 + 400
            stop_event = threading.Event()

            watchdog = threading.Thread(
                target=cls._watchdog,
                daemon=True,
                args=(pi, time_limit, handle_limit, stop_event)
            )
            watchdog.start()
            stack.callback(watchdog.join)
            stack.callback(stop_event.set)

            success = KERNEL32.ResumeThread(pi.hThread)
            cls.check_os_error(success)
            written = wintypes.DWORD()

            bytes_input = input.encode('utf-8')

            success = KERNEL32.WriteFile(
                stdin_w,
                bytes_input,
                len(bytes_input),
                ctypes.byref(written),
                None
            )
            cls.check_os_error(success)

            cls._safe_close(stdin_w)

            output, error = b'', b''
            while True:
                output = cls._read_pipe(output, stdout_r)
                error = cls._read_pipe(error, stderr_r)
                p_state = KERNEL32.WaitForSingleObject(pi.hProcess, 0)
                if p_state == 0:
                    break
                cls.check_os_error(p_state)
                time.sleep(0.01)

            cls._safe_close(stdout_r)
            cls._safe_close(stderr_r)

            if len(output) > 0 and len(error) == 0:
                return cls.Output(output.decode('utf-8'))
            elif len(output) == 0 and len(error) > 0:
                return cls.SubprocessError(error.decode('utf-8'))
            else:
                raise RuntimeError(
                    'Sandbox runtime error. Process did not survived to reading output'
                )
