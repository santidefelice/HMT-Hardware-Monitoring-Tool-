# Installation and Configuration Guide – Hardware Monitoring Tool

This guide provides step‑by‑step instructions for installing and running the
Hardware Monitoring Tool on a typical development machine.

## 1. Prerequisites

- Python 3.8 or later (tested with Python 3.13 via Homebrew on macOS).
- Internet access to install Python packages (if they are not already cached).

## 2. Obtain the Code

1. Clone or copy the `HMT-Hardware-Monitoring-Tool-` folder onto your machine.
2. Open a terminal and change into the project root:

   ```bash
   cd /path/to/HMT-Hardware-Monitoring-Tool-
   ```

## 3. Create a Virtual Environment (Recommended)

To avoid conflicts with system Python packages, it is recommended to use a
virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

- On macOS / Linux:

  ```bash
  source .venv/bin/activate
  ```

- On Windows (PowerShell):

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

## 4. Install Dependencies

With the virtual environment active, install the required packages:

```bash
python -m pip install psutil GPUtil
```

Notes:

- `psutil` is mandatory; the application will not start without it.
- `GPUtil` is optional and only used when NVIDIA GPUs are present
  (Windows / Linux).

## 5. Run the Application

From the project root:

```bash
cd Code/Source
python index.py
```

If everything is configured correctly, a Tkinter window titled
**"Hardware Monitoring Tool"** will appear.

## 6. Configuration by Environment

### macOS

- Ensure you have Python 3 installed (e.g., via Homebrew).
- Prefer a virtualenv to avoid PEP‑668 “externally managed environment” issues.
- GPU tab will show static GPU information (name, VRAM, Metal support) via
  `system_profiler`; real‑time GPU metrics are not exposed by this tool.

### Windows

- Install Python 3 (from `python.org` or the Microsoft Store).
- Optionally install `wmi` for richer CPU name detection:

  ```bash
  python -m pip install wmi
  ```

- For NVIDIA GPU monitoring, ensure:
  - NVIDIA drivers are installed.
  - `nvidia-smi` is available in your PATH.

### Linux

- Install `lm-sensors` (or equivalent) if you want CPU temperature readings:

  ```bash
  sudo apt install lm-sensors
  sudo sensors-detect
  ```

- Ensure your user has permission to read hardware sensors and disk statistics.

## 7. Screenshots

For a formal submission, you can augment this document with screenshots
showing:

- Terminal commands used to create/activate the virtualenv and install
  dependencies.
- The application window with each tab (CPU, Memory, GPU, Storage, Settings).

Screenshots can be stored in a separate `Documents/Screenshots/` subfolder
or embedded into this document if your submission format allows it.


