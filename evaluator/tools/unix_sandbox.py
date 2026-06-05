import subprocess
from platform import system

try:
    import resource
except ImportError:
    pass

OS = system()

class UnixProcessAPI:

    @classmethod
    def _limit_unix_resource(cls) -> None:
        setrlimit = resource.setrlimit # type:ignore
        setrlimit(resource.RLIMIT_CPU, (5, 5)) # type:ignore
        setrlimit(resource.RLIMIT_NOFILE, (10, 10)) # type:ignore
        setrlimit(resource.RLIMIT_NPROC, (0, 0)) # type:ignore
        setrlimit(resource.RLIMIT_STACK, (4 * 1024**2, 4 * 1024**2)) #type:ignore
        setrlimit(resource.RLIMIT_CORE, (0, 0)) #type:ignore
        setrlimit(resource.RLIMIT_MEMLOCK, (0, 0)) #type:ignore

        if OS == 'Linux':
            setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, -1)) # type:ignore
            setrlimit(resource.RLIMIT_MSGQUEUE, (0, 0)) # type:ignore
            setrlimit(resource.RLIMIT_NICE, (0, 0)) #type:ignore
            setrlimit(resource.RLIMIT_RTTIME, (0, 0)) #type:ignore
            setrlimit(resource.RLIMIT_SIGPENDING, (32, 32)) #type:ignore

    @classmethod
    def create_unix_process(cls, cmd: list[str], input: str) -> str:
        p = subprocess.run(
            cmd,
            input=input,
            text=True,
            capture_output=True,
            timeout=5,
            preexec_fn=cls._limit_unix_resource
        )
        if p.returncode != 0:
            raise RuntimeError(p.stderr)
        return p.stdout
