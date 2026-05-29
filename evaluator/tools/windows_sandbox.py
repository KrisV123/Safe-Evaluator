import ctypes
import threading
import time
from dataclasses import dataclass
from typing import Literal
import ctypes
from ctypes import wintypes

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


class WindowsProcessAPI:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    CREATE_SUSPENDED = 0x00000004
    STARTF_USESTDHANDLES = 0x00000100
    HANDLE_FLAG_INHERIT = 1

    # declaring ABI arguments

    kernel32.GetProcessHandleCount.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.DWORD)
        ]
    kernel32.GetProcessHandleCount.restype = wintypes.BOOL

    kernel32.TerminateProcess.argtypes = [
        wintypes.HANDLE,
        wintypes.UINT
    ]
    kernel32.TerminateProcess.restype = wintypes.BOOL

    LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)

    kernel32.CreateJobObjectW.argtypes = [
        LPSECURITY_ATTRIBUTES,
        wintypes.LPCWSTR
    ]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE

    kernel32.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR,  wintypes.LPVOID,
        wintypes.LPVOID,  wintypes.BOOL,    wintypes.DWORD,
        wintypes.LPVOID,  wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFO),
        ctypes.POINTER(PROCESS_INFORMATION)
    ]

    kernel32.WriteFile.argtypes = [
        wintypes.HANDLE,
        wintypes.LPCVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID
    ]
    kernel32.WriteFile.restype = wintypes.BOOL

    kernel32.PeekNamedPipe.argtypes = [
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.PeekNamedPipe.restype = wintypes.BOOL

    kernel32.WaitForSingleObject.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD
    ]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD

    @classmethod
    def _watchdog_handles(cls, pi: PROCESS_INFORMATION, limit: int):
        """
        Check, if ammount of handles is not larger than limit.
        If yes, process will will be killed. Meant to be execudet in parallel.
        """

        while True:
            count = wintypes.DWORD()
            cls.kernel32.GetProcessHandleCount(
                pi.hProcess,
                ctypes.byref(count)
            )
            if count.value > limit:
                cls.kernel32.TerminateProcess(
                    pi.hProcess,
                    1
                )
            time.sleep(0.05)

    @classmethod
    def _create_pipe(cls, r_handle: wintypes.HANDLE, w_handle: wintypes.HANDLE, inherit: Literal['r', 'w', 'rw']):
        """Create pipe from handles. Needs to be closed manually"""

        cls.kernel32.CreatePipe(ctypes.byref(r_handle), ctypes.byref(w_handle), None, 0)

        if inherit == 'r':
            cls.kernel32.SetHandleInformation(r_handle, cls.HANDLE_FLAG_INHERIT, 1)
            cls.kernel32.SetHandleInformation(w_handle, cls.HANDLE_FLAG_INHERIT, 0)
        elif inherit == 'w':
            cls.kernel32.SetHandleInformation(r_handle, cls.HANDLE_FLAG_INHERIT, 0)
            cls.kernel32.SetHandleInformation(w_handle, cls.HANDLE_FLAG_INHERIT, 1)
        elif inherit == 'rw':
            cls.kernel32.SetHandleInformation(r_handle, cls.HANDLE_FLAG_INHERIT, 1)
            cls.kernel32.SetHandleInformation(w_handle, cls.HANDLE_FLAG_INHERIT, 1)
        else:
            raise SyntaxError('inherit literal does not exist')

    @classmethod
    def _read_pipe(cls, buffer: bytes, r_handle: wintypes.HANDLE, output_size: int=4096) -> bytes:
        """Accumulate new read bytes to buffer. Meant to be executed in reading loop"""

        available_out = wintypes.DWORD()
        cls.kernel32.PeekNamedPipe(r_handle, None, 0, None, ctypes.byref(available_out), None)
        if available_out.value > 0:
            out_buffer = ctypes.create_string_buffer(output_size)
            out_size = wintypes.DWORD()
            success = cls.kernel32.ReadFile(r_handle, out_buffer, output_size, ctypes.byref(out_size), None)
            if success and out_size.value > 0:
                buffer += out_buffer.raw[:out_size.value]

        return buffer

    @dataclass(slots=True, frozen=True)
    class Output:
        value: bytes

    @dataclass(slots=True, frozen=True)
    class Error:
        value: bytes

    @classmethod
    def create_windows_process(cls, cmd: str, input: bytes) -> Output | Error:
        """
        Execute command in separated process with given input and
        returns output or error wrapped in coresponding objects
        """

        job = cls.kernel32.CreateJobObjectW(None, "sandbox_limits")
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()

        info.BasicLimitInformation.LimitFlags = (
            cls.JOB_OBJECT_LIMIT_PROCESS_MEMORY |
            cls.JOB_OBJECT_LIMIT_PROCESS_TIME
        )
        info.ProcessMemoryLimit = 100 * 1024 * 1024 # 100 MB
        info.PerProcessUserTimeLimit = 5 * 10_000_000 # 5 seconds

        cls.kernel32.SetInformationJobObject(
            job,
            cls.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info)
        )

        stdin_r, stdin_w = wintypes.HANDLE(), wintypes.HANDLE()
        cls._create_pipe(stdin_r, stdin_w, 'r')
        stdout_r, stdout_w = wintypes.HANDLE(), wintypes.HANDLE()
        cls._create_pipe(stdout_r, stdout_w, 'w')
        stderr_r, stderr_w = wintypes.HANDLE(), wintypes.HANDLE()
        cls._create_pipe(stderr_r, stderr_w, 'w')

        si = STARTUPINFO()
        si.cb = ctypes.sizeof(si)

        si.dwFlags = cls.STARTF_USESTDHANDLES
        si.hStdInput, si.hStdOutput, si.hStdError = stdin_r, stdout_w, stderr_w

        pi = PROCESS_INFORMATION()

        cls.kernel32.CreateProcessW(
            None,
            ctypes.create_unicode_buffer(cmd),
            None,
            None,
            True,
            cls.CREATE_SUSPENDED,
            None,
            None,
            ctypes.byref(si),
            ctypes.byref(pi)
        )

        cls.kernel32.CloseHandle(stdin_r)
        cls.kernel32.CloseHandle(stdout_w)
        cls.kernel32.CloseHandle(stderr_w)

        cls.kernel32.AssignProcessToJobObject(job, pi.hProcess)

        threading.Thread(
            target=cls._watchdog_handles,
            daemon=True,
            args=(pi, 81 + 400) # 81 cca minimum + 400 extra
        ).start()

        cls.kernel32.ResumeThread(pi.hThread)
        written = wintypes.DWORD()

        cls.kernel32.WriteFile(
            stdin_w,
            input,
            len(input),
            ctypes.byref(written),
            None
        )
        cls.kernel32.CloseHandle(stdin_w)

        output, error = b'', b''
        while True:
            output = cls._read_pipe(output, stdout_r)
            error = cls._read_pipe(error, stderr_r)
            if cls.kernel32.WaitForSingleObject(pi.hProcess, 0) == 0:
                break
            time.sleep(0.01)

        cls.kernel32.CloseHandle(stdout_r)
        cls.kernel32.CloseHandle(stderr_r)

        if len(output) > 0 and len(error) == 0:
            return cls.Output(output)
        elif len(output) == 0 and len(error) > 0:
            return cls.Error(error)
        else:
            raise RuntimeError(
                'Sandbox runtime error. Process did not survived to reading output'
            )
