# Hardware Monitor

A real-time desktop application for monitoring system hardware performance including CPU, RAM, GPU, and storage metrics.

## Features

- **CPU Monitoring**
  - Usage percentage
  - Clock speeds (current/base/boost)
  - Core temperatures
  - Per-core utilization

- **Memory (RAM) Monitoring**
  - Usage percentage and absolute values
  - Available/used memory
  - Memory speed and timings
  - Swap usage

- **GPU Monitoring**
  - Temperature monitoring
  - Usage percentage
  - Memory utilization
  - Clock speeds (core/memory)
  - Power consumption

- **Storage Monitoring**
  - Disk usage by drive
  - Read/write speeds
  - Available space
  - Health status

- **Real-time Updates**
  - Live metrics refresh
  - Historical graphs
  - Customizable refresh intervals

## Screenshots

*Coming soon - screenshots will be added once the UI is implemented*

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `psutil` - System and process utilities
- `GPUtil` - GPU monitoring (NVIDIA)
- `tkinter` - GUI framework (usually included with Python)
- `matplotlib` - For graphs and charts
- `threading` - For background metric collection

**Windows-specific:**
- `wmi` - Windows Management Instrumentation
- `pywin32` - Windows API access

**Linux-specific:**
- `sensors` - Hardware sensor readings

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hardware-monitor.git
cd hardware-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### Basic Operation

1. Launch the application by running `python main.py`
2. The main window will display real-time hardware metrics
3. Metrics automatically refresh every second (configurable)
4. Use the tabs to switch between different hardware components

### Configuration

- **Refresh Rate**: Adjust update frequency in settings (0.5-5 seconds)
- **Temperature Units**: Toggle between Celsius and Fahrenheit
- **Graph History**: Set how long to retain historical data
- **Alerts**: Configure temperature and usage thresholds

## System Requirements

### Minimum Requirements
- Operating System: Windows 10, macOS 10.14, or Linux
- RAM: 100 MB available memory
- Python: 3.8+
- Disk Space: 50 MB

### Supported Hardware
- **CPUs**: Intel, AMD (any modern processor)
- **GPUs**: NVIDIA (GTX 900 series+), AMD (limited support)
- **RAM**: Any DDR3/DDR4/DDR5 memory
- **Storage**: HDDs, SSDs, NVMe drives

## Development

### Project Structure
```
hardware-monitor/
├── main.py              # Application entry point
├── src/
│   ├── gui/             # GUI components
│   ├── monitors/        # Hardware monitoring modules
│   ├── utils/           # Utility functions
│   └── config/          # Configuration management
├── assets/              # Icons and images
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Features

1. Create a new monitor class in `src/monitors/`
2. Implement the required interface methods
3. Add GUI components in `src/gui/`
4. Update the main application loop

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-monitor`)
3. Commit your changes (`git commit -am 'Add new hardware monitor'`)
4. Push to the branch (`git push origin feature/new-monitor`)
5. Create a Pull Request

### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add docstrings to all functions and classes
- Include unit tests for new features

## Troubleshooting

### Common Issues

**GPU monitoring not working:**
- Ensure you have NVIDIA drivers installed
- Run the application as administrator (Windows)
- Check that your GPU is supported

**Temperature readings unavailable:**
- Install `lm-sensors` on Linux
- Enable WMI service on Windows
- Some laptops may require additional drivers

**High CPU usage:**
- Increase refresh interval in settings
- Disable unused monitoring features
- Check for background processes

**Permission errors:**
- Run as administrator on Windows
- Use `sudo` on Linux for hardware access
- Check file permissions in installation directory

### Performance Tips

- Increase refresh interval to reduce CPU usage
- Disable graphs if not needed
- Close other monitoring tools to avoid conflicts
- Use lightweight theme for better performance

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **psutil** - Cross-platform system monitoring
- **GPUtil** - Simple GPU monitoring library
- **OpenHardwareMonitor** - Inspiration for hardware access methods
- Community contributors and testers

## Changelog

### Version 1.0.0 (Planned)
- Initial release
- Basic CPU, RAM, GPU, storage monitoring
- Real-time graphs and metrics
- Cross-platform support

## Roadmap

- [ ] Network interface monitoring
- [ ] Fan speed control
- [ ] System alerts and notifications
- [ ] Export data to CSV/JSON
- [ ] Dark/light theme support
- [ ] Tray icon with quick stats
- [ ] Multiple GPU support
- [ ] AMD GPU support improvement
- [ ] Web interface option
- [ ] Mobile companion app

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hardware-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hardware-monitor/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/hardware-monitor/wiki)

---

**Made with ❤️ for system monitoring enthusiasts**