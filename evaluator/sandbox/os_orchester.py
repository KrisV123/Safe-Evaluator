from evaluator.sandbox.base import Sandbox
from platform import system

OS = system()

def get_sandbox() -> type[Sandbox]:
    """function, that returns correct sandbox API"""

    if OS == 'Windows':
        from evaluator.sandbox.windows_api import WindowsProcessAPI
        return WindowsProcessAPI
    elif OS in ('Linux', 'Darwin'):
        from evaluator.sandbox.unix_api import UnixProcessAPI
        return UnixProcessAPI
    else:
        raise RuntimeError(f'api for {OS} does not exist')
