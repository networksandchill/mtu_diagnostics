import psutil
import platform
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..utils.platform import run_command

@dataclass
class NetworkInterface:
    name: str
    mtu: int
    is_up: bool
    addresses: List[str]
    type: str = "unknown"

class InterfaceManager:
    def __init__(self):
        self.system = platform.system().lower()
    
    def get_all_interfaces(self) -> List[NetworkInterface]:
        interfaces = []
        
        for interface_name, addrs in psutil.net_if_addrs().items():
            stats = psutil.net_if_stats().get(interface_name)
            if not stats:
                continue
                
            addresses = [addr.address for addr in addrs 
                        if addr.family in (psutil.AF_LINK, 2, 10)]  # MAC, IPv4, IPv6
            
            interface = NetworkInterface(
                name=interface_name,
                mtu=stats.mtu,
                is_up=stats.isup,
                addresses=addresses,
                type=self._get_interface_type(interface_name)
            )
            interfaces.append(interface)
        
        return interfaces
    
    def get_interface_by_name(self, name: str) -> Optional[NetworkInterface]:
        for interface in self.get_all_interfaces():
            if interface.name == name:
                return interface
        return None
    
    def get_default_interface(self) -> Optional[NetworkInterface]:
        try:
            if self.system == 'windows':
                result = run_command(['route', 'print', '0.0.0.0'])
                if result['success']:
                    lines = result['stdout'].split('\n')
                    for line in lines:
                        if '0.0.0.0' in line and 'Gateway' not in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                interface_ip = parts[3]
                                return self._find_interface_by_ip(interface_ip)
            
            elif self.system == 'darwin':
                result = run_command(['route', 'get', 'default'])
                if result['success']:
                    for line in result['stdout'].split('\n'):
                        if 'interface:' in line:
                            interface_name = line.split(':')[1].strip()
                            return self.get_interface_by_name(interface_name)
            
            else:  # Linux
                result = run_command(['ip', 'route', 'show', 'default'])
                if result['success']:
                    line = result['stdout'].split('\n')[0]
                    if 'dev' in line:
                        parts = line.split()
                        dev_index = parts.index('dev')
                        if dev_index + 1 < len(parts):
                            interface_name = parts[dev_index + 1]
                            return self.get_interface_by_name(interface_name)
                            
        except Exception:
            pass
        
        active_interfaces = [iface for iface in self.get_all_interfaces() 
                           if iface.is_up and iface.addresses]
        return active_interfaces[0] if active_interfaces else None
    
    def _get_interface_type(self, name: str) -> str:
        name_lower = name.lower()
        if 'eth' in name_lower or 'en' in name_lower:
            return 'ethernet'
        elif 'wlan' in name_lower or 'wi-fi' in name_lower or 'wifi' in name_lower:
            return 'wireless'
        elif 'lo' in name_lower or 'loopback' in name_lower:
            return 'loopback'
        elif 'tun' in name_lower or 'tap' in name_lower:
            return 'tunnel'
        else:
            return 'unknown'
    
    def _find_interface_by_ip(self, ip: str) -> Optional[NetworkInterface]:
        for interface in self.get_all_interfaces():
            if ip in interface.addresses:
                return interface
        return None