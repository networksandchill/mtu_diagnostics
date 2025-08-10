from typing import Dict, List, Optional, Any
from .interface import InterfaceManager, NetworkInterface
from .tester import MTUTester

class MTUDetector:
    def __init__(self):
        self.interface_manager = InterfaceManager()
        self.tester = MTUTester()
    
    def detect_interface_mtu(self, interface_name: Optional[str] = None) -> Dict[str, Any]:
        if interface_name:
            interface = self.interface_manager.get_interface_by_name(interface_name)
            if not interface:
                return {
                    'success': False,
                    'error': f'Interface {interface_name} not found'
                }
        else:
            interface = self.interface_manager.get_default_interface()
            if not interface:
                return {
                    'success': False,
                    'error': 'No active network interface found'
                }
        
        return {
            'success': True,
            'interface': {
                'name': interface.name,
                'mtu': interface.mtu,
                'is_up': interface.is_up,
                'type': interface.type,
                'addresses': interface.addresses
            }
        }
    
    def detect_path_mtu(self, target: str, interface_name: Optional[str] = None) -> Dict[str, Any]:
        interface_info = self.detect_interface_mtu(interface_name)
        if not interface_info['success']:
            return interface_info
        
        interface = interface_info['interface']
        
        # Test maximum working MTU to target
        mtu_result = self.tester.find_max_mtu(target, start_size=interface['mtu'])
        
        result = {
            'success': mtu_result['success'],
            'interface': interface,
            'target': target
        }
        
        if mtu_result['success']:
            result.update({
                'path_mtu': mtu_result['max_mtu'],
                'interface_mtu': interface['mtu'],
                'mtu_optimal': mtu_result['max_mtu'] >= interface['mtu'],
                'target_ip': mtu_result['ip']
            })
        else:
            result['error'] = mtu_result.get('error', 'MTU detection failed')
        
        return result
    
    def get_all_interfaces_info(self) -> Dict[str, Any]:
        interfaces = self.interface_manager.get_all_interfaces()
        
        return {
            'success': True,
            'interfaces': [
                {
                    'name': iface.name,
                    'mtu': iface.mtu,
                    'is_up': iface.is_up,
                    'type': iface.type,
                    'addresses': iface.addresses
                }
                for iface in interfaces
            ]
        }
    
    def comprehensive_mtu_test(self, target: str, interface_name: Optional[str] = None) -> Dict[str, Any]:
        # Get interface info
        interface_info = self.detect_interface_mtu(interface_name)
        if not interface_info['success']:
            return interface_info
        
        interface = interface_info['interface']
        
        # Test path MTU
        path_mtu_result = self.tester.find_max_mtu(target, start_size=interface['mtu'])
        
        # Test common MTU sizes
        common_sizes_result = self.tester.test_common_sizes(target)
        
        # Test jumbo frames if interface supports them
        jumbo_result = None
        if interface['mtu'] > 1500:
            jumbo_result = self.tester.test_jumbo_frames(target)
        
        return {
            'success': True,
            'interface': interface,
            'target': target,
            'path_mtu': path_mtu_result,
            'common_sizes_test': common_sizes_result,
            'jumbo_frames_test': jumbo_result
        }