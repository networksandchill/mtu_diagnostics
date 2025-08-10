import platform
import subprocess
import sys
from typing import List, Dict, Any

def get_platform_info() -> Dict[str, str]:
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine()
    }

def run_command(cmd: List[str], timeout: int = 10) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def is_admin() -> bool:
    try:
        if sys.platform == 'win32':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            import os
            return os.geteuid() == 0
    except Exception:
        return False