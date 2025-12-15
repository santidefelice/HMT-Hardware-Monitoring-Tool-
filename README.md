# Hardware Monitor

A real-time desktop application for monitoring system hardware performance including CPU, RAM, GPU, and storage metrics.

## Features

- **CPU Monitoring**

  - Overall CPU usage percentage
  - Per-core utilization with progress bars
  - Current clock frequency
  - Core/thread counts
  - CPU name detection per OS
  - Core/package temperature (Linux via `psutil.sensors_temperatures`, where available)

- **Memory (RAM) Monitoring**

  - Usage percentage
  - Total / used / available memory (in GB)
  - Swap total / used / usage percentage
  - Simple historical RAM usage graph

- **GPU Monitoring**

  - **Windows / Linux (NVIDIA + GPUtil):**
    - GPU load percentage
    - GPU memory utilization and used / total memory
    - Temperature (via NVIDIA / `nvidia-smi` / GPUtil)
    - Power draw and power limit (where exposed)
  - **macOS:**
    - Static GPU information via `system_profiler`:
      - GPU name
      - Vendor
      - VRAM / shared VRAM
      - Metal support string
    - (macOS currently does **not** provide real-time GPU usage/temperature in this app)

- **Storage Monitoring**

  - Disk usage by partition (total / used / free / percentage)
  - Global read/write speeds (MB/s) computed from disk I/O counters

- **Real-time Updates**
  - Live metrics refresh on all tabs
  - Simple historical graphs for CPU and RAM usage
  - Customizable refresh interval (per-app, via the **Settings** tab)

## Screenshots

_Coming soon - screenshots will be added once the UI is implemented_

## Installation

### Prerequisites

- **Python**: 3.8 or higher (tested with 3.13 via Homebrew on macOS)
- **pip** package manager

### Dependencies

- **Core Python packages (installed via pip in a virtual environment):**

  - `psutil` – System and process utilities (CPU, RAM, disks, I/O, sensors)
  - `GPUtil` – Optional GPU monitoring for NVIDIA GPUs (Windows/Linux)

- **Standard library / built‑in modules (no install required):**

  - `tkinter` – GUI framework (bundled with most Python distributions)
  - `platform`, `subprocess`, `time`, `collections`, `json`, etc.

- **Windows-specific (optional):**
  - `wmi` – For richer CPU name detection (fallbacks exist if not installed)

### Recommended: Virtual environment (especially on macOS / Homebrew)

From the project root (`HMT-Hardware-Monitoring-Tool-`):

```bash
cd /Users/youruser/Desktop/HMT/HMT-Hardware-Monitoring-Tool-

# 1) Create a virtual environment (once)
python3 -m venv .venv

# 2) Activate it
source .venv/bin/activate

# 3) Install Python dependencies INSIDE the venv
python -m pip install psutil GPUtil
```

After activation, the `python` command will refer to the virtualenv interpreter, and the app will be able to import `psutil` and (optionally) `GPUtil` without conflicting with system packages.

### Quick Start

1. **Clone or open the project** (example path):

```bash
cd /Users/youruser/Desktop/HMT/HMT-Hardware-Monitoring-Tool-
```

2. **(Optional but recommended)**: Create and activate a virtualenv, then install dependencies as shown above.

3. **Run the application** from the `Code/Source` directory:

```bash
cd Code/Source
python index.py
```

If you are _not_ using a virtualenv and are comfortable modifying your system Python packages, you can instead run:

```bash
python3 -m pip install psutil GPUtil
cd Code/Source
python3 index.py
```

> On recent Homebrew Pythons (PEP 668 “externally managed”), using a virtualenv is the safest way to install `psutil` and other libraries.

## Usage

### Basic Operation

1. Launch the application by running `python index.py` from `Code/Source` (preferably inside a virtualenv).
2. The main window opens with a tabbed interface (`CPU`, `Memory`, `GPU`, `Storage`, `Settings`).
3. Metrics automatically refresh at the configured interval (default: 1000 ms).
4. Use the tabs to switch between different hardware components.

### Configuration (via Settings tab)

- **Refresh Interval (ms)**:  
  Adjust the global update frequency for all metrics (250–5000 ms).  
  Lower values update more smoothly but increase CPU usage.

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

### Project Structure (current)

```
HMT-Hardware-Monitoring-Tool-/
├── Code/
│   ├── README.txt         # Code structure, install guide, brief user manual
│   └── Source/
│       └── index.py       # Application entry point (Tkinter UI and monitoring logic)
├── Documents/
│   ├── Project_Documentation.md
│   ├── Daily_Scrum_Meeting_Minutes.md
│   ├── User_Manual.md
│   ├── Installation_Guide.md
│   └── Shortcomings_Wishlist.md
├── Posters/
│   └── README.txt         # Place final poster files here
├── Presentation Slides/
│   └── README.txt         # Place final slide deck here
├── Videos/
│   └── index.html         # Links to the four required YouTube videos
└── README.md              # This file
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
