# User Manual (Detailed) – Hardware Monitoring Tool

This document is a more detailed user manual complementing the brief guide
in `Code/README.txt`.

## Launching the Application

1. Ensure Python and the required dependencies are installed as described
   in `Code/README.txt`.
2. From the project root, activate your virtual environment (if used).
3. Change into the source directory and run:

   ```bash
   cd Code/Source
   python index.py
   ```

4. The main window of the Hardware Monitoring Tool should appear.

## Main Window

- The window title is **"Hardware Monitoring Tool"**.
- A tabbed interface is provided via tabs:
  - `CPU`
  - `Memory`
  - `GPU`
  - `Storage`
  - `Settings`

You can click each tab to switch between different hardware views.

## CPU Tab

- Shows:
  - Overall CPU usage as a percentage.
  - Per‑core utilization with progress bars and labels.
  - Current CPU frequency.
  - CPU name, physical core count, logical processor count.
  - CPU temperature on Linux when supported by `psutil.sensors_temperatures`.
- Includes a simple history graph of recent CPU usage.

## Memory Tab

- Shows:
  - Total RAM, used RAM, available RAM (GB).
  - Current RAM usage percentage.
  - Swap total, used, and usage percentage.
- Includes a simple history graph of recent RAM usage.

## GPU Tab

- On Windows / Linux with NVIDIA GPUs and `GPUtil`:
  - GPU name.
  - GPU load percentage.
  - Memory utilization percentage and used/total memory in GB.
  - GPU temperature (where available).
  - Power draw and power limit (where available).
- On macOS:
  - Static GPU information from `system_profiler`:
    - GPU name, vendor, VRAM / shared VRAM, Metal support.
  - Real‑time usage/temperature is not shown.

## Storage Tab

- Shows each detected partition with:
  - Mount point and file system.
  - Total, used, and free space in GB.
  - Usage percentage.
- Shows approximate global disk read and write speeds (MB/s).

## Settings Tab

- Allows you to configure the **refresh interval** (in milliseconds).
- Valid values: 250–5000 ms.
  - Lower values provide smoother updates but use more CPU.
  - Higher values reduce overhead but update less frequently.

## Exiting the Application

- Close the window using the standard window controls, or
- Use the keyboard shortcut for closing windows on your OS
  (e.g., `Cmd+Q` on macOS, `Alt+F4` on Windows).


