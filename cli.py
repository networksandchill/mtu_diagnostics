#!/usr/bin/env python3
import click
from mtu_diagnostics.core.detector import MTUDetector
from mtu_diagnostics.diagnostics.analyzer import DiagnosticAnalyzer
from mtu_diagnostics.diagnostics.reporter import MTUReporter

@click.group()
@click.version_option(version="0.1.0")
def main():
    """MTU Diagnostics Tool - Detect and diagnose network MTU issues."""
    pass

@main.command()
@click.option('--interface', '-i', help='Specific network interface to check')
@click.option('--format', '-f', default='text', type=click.Choice(['text', 'json']), 
              help='Output format')
def detect(interface, format):
    """Detect MTU size for network interface."""
    detector = MTUDetector()
    reporter = MTUReporter(format)
    
    result = detector.detect_interface_mtu(interface)
    click.echo(reporter.format_interface_info(result))

@main.command()
@click.argument('target')
@click.option('--interface', '-i', help='Specific network interface to use')
@click.option('--format', '-f', default='text', type=click.Choice(['text', 'json']), 
              help='Output format')
def test(target, interface, format):
    """Test MTU size to a specific target."""
    detector = MTUDetector()
    reporter = MTUReporter(format)
    
    result = detector.detect_path_mtu(target, interface)
    click.echo(reporter.format_path_mtu_result(result))

@main.command()
@click.argument('target')
@click.option('--interface', '-i', help='Specific network interface to use')
@click.option('--format', '-f', default='text', type=click.Choice(['text', 'json']), 
              help='Output format')
def analyze(target, interface, format):
    """Perform comprehensive MTU analysis with recommendations."""
    detector = MTUDetector()
    analyzer = DiagnosticAnalyzer()
    reporter = MTUReporter(format)
    
    click.echo("Running comprehensive MTU analysis...")
    
    result = detector.comprehensive_mtu_test(target, interface)
    
    if result.get('success'):
        recommendations = analyzer.analyze_mtu_results(result)
        summary = analyzer.generate_summary(recommendations)
        
        # Show test results
        click.echo(reporter.format_comprehensive_test(result))
        click.echo()
        
        # Show analysis
        click.echo(reporter.format_analysis_results(recommendations, summary))
    else:
        click.echo(f"Error: {result.get('error', 'Unknown error')}")

@main.command()
@click.option('--format', '-f', default='text', type=click.Choice(['text', 'json']), 
              help='Output format')
def interfaces(format):
    """List all network interfaces and their MTU settings."""
    detector = MTUDetector()
    reporter = MTUReporter(format)
    
    result = detector.get_all_interfaces_info()
    click.echo(reporter.format_interfaces_list(result))

@main.command()
@click.argument('target')
@click.option('--interface', '-i', help='Specific network interface to use')
@click.option('--timeout', '-t', default=5, help='Ping timeout in seconds')
def trace(target, interface, timeout):
    """Trace path MTU discovery (basic implementation)."""
    from mtu_diagnostics.core.tester import MTUTester
    from mtu_diagnostics.utils.network import resolve_hostname
    
    tester = MTUTester()
    
    click.echo(f"Tracing path MTU to {target}...")
    
    ip = resolve_hostname(target)
    if not ip:
        click.echo(f"Error: Could not resolve {target}")
        return
    
    click.echo(f"Target IP: {ip}")
    
    # Test common MTU sizes
    result = tester.test_common_sizes(target, timeout)
    
    if result['success']:
        click.echo("\nMTU Size Test Results:")
        for test in result['results']:
            status = "✓" if test['success'] else "✗"
            click.echo(f"{status} {test['mtu_size']}: {test['reason']}")
        
        # Find optimal MTU
        mtu_result = tester.find_max_mtu(target)
        if mtu_result['success']:
            click.echo(f"\nOptimal MTU: {mtu_result['max_mtu']}")
    else:
        click.echo(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    main()