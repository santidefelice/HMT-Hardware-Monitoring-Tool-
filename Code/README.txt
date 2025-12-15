Code Directory Overview
=======================

This `Code` directory contains everything needed to build, run, and deploy the
Hardware Monitoring Tool application. It includes:

- All Python source code
- The desktop application entry point
- A description of any deployable artifacts
- A high‑level installation guide
- A short user manual


Directory Structure
-------------------

From the project root you should see:

    HMT-Hardware-Monitoring-Tool-/
    ├── Code/
    │   ├── README.txt        # This file: code structure, install guide, user guide
    │   └── Source/
    │       └── index.py      # Main Tkinter application (CPU/RAM/GPU/Storage monitor)
    ├── Documents/            # Project documentation, minutes, manuals, etc.
    ├── Posters/              # Final poster(s) for the project
    ├── Presentation Slides/  # Final presentation deck
    └── Videos/               # index.html linking to YouTube videos

For this project there is:

- **No WebSite subdirectory** (this is a desktop GUI app, not a web app).
- **No Database subdirectory** (the app does not use a database).


Installation Guide (Step‑by‑Step)
---------------------------------

The application is a Python Tkinter desktop program. The safest way to install
dependencies is to use a virtual environment so you do not modify your system
Python.

1. Open a terminal and go to the project root:

       cd /path/to/HMT-Hardware-Monitoring-Tool-

2. Create a virtual environment (only once):

       python3 -m venv .venv

3. Activate the virtual environment:

   - On macOS / Linux:

         source .venv/bin/activate

   - On Windows (PowerShell):

         .venv\Scripts\Activate.ps1

4. Install the required Python packages into the virtualenv:

       python -m pip install psutil GPUtil

   Notes:
   - `psutil` is required; the app will not start without it.
   - `GPUtil` is optional and only used when NVIDIA GPUs are present
     (primarily on Windows / Linux).

5. Run the application from the `Code/Source` directory:

       cd Code/Source
       python index.py

   A Tkinter window titled **"Hardware Monitoring Tool"** should open with
   the following tabs: **CPU**, **Memory**, **GPU**, **Storage**, **Settings**.

6. When finished, you can deactivate the virtual environment with:

       deactivate

If you cannot or do not want to use a virtual environment, you can install the
dependencies directly into your system Python with:

    python3 -m pip install psutil GPUtil

but this is not recommended on PEP‑668 “externally managed” environments
(e.g. Homebrew Python on macOS).


User Manual (Brief)
-------------------

1. **Launching the app**

   - Follow the Installation Guide above.
   - From `Code/Source`, run:

         python index.py

   - The main window appears with a tabbed interface.

2. **CPU tab**

   - Shows:
     - Overall CPU usage (%)
     - Per‑core utilization with progress bars
     - Current clock frequency
     - CPU name, physical cores, logical processors
     - CPU temperature (Linux only, where sensors are available)
   - Includes a small history graph of recent CPU usage.

3. **Memory tab**

   - Shows:
     - Total, used, and available RAM (GB)
     - RAM usage percentage
     - Swap total, used, and usage percentage
   - Includes a small history graph of recent RAM usage.

4. **GPU tab**

   - On **Windows / Linux with NVIDIA GPUs and GPUtil installed**:
     - GPU name
     - GPU load (%)
     - GPU memory usage (% and used/total GB)
     - Temperature (°C) and power draw where supported
   - On **macOS**:
     - Static GPU information from `system_profiler`:
       - GPU name, vendor, VRAM, Metal support
     - Real‑time usage/temperature is not shown (not exposed by the APIs used).

5. **Storage tab**

   - Lists each mounted partition with:
     - File system type
     - Total, used, free space (GB)
     - Usage percentage
   - Shows approximate global disk read/write speeds in MB/s.

6. **Settings tab**

   - Allows you to change the **refresh interval (milliseconds)** for all
     metrics (250–5000 ms).  Lower intervals give smoother updates but use
     more CPU.


Deployable Code
---------------

For this project the **deployable artifact** is simply the Python application
itself:

- `Code/Source/index.py`

To deploy on another machine:

1. Copy the entire `HMT-Hardware-Monitoring-Tool-` directory.
2. Create a virtualenv on the target machine.
3. Install `psutil` and, optionally, `GPUtil` into that environment.
4. Run `python Code/Source/index.py`.


