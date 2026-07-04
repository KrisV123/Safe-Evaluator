from abc import ABC, abstractmethod
from dataclasses import dataclass

class Sandbox(ABC):
    """Abstract class for OS api, that create limited processes"""

    @dataclass(slots=True, frozen=True)
    class ReturnTypes:
        pass

    @dataclass(slots=True, frozen=True)
    class Output(ReturnTypes):
        """Valid output from subprocess worker without any error"""
        value: str


    @dataclass(slots=True, frozen=True)
    class Error(ReturnTypes):
        """Generic parent error class for other errors"""
        pass


    @dataclass(slots=True, frozen=True)
    class SubprocessError(Error):
        """Error from subprocess worker script"""
        value: str
    

    @dataclass(slots=True, frozen=True)
    class WallKill(Error):
        """Process killed by reaching wall-clock time limit"""
        pass


    @dataclass(slots=True, frozen=True)
    class KilledProcess(Error):
        """Forcefully killed subprocess with signal"""
        signal: int


    @classmethod
    @abstractmethod
    def create_process(cls,
                       cmd: list[str],
                       input: str,
                       time_limit: int=5,
                       memory_limit: int=100) -> Output | Error:
        ...
