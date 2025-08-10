import socket
import platform
from typing import List, Dict, Optional
from .platform import run_command

def is_valid_ip(ip: str) -> bool:
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def resolve_hostname(hostname: str) -> Optional[str]:
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def get_ping_command(target: str, size: int, dont_fragment: bool = True) -> List[str]:
    system = platform.system().lower()
    
    if system == 'windows':
        cmd = ['ping', '-n', '1', '-l', str(size)]
        if dont_fragment:
            cmd.extend(['-f'])
        cmd.append(target)
    elif system == 'darwin':  # macOS
        cmd = ['ping', '-c', '1', '-s', str(size)]
        if dont_fragment:
            cmd.extend(['-D'])
        cmd.append(target)
    else:  # Linux and others
        cmd = ['ping', '-c', '1', '-s', str(size)]
        if dont_fragment:
            cmd.extend(['-M', 'do'])
        cmd.append(target)
    
    return cmd

def ping_with_size(target: str, size: int, dont_fragment: bool = True, timeout: int = 5) -> Dict[str, any]:
    cmd = get_ping_command(target, size, dont_fragment)
    result = run_command(cmd, timeout)
    
    success = result['success']
    if not success and result['stderr']:
        if any(phrase in result['stderr'].lower() for phrase in 
               ['message too long', 'packet too big', 'fragmentation needed']):
            return {'success': False, 'reason': 'mtu_exceeded', 'output': result}
    
    return {
        'success': success,
        'reason': 'ok' if success else 'failed',
        'output': result
    }