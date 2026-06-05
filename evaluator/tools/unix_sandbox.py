import subprocess

try:
    import resource
except ImportError:
    pass

class UnixProcessAPI:

    @classmethod
    def _limit_unix_resource(cls) -> None:
        setrlimit = resource.setrlimit # type: ignore
        setrlimit(resource.RLIMIT_CPU, (5, 5)) # type: ignore
        #setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, -1)) # type: ignore
        setrlimit(resource.RLIMIT_NOFILE, (10, 10)) # type: ignore
        #setrlimit(resource.RLIMIT_NPROC, (0, 0)) # type: ignore

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
