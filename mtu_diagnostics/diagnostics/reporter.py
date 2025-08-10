import json
from typing import Dict, List, Any, Optional
from .analyzer import MTURecommendation

class MTUReporter:
    def __init__(self, format_type: str = 'text'):
        self.format_type = format_type.lower()
    
    def format_interface_info(self, result: Dict[str, Any]) -> str:
        if not result.get('success'):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        interface = result['interface']
        
        if self.format_type == 'json':
            return json.dumps(result, indent=2)
        
        output = []
        output.append("=== Interface Information ===")
        output.append(f"Name: {interface['name']}")
        output.append(f"MTU: {interface['mtu']}")
        output.append(f"Status: {'Up' if interface['is_up'] else 'Down'}")
        output.append(f"Type: {interface['type']}")
        
        if interface['addresses']:
            output.append("Addresses:")
            for addr in interface['addresses']:
                output.append(f"  - {addr}")
        
        return '\n'.join(output)
    
    def format_path_mtu_result(self, result: Dict[str, Any]) -> str:
        if not result.get('success'):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        if self.format_type == 'json':
            return json.dumps(result, indent=2)
        
        output = []
        output.append("=== Path MTU Detection ===")
        output.append(f"Target: {result['target']}")
        output.append(f"Target IP: {result.get('target_ip', 'N/A')}")
        output.append(f"Interface: {result['interface']['name']}")
        output.append(f"Interface MTU: {result['interface_mtu']}")
        output.append(f"Path MTU: {result['path_mtu']}")
        output.append(f"MTU Optimal: {'Yes' if result['mtu_optimal'] else 'No'}")
        
        return '\n'.join(output)
    
    def format_comprehensive_test(self, result: Dict[str, Any]) -> str:
        if not result.get('success'):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        if self.format_type == 'json':
            return json.dumps(result, indent=2)
        
        output = []
        output.append("=== Comprehensive MTU Test ===")
        output.append(f"Target: {result['target']}")
        output.append(f"Interface: {result['interface']['name']} (MTU: {result['interface']['mtu']})")
        
        # Path MTU results
        path_mtu = result.get('path_mtu', {})
        if path_mtu.get('success'):
            output.append(f"\nPath MTU: {path_mtu['max_mtu']}")
        else:
            output.append(f"\nPath MTU: Failed - {path_mtu.get('error', 'Unknown error')}")
        
        # Common sizes test results
        common_test = result.get('common_sizes_test', {})
        if common_test.get('success'):
            output.append("\n--- Common MTU Sizes Test ---")
            for test_result in common_test.get('results', []):
                status = "✓" if test_result['success'] else "✗"
                output.append(f"{status} {test_result['mtu_size']}: {test_result['reason']}")
        
        # Jumbo frames test
        jumbo_test = result.get('jumbo_frames_test')
        if jumbo_test:
            output.append("\n--- Jumbo Frames Test ---")
            if jumbo_test.get('jumbo_supported'):
                output.append(f"✓ Jumbo frames supported (max: {jumbo_test.get('max_jumbo_mtu')})")
            else:
                output.append("✗ Jumbo frames not supported")
        
        return '\n'.join(output)
    
    def format_analysis_results(self, recommendations: List[MTURecommendation], 
                              summary: Dict[str, Any]) -> str:
        if self.format_type == 'json':
            return json.dumps({
                'summary': summary,
                'recommendations': [
                    {
                        'issue': rec.issue,
                        'severity': rec.severity,
                        'description': rec.description,
                        'recommendation': rec.recommendation,
                        'optimal_mtu': rec.optimal_mtu
                    }
                    for rec in recommendations
                ]
            }, indent=2)
        
        output = []
        output.append("=== MTU Analysis Results ===")
        
        # Summary
        status_icon = {
            'optimal': '✓',
            'issues_found': '⚠',
            'minor_issues': 'ⓘ'
        }.get(summary['status'], '?')
        
        output.append(f"\nStatus: {status_icon} {summary['message']}")
        
        if not recommendations:
            output.append("\nNo issues found. Your MTU configuration appears to be optimal.")
            return '\n'.join(output)
        
        # Group recommendations by severity
        high_priority = [r for r in recommendations if r.severity == 'high']
        medium_priority = [r for r in recommendations if r.severity == 'medium']
        low_priority = [r for r in recommendations if r.severity == 'low']
        
        for priority_group, title, icon in [
            (high_priority, "Critical Issues", "🔴"),
            (medium_priority, "Important Issues", "🟡"),
            (low_priority, "Optimization Opportunities", "🔵")
        ]:
            if priority_group:
                output.append(f"\n--- {title} {icon} ---")
                for rec in priority_group:
                    output.append(f"\nIssue: {rec.description}")
                    output.append(f"Recommendation: {rec.recommendation}")
                    if rec.optimal_mtu:
                        output.append(f"Suggested MTU: {rec.optimal_mtu}")
        
        return '\n'.join(output)
    
    def format_interfaces_list(self, result: Dict[str, Any]) -> str:
        if not result.get('success'):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        if self.format_type == 'json':
            return json.dumps(result, indent=2)
        
        output = []
        output.append("=== Network Interfaces ===")
        
        for interface in result.get('interfaces', []):
            status = "UP" if interface['is_up'] else "DOWN"
            output.append(f"\n{interface['name']} ({interface['type']})")
            output.append(f"  MTU: {interface['mtu']}")
            output.append(f"  Status: {status}")
            if interface['addresses']:
                output.append(f"  Addresses: {', '.join(interface['addresses'][:2])}")
                if len(interface['addresses']) > 2:
                    output.append(f"    ... and {len(interface['addresses']) - 2} more")
        
        return '\n'.join(output)