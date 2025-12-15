# Shortcomings and Wishlist – Hardware Monitoring Tool

## Current Shortcomings

- GPU monitoring on macOS is limited to static information from
  `system_profiler` (no real-time usage or temperatures).
- CPU temperature monitoring is currently implemented only for Linux where
  `psutil.sensors_temperatures` exposes the required sensors.
- There is no network interface monitoring.
- No built-in alerting (e.g., notifications when thresholds are exceeded).
- No built-in export of metrics to CSV/JSON.

## Wishlist / Future Enhancements

- Add cross-platform GPU monitoring for AMD and Apple Silicon GPUs.
- Add a network monitoring tab (throughput per interface, error counts, etc.).
- Implement configurable alerts and notifications for:
  - High CPU/GPU usage
  - High temperatures
  - Low disk space
- Provide an option to export metrics history to CSV/JSON.
- Add dark/light theme support for the UI.
- Add system tray icon integration for quick stats.


