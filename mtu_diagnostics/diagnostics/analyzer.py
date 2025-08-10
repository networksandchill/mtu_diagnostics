from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MTURecommendation:
    issue: str
    severity: str  # 'low', 'medium', 'high'
    description: str
    recommendation: str
    optimal_mtu: Optional[int] = None

class DiagnosticAnalyzer:
    def __init__(self):
        self.common_issues = {
            'pppoe_overhead': {
                'description': 'PPPoE connection reduces standard Ethernet MTU from 1500 to 1492',
                'recommendation': 'Set MTU to 1492 for PPPoE connections',
                'optimal_mtu': 1492
            },
            'vpn_overhead': {
                'description': 'VPN tunneling adds overhead, reducing effective MTU',
                'recommendation': 'Reduce MTU by 50-100 bytes for VPN connections',
                'optimal_mtu': None
            },
            'fragmentation': {
                'description': 'Packets are being fragmented due to MTU mismatch',
                'recommendation': 'Reduce MTU to avoid fragmentation',
                'optimal_mtu': None
            },
            'jumbo_mismatch': {
                'description': 'Interface supports jumbo frames but path does not',
                'recommendation': 'Disable jumbo frames or set appropriate MTU',
                'optimal_mtu': 1500
            },
            'suboptimal_mtu': {
                'description': 'Current MTU is smaller than optimal for this path',
                'recommendation': 'Increase MTU to improve performance',
                'optimal_mtu': None
            }
        }
    
    def analyze_mtu_results(self, detection_result: Dict[str, Any]) -> List[MTURecommendation]:
        recommendations = []
        
        if not detection_result.get('success'):
            return recommendations
        
        interface = detection_result.get('interface', {})
        path_mtu_data = detection_result.get('path_mtu', {})
        common_sizes = detection_result.get('common_sizes_test', {})
        
        interface_mtu = interface.get('mtu', 0)
        path_mtu = path_mtu_data.get('max_mtu') if path_mtu_data.get('success') else None
        
        if path_mtu and interface_mtu:
            recommendations.extend(self._analyze_mtu_mismatch(interface_mtu, path_mtu))
        
        if common_sizes and common_sizes.get('success'):
            recommendations.extend(self._analyze_common_sizes(common_sizes.get('results', []), interface_mtu))
        
        # Check for specific connection types
        recommendations.extend(self._check_connection_specific_issues(interface, path_mtu))
        
        return recommendations
    
    def _analyze_mtu_mismatch(self, interface_mtu: int, path_mtu: int) -> List[MTURecommendation]:
        recommendations = []
        
        mtu_diff = interface_mtu - path_mtu
        
        if mtu_diff > 0:
            severity = 'high' if mtu_diff > 100 else 'medium'
            recommendations.append(MTURecommendation(
                issue='mtu_mismatch',
                severity=severity,
                description=f'Interface MTU ({interface_mtu}) is larger than path MTU ({path_mtu})',
                recommendation=f'Reduce interface MTU to {path_mtu} to avoid fragmentation',
                optimal_mtu=path_mtu
            ))
        
        elif mtu_diff < -50:  # Path MTU significantly larger
            recommendations.append(MTURecommendation(
                issue='suboptimal_mtu',
                severity='low',
                description=f'Interface MTU ({interface_mtu}) is smaller than path MTU ({path_mtu})',
                recommendation=f'Consider increasing interface MTU to {path_mtu} for better performance',
                optimal_mtu=path_mtu
            ))
        
        return recommendations
    
    def _analyze_common_sizes(self, results: List[Dict], interface_mtu: int) -> List[MTURecommendation]:
        recommendations = []
        
        # Find the largest working MTU size
        working_sizes = [r['mtu_size'] for r in results if r['success']]
        failed_sizes = [r['mtu_size'] for r in results if not r['success']]
        
        if not working_sizes:
            recommendations.append(MTURecommendation(
                issue='no_connectivity',
                severity='high',
                description='No MTU sizes are working - network connectivity issue',
                recommendation='Check network connectivity and routing'
            ))
            return recommendations
        
        max_working = max(working_sizes)
        
        # Check for PPPoE signature (1492 works but 1500 doesn't)
        if 1492 in working_sizes and 1500 in failed_sizes:
            recommendations.append(MTURecommendation(
                issue='pppoe_overhead',
                severity='medium',
                description=self.common_issues['pppoe_overhead']['description'],
                recommendation=self.common_issues['pppoe_overhead']['recommendation'],
                optimal_mtu=1492
            ))
        
        # Check for other common overhead patterns
        elif max_working < 1500 and 1500 in failed_sizes:
            recommendations.append(MTURecommendation(
                issue='tunnel_overhead',
                severity='medium',
                description=f'Maximum working MTU is {max_working}, suggesting tunnel overhead',
                recommendation=f'Use MTU of {max_working} or investigate tunnel configuration',
                optimal_mtu=max_working
            ))
        
        return recommendations
    
    def _check_connection_specific_issues(self, interface: Dict, path_mtu: Optional[int]) -> List[MTURecommendation]:
        recommendations = []
        
        interface_type = interface.get('type', 'unknown')
        interface_mtu = interface.get('mtu', 0)
        
        # Jumbo frame analysis
        if interface_mtu > 1500:
            if path_mtu and path_mtu <= 1500:
                recommendations.append(MTURecommendation(
                    issue='jumbo_mismatch',
                    severity='medium',
                    description=self.common_issues['jumbo_mismatch']['description'],
                    recommendation=self.common_issues['jumbo_mismatch']['recommendation'],
                    optimal_mtu=1500
                ))
        
        # Wireless-specific recommendations
        if interface_type == 'wireless' and interface_mtu == 1500:
            recommendations.append(MTURecommendation(
                issue='wireless_optimization',
                severity='low',
                description='Wireless connections may benefit from slightly reduced MTU',
                recommendation='Consider reducing MTU to 1472 for wireless connections',
                optimal_mtu=1472
            ))
        
        return recommendations
    
    def generate_summary(self, recommendations: List[MTURecommendation]) -> Dict[str, Any]:
        if not recommendations:
            return {
                'status': 'optimal',
                'message': 'No MTU issues detected',
                'severity': 'none'
            }
        
        high_severity = [r for r in recommendations if r.severity == 'high']
        medium_severity = [r for r in recommendations if r.severity == 'medium']
        
        if high_severity:
            return {
                'status': 'issues_found',
                'message': f'{len(high_severity)} high-priority MTU issues found',
                'severity': 'high',
                'critical_issues': len(high_severity)
            }
        elif medium_severity:
            return {
                'status': 'issues_found',
                'message': f'{len(medium_severity)} medium-priority MTU issues found',
                'severity': 'medium',
                'issues': len(medium_severity)
            }
        else:
            return {
                'status': 'minor_issues',
                'message': f'{len(recommendations)} minor MTU optimization opportunities found',
                'severity': 'low',
                'optimizations': len(recommendations)
            }