from typing import Dict, Optional, List, Tuple
from ..utils.network import ping_with_size, resolve_hostname
from .interface import NetworkInterface

class MTUTester:
    def __init__(self):
        self.common_mtu_sizes = [1500, 1492, 1480, 1472, 1464, 1450, 1420, 1400, 1350, 1280, 1200, 576]
        self.jumbo_frame_sizes = [9000, 8000, 7000, 6000, 4000]
        
    def find_max_mtu(self, target: str, start_size: int = 1500, 
                     min_size: int = 576, timeout: int = 5) -> Dict[str, any]:
        ip = resolve_hostname(target)
        if not ip:
            return {
                'success': False,
                'error': f'Could not resolve hostname: {target}',
                'max_mtu': None
            }
        
        working_size = None
        failed_size = start_size + 1
        
        for size in sorted(self.common_mtu_sizes, reverse=True):
            if size > start_size:
                continue
                
            # Account for IP (20) and ICMP (8) headers
            payload_size = size - 28
            if payload_size < 0:
                continue
                
            result = ping_with_size(ip, payload_size, dont_fragment=True, timeout=timeout)
            
            if result['success']:
                working_size = size
                break
            elif result['reason'] == 'mtu_exceeded':
                failed_size = min(failed_size, size)
        
        if working_size is None:
            return {
                'success': False,
                'error': 'No working MTU size found',
                'max_mtu': None,
                'failed_at': failed_size
            }
        
        # Binary search for exact MTU between working_size and failed_size
        exact_mtu = self._binary_search_mtu(ip, working_size, failed_size, timeout)
        
        return {
            'success': True,
            'max_mtu': exact_mtu,
            'target': target,
            'ip': ip
        }
    
    def test_common_sizes(self, target: str, timeout: int = 5) -> Dict[str, any]:
        ip = resolve_hostname(target)
        if not ip:
            return {
                'success': False,
                'error': f'Could not resolve hostname: {target}',
                'results': []
            }
        
        results = []
        for mtu_size in self.common_mtu_sizes:
            payload_size = mtu_size - 28  # IP + ICMP headers
            if payload_size < 0:
                continue
                
            result = ping_with_size(ip, payload_size, dont_fragment=True, timeout=timeout)
            results.append({
                'mtu_size': mtu_size,
                'success': result['success'],
                'reason': result['reason']
            })
        
        return {
            'success': True,
            'target': target,
            'ip': ip,
            'results': results
        }
    
    def test_jumbo_frames(self, target: str, timeout: int = 10) -> Dict[str, any]:
        ip = resolve_hostname(target)
        if not ip:
            return {
                'success': False,
                'error': f'Could not resolve hostname: {target}',
                'jumbo_supported': False
            }
        
        for size in sorted(self.jumbo_frame_sizes, reverse=True):
            payload_size = size - 28
            result = ping_with_size(ip, payload_size, dont_fragment=True, timeout=timeout)
            
            if result['success']:
                return {
                    'success': True,
                    'jumbo_supported': True,
                    'max_jumbo_mtu': size,
                    'target': target,
                    'ip': ip
                }
        
        return {
            'success': True,
            'jumbo_supported': False,
            'target': target,
            'ip': ip
        }
    
    def _binary_search_mtu(self, ip: str, low: int, high: int, timeout: int) -> int:
        while high - low > 1:
            mid = (low + high) // 2
            payload_size = mid - 28
            
            result = ping_with_size(ip, payload_size, dont_fragment=True, timeout=timeout)
            
            if result['success']:
                low = mid
            else:
                high = mid
        
        return low