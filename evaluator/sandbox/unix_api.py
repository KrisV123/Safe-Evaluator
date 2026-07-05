import subprocess
import functools
from platform import system
from evaluator.sandbox.base import Sandbox

try:
    import resource
except ImportError:
    pass

OS = system()

class UnixProcessAPI(Sandbox):

    @classmethod
    def _limit_unix_resource(cls, time_limit: int, memory_limit: int) -> None:
        setrlimit = resource.setrlimit # type:ignore

        setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit)) # type:ignore
        setrlimit(resource.RLIMIT_NOFILE, (10, 10)) # type:ignore
        setrlimit(resource.RLIMIT_NPROC, (0, 0)) # type:ignore
        setrlimit(resource.RLIMIT_STACK, (4 * 1024**2, 4 * 1024**2)) #type:ignore
        setrlimit(resource.RLIMIT_CORE, (0, 0)) #type:ignore
        setrlimit(resource.RLIMIT_MEMLOCK, (0, 0)) #type:ignore

        if OS == 'Linux':
            setrlimit(resource.RLIMIT_AS, (memory_limit * 1024 * 1024, -1)) # type:ignore
            setrlimit(resource.RLIMIT_MSGQUEUE, (0, 0)) # type:ignore
            setrlimit(resource.RLIMIT_NICE, (0, 0)) #type:ignore
            setrlimit(resource.RLIMIT_RTTIME, (0, 0)) #type:ignore
            setrlimit(resource.RLIMIT_SIGPENDING, (32, 32)) #type:ignore

    @classmethod
    def create_process(cls,
                       cmd: list[str],
                       input: str,
                       time_limit:int=5,
                       memory_limit:int=100) -> Sandbox.Output | Sandbox.Error:
        preset_limit_unix_resource = functools.partial(
            cls._limit_unix_resource,
            time_limit=time_limit, memory_limit=memory_limit
        )
        try:
            p = subprocess.run(
                cmd,
                input=input,
                text=True,
                capture_output=True,
                timeout=time_limit,
                preexec_fn=preset_limit_unix_resource
            )
        except subprocess.TimeoutExpired:
            return cls.WallKill()

        returncode = p.returncode
        if returncode < 0:
            return cls.KilledProcess(returncode)
        elif returncode != 0:
            return cls.SubprocessError(p.stderr)
        return cls.Output(p.stdout)
