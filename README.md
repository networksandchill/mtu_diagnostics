# MTU Diagnostics Tool

A Python command-line tool for detecting and diagnosing Maximum Transmission Unit (MTU) size issues on network interfaces and paths.

## Features

- **Interface MTU Detection**: Check MTU settings for network interfaces
- **Path MTU Discovery**: Test maximum working MTU to specific destinations  
- **Comprehensive Analysis**: Identify common MTU issues and provide recommendations
- **Cross-platform Support**: Works on Linux, macOS, and Windows
- **Multiple Output Formats**: Text and JSON output options

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mtu-diagnostics.git
cd mtu-diagnostics

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

### Basic Commands

```bash
# Check MTU of default interface
mtu-diag detect

# Check specific interface
mtu-diag detect -i eth0

# Test MTU to a target
mtu-diag test google.com

# Comprehensive analysis with recommendations
mtu-diag analyze google.com

# List all network interfaces
mtu-diag interfaces

# Trace path MTU discovery
mtu-diag trace google.com
```

### Output Formats

Use `--format json` for machine-readable output:

```bash
mtu-diag detect --format json
mtu-diag analyze google.com --format json
```

## Common MTU Issues Detected

- **PPPoE Overhead**: Standard 1500 MTU reduced to 1492 for PPPoE connections
- **VPN Tunneling**: Additional headers reducing effective MTU
- **Jumbo Frame Mismatches**: Interface supports jumbo frames but path doesn't
- **Fragmentation**: Packets being fragmented due to MTU mismatches
- **Suboptimal Settings**: MTU smaller than optimal for the network path

## Examples

### Basic Interface Check
```bash
$ mtu-diag detect
=== Interface Information ===
Name: en0
MTU: 1500
Status: Up  
Type: ethernet
Addresses:
  - 192.168.1.100
  - fe80::1234:5678:9abc:def0
```

### Path MTU Test
```bash
$ mtu-diag test google.com
=== Path MTU Detection ===
Target: google.com
Target IP: 142.250.191.14
Interface: en0
Interface MTU: 1500
Path MTU: 1500
MTU Optimal: Yes
```

### Comprehensive Analysis
```bash
$ mtu-diag analyze google.com
Running comprehensive MTU analysis...

=== Comprehensive MTU Test ===
Target: google.com
Interface: en0 (MTU: 1500)

Path MTU: 1500

--- Common MTU Sizes Test ---
✓ 1500: ok
✓ 1492: ok
✓ 1480: ok
...

=== MTU Analysis Results ===

Status: ✓ No MTU issues detected
No issues found. Your MTU configuration appears to be optimal.
```

## Requirements

- Python 3.7+
- psutil>=5.8.0
- click>=8.0.0

## Platform Support

- **Linux**: Uses `ping` with `-M do` for don't fragment
- **macOS**: Uses `ping` with `-D` for don't fragment  
- **Windows**: Uses `ping` with `-f` for don't fragment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.