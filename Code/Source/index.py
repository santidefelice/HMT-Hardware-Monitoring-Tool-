import json
import platform
import subprocess
import time
from collections import deque

try:
    import psutil  # type: ignore[import]
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency 'psutil'. Install it with 'pip install psutil' and rerun."
    ) from exc

import tkinter as tk
from tkinter import ttk

try:
    import GPUtil  # type: ignore[import]
except Exception:
    GPUtil = None  # GPU monitoring will be disabled if GPUtil is unavailable


REFRESH_INTERVAL_MS = 1000  # default refresh interval in milliseconds
HISTORY_LENGTH = 60  # samples to keep for simple historical graphs


class HistoryGraph(ttk.Frame):
    """
    Lightweight line graph for displaying recent percentage history (0–100).
    Uses a Tkinter Canvas and a fixed-size deque of samples.
    """

    def __init__(self, parent, title: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
        self.canvas_width = 400
        self.canvas_height = 100
        self.history = deque(maxlen=HISTORY_LENGTH)

        ttk.Label(self, text=title, font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            background="#1e1e1e",
            highlightthickness=0,
        )
        self.canvas.pack(fill="x", expand=True, pady=(2, 0))

        # Pre-fill with zeros so the graph looks consistent from start
        for _ in range(HISTORY_LENGTH):
            self.history.append(0.0)
        self.draw()

    def add_sample(self, value: float) -> None:
        """Add a new percentage sample (0–100) and redraw the graph."""
        value = max(0.0, min(100.0, float(value)))
        self.history.append(value)
        self.draw()

    def draw(self) -> None:
        self.canvas.delete("all")

        if len(self.history) < 2:
            return

        # Draw background grid lines (25%, 50%, 75%)
        for frac, color in [(0.25, "#333333"), (0.5, "#444444"), (0.75, "#333333")]:
            y = self.canvas_height * (1 - frac)
            self.canvas.create_line(
                0, y, self.canvas_width, y, fill=color, dash=(2, 4)
            )

        step_x = self.canvas_width / (len(self.history) - 1)
        points = []
        for i, value in enumerate(self.history):
            x = i * step_x
            y = self.canvas_height * (1 - value / 100.0)
            points.extend([x, y])

        if len(points) >= 4:
            self.canvas.create_line(
                *points, fill="#00ff7f", width=2, smooth=True
            )


class CPUPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="10")

        self.cpu_usage = tk.StringVar(value="0%")
        self.cpu_frequency = tk.StringVar(value="0 MHz")
        self.cpu_temp = tk.StringVar(value="N/A")
        self.cpu_cores = tk.StringVar(value="0")
        self.cpu_threads = tk.StringVar(value="0")
        self.cpu_name = tk.StringVar(value="Unknown")

        self.core_usages = []
        self.core_bars = []
        self.core_labels = []

        self.cpu_history_graph = HistoryGraph(self, "CPU Usage History")

        self._build_ui()
        self._populate_static_info()

    # ---------------- CPU UI ---------------- #
    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)

        title_label = ttk.Label(
            self, text="CPU Information", font=("Helvetica", 16)
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # CPU Name
        ttk.Label(
            self, text="Processor:", font=("Helvetica", 12, "bold")
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.cpu_name, wraplength=300).grid(
            row=1, column=1, sticky=tk.W
        )

        # CPU cores & threads
        ttk.Label(
            self, text="Physical Cores:", font=("Helvetica", 12, "bold")
        ).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.cpu_cores).grid(
            row=2, column=1, sticky=tk.W
        )

        ttk.Label(
            self, text="Logical Processors:", font=("Helvetica", 12, "bold")
        ).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.cpu_threads).grid(
            row=3, column=1, sticky=tk.W
        )

        ttk.Separator(self, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )

        ttk.Label(
            self, text="Real-time Metrics", font=("Helvetica", 16)
        ).grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # Overall CPU usage
        ttk.Label(
            self, text="Overall CPU Usage:", font=("Helvetica", 12, "bold")
        ).grid(row=6, column=0, sticky=tk.W, padx=(0, 10))
        usage_label = ttk.Label(
            self, textvariable=self.cpu_usage, font=("Helvetica", 12), foreground="blue"
        )
        usage_label.grid(row=6, column=1, sticky=tk.W)

        # CPU Frequency
        ttk.Label(
            self, text="Current Frequency:", font=("Helvetica", 12, "bold")
        ).grid(row=7, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.cpu_frequency, font=("Helvetica", 12)).grid(
            row=7, column=1, sticky=tk.W
        )

        # CPU Temperature
        ttk.Label(
            self, text="Temperature:", font=("Helvetica", 12, "bold")
        ).grid(row=8, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.cpu_temp, font=("Helvetica", 12)).grid(
            row=8, column=1, sticky=tk.W
        )

        # Per-core usage
        self.core_frame = ttk.LabelFrame(self, text="Per-Core Usage", padding="10")
        self.core_frame.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(20, 0),
        )

        self._create_core_widgets()

        # History graph
        self.cpu_history_graph.grid(
            row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0)
        )

        for i in range(11):
            self.rowconfigure(i, weight=1 if i == 9 else 0)

    def _create_core_widgets(self) -> None:
        cpu_count = psutil.cpu_count(logical=True) or 1

        cols = min(4, cpu_count)
        self.core_usages = []
        self.core_bars = []
        self.core_labels = []

        for i in range(cpu_count):
            row = (i // cols) * 2
            col = i % cols

            core_var = tk.StringVar(value="0%")
            self.core_usages.append(core_var)

            label = ttk.Label(self.core_frame, text=f"Core {i}:", font=("Helvetica", 9))
            label.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            self.core_labels.append(label)

            progress = ttk.Progressbar(
                self.core_frame, length=100, mode="determinate", maximum=100
            )
            progress.grid(
                row=row + 1, column=col, padx=5, pady=2, sticky=(tk.W, tk.E)
            )
            self.core_bars.append(progress)

            self.core_frame.columnconfigure(col, weight=1)

    # ---------------- CPU Data ---------------- #
    def _populate_static_info(self) -> None:
        try:
            system = platform.system()
            if system == "Windows":
                try:
                    import wmi  # type: ignore

                    c = wmi.WMI()
                    for processor in c.Win32_Processor():
                        self.cpu_name.set(processor.Name.strip())
                        break
                except Exception:
                    self.cpu_name.set(platform.processor() or "Unknown")
            elif system == "Darwin":
                try:
                    cpu_name = (
                        subprocess.check_output(
                            ["sysctl", "-n", "machdep.cpu.brand_string"]
                        )
                        .strip()
                        .decode()
                    )
                    self.cpu_name.set(cpu_name)
                except Exception:
                    self.cpu_name.set(platform.processor() or "Unknown")
            else:
                self.cpu_name.set(platform.processor() or "Unknown")
        except Exception:
            self.cpu_name.set("Unable to detect processor")

        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)

        self.cpu_cores.set(str(physical_cores) if physical_cores else "N/A")
        self.cpu_threads.set(str(logical_cores) if logical_cores else "N/A")

    def _get_cpu_temperature(self) -> str:
        try:
            if platform.system() == "Linux":
                temps = psutil.sensors_temperatures()
                for key in ("coretemp", "k10temp"):
                    if key in temps:
                        for temp in temps[key]:
                            if (
                                "Package" in temp.label
                                or "Core" in temp.label
                                or temp.label == ""
                            ):
                                return f"{temp.current:.1f} °C"
        except Exception:
            pass
        return "N/A"

    def update_metrics(self) -> None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_usage.set(f"{cpu_percent:.1f}%")
            self.cpu_history_graph.add_sample(cpu_percent)

            core_percents = psutil.cpu_percent(percpu=True, interval=None)
            for i, (percent, var, bar) in enumerate(
                zip(core_percents, self.core_usages, self.core_bars)
            ):
                var.set(f"{percent:.1f}%")
                bar["value"] = percent
                self.core_labels[i].config(text=f"Core {i}: {percent:.1f}%")

            freq = psutil.cpu_freq()
            if freq:
                self.cpu_frequency.set(f"{freq.current:.1f} MHz")
            else:
                self.cpu_frequency.set("N/A")

            self.cpu_temp.set(self._get_cpu_temperature())
        except Exception as exc:
            print(f"Error updating CPU metrics: {exc}")


class MemoryPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="10")

        self.total_mem = tk.StringVar(value="0 GB")
        self.used_mem = tk.StringVar(value="0 GB")
        self.available_mem = tk.StringVar(value="0 GB")
        self.mem_percent = tk.StringVar(value="0%")

        self.swap_total = tk.StringVar(value="0 GB")
        self.swap_used = tk.StringVar(value="0 GB")
        self.swap_percent = tk.StringVar(value="0%")

        self.mem_history_graph = HistoryGraph(self, "RAM Usage History")

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Memory (RAM) Information", font=("Helvetica", 16)).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        # RAM stats
        ttk.Label(
            self, text="Total Memory:", font=("Helvetica", 12, "bold")
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.total_mem).grid(
            row=1, column=1, sticky=tk.W
        )

        ttk.Label(
            self, text="Used Memory:", font=("Helvetica", 12, "bold")
        ).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.used_mem).grid(
            row=2, column=1, sticky=tk.W
        )

        ttk.Label(
            self, text="Available Memory:", font=("Helvetica", 12, "bold")
        ).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.available_mem).grid(
            row=3, column=1, sticky=tk.W
        )

        ttk.Label(
            self, text="Memory Usage:", font=("Helvetica", 12, "bold")
        ).grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.mem_percent).grid(
            row=4, column=1, sticky=tk.W
        )

        ttk.Separator(self, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )

        # Swap stats
        ttk.Label(self, text="Swap", font=("Helvetica", 14)).grid(
            row=6, column=0, columnspan=2, pady=(0, 10)
        )

        ttk.Label(
            self, text="Total Swap:", font=("Helvetica", 12, "bold")
        ).grid(row=7, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.swap_total).grid(
            row=7, column=1, sticky=tk.W
        )

        ttk.Label(
            self, text="Used Swap:", font=("Helvetica", 12, "bold")
        ).grid(row=8, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.swap_used).grid(
            row=8, column=1, sticky=tk.W
        )

        ttk.Label(
            self, text="Swap Usage:", font=("Helvetica", 12, "bold")
        ).grid(row=9, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(self, textvariable=self.swap_percent).grid(
            row=9, column=1, sticky=tk.W
        )

        # History graph
        self.mem_history_graph.grid(
            row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0)
        )

    @staticmethod
    def _to_gb(value_bytes: float) -> float:
        return value_bytes / (1024**3)

    def update_metrics(self) -> None:
        try:
            vm = psutil.virtual_memory()
            self.total_mem.set(f"{self._to_gb(vm.total):.2f} GB")
            self.used_mem.set(f"{self._to_gb(vm.used):.2f} GB")
            self.available_mem.set(f"{self._to_gb(vm.available):.2f} GB")
            self.mem_percent.set(f"{vm.percent:.1f}%")
            self.mem_history_graph.add_sample(vm.percent)

            sm = psutil.swap_memory()
            self.swap_total.set(f"{self._to_gb(sm.total):.2f} GB")
            self.swap_used.set(f"{self._to_gb(sm.used):.2f} GB")
            self.swap_percent.set(f"{sm.percent:.1f}%")
        except Exception as exc:
            print(f"Error updating memory metrics: {exc}")


class GPUPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="10")

        self._system = platform.system()

        self.info_label = ttk.Label(
            self,
            text="Detecting GPUs...",
            font=("Helvetica", 12),
            foreground="blue",
            wraplength=500,
            justify="left",
        )
        self.info_label.pack(anchor="w", pady=(0, 10))

        self.gpu_frames = []
        self._detect_initial()

    def _detect_initial(self) -> None:
        # macOS: use system_profiler to show static GPU information
        if self._system == "Darwin":
            self._setup_macos_gpus()
            return

        if GPUtil is None:
            self.info_label.config(
                text=(
                    "GPUtil is not installed or failed to import. "
                    "GPU monitoring is disabled.\n\n"
                    "Install with: pip install GPUtil"
                ),
                foreground="red",
            )
            return

        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                self.info_label.config(
                    text="No supported GPUs detected on this system.",
                    foreground="orange",
                )
                return

            self.info_label.config(
                text="GPU Metrics (NVIDIA via nvidia-smi / GPUtil):",
                foreground="black",
            )

            for gpu in gpus:
                frame = self._create_gpu_frame(gpu)
                frame.pack(fill="x", expand=True, pady=(0, 10))
                self.gpu_frames.append(frame)
        except Exception as exc:
            self.info_label.config(
                text=f"Error detecting GPUs: {exc}", foreground="red"
            )

    def _setup_macos_gpus(self) -> None:
        """Populate static GPU info on macOS using system_profiler."""
        try:
            output = subprocess.check_output(
                ["system_profiler", "SPDisplaysDataType", "-json"],
                text=True,
            )
            data = json.loads(output)
            displays = data.get("SPDisplaysDataType", [])

            if not displays:
                self.info_label.config(
                    text="No GPU information reported by system_profiler.",
                    foreground="orange",
                )
                return

            self.info_label.config(
                text=(
                    "GPU Information (macOS via system_profiler).\n"
                    "Real-time usage/temperature is not exposed by the OS APIs used here."
                ),
                foreground="black",
            )

            for idx, gpu in enumerate(displays):
                frame = ttk.LabelFrame(self, text=f"GPU {idx}", padding="10")
                frame.pack(fill="x", expand=True, pady=(0, 10))

                name = gpu.get("sppci_model") or gpu.get("_name", "Unknown GPU")
                vendor = gpu.get("spdisplays_vendor", "Unknown vendor")
                vram = gpu.get("spdisplays_vram") or gpu.get(
                    "spdisplays_vram_shared", "N/A"
                )
                metal = gpu.get("spdisplays_metal", "N/A")

                tk.Label(frame, text="Name:", font=("Helvetica", 11, "bold")).grid(
                    row=0, column=0, sticky=tk.W, padx=(0, 10)
                )
                tk.Label(frame, text=name).grid(row=0, column=1, sticky=tk.W)

                tk.Label(frame, text="Vendor:", font=("Helvetica", 11, "bold")).grid(
                    row=1, column=0, sticky=tk.W, padx=(0, 10)
                )
                tk.Label(frame, text=vendor).grid(row=1, column=1, sticky=tk.W)

                tk.Label(frame, text="VRAM:", font=("Helvetica", 11, "bold")).grid(
                    row=2, column=0, sticky=tk.W, padx=(0, 10)
                )
                tk.Label(frame, text=vram).grid(row=2, column=1, sticky=tk.W)

                tk.Label(
                    frame, text="Metal Support:", font=("Helvetica", 11, "bold")
                ).grid(row=3, column=0, sticky=tk.W, padx=(0, 10)
                )
                tk.Label(frame, text=metal).grid(row=3, column=1, sticky=tk.W)

        except Exception as exc:
            self.info_label.config(
                text=f"Error reading macOS GPU info: {exc}", foreground="red"
            )

    def _create_gpu_frame(self, gpu):
        frame = ttk.LabelFrame(self, text=f"GPU {gpu.id}", padding="10")

        frame.name = tk.StringVar(value=gpu.name)
        frame.load = tk.StringVar(value="0%")
        frame.mem_util = tk.StringVar(value="0%")
        frame.mem_used = tk.StringVar(value="0 GB")
        frame.mem_total = tk.StringVar(value="0 GB")
        frame.temp = tk.StringVar(value="N/A")
        frame.power = tk.StringVar(value="N/A")

        ttk.Label(
            frame, text="Name:", font=("Helvetica", 11, "bold")
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(frame, textvariable=frame.name).grid(
            row=0, column=1, sticky=tk.W
        )

        ttk.Label(
            frame, text="GPU Load:", font=("Helvetica", 11, "bold")
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(frame, textvariable=frame.load).grid(
            row=1, column=1, sticky=tk.W
        )

        ttk.Label(
            frame, text="Memory Usage:", font=("Helvetica", 11, "bold")
        ).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(frame, textvariable=frame.mem_util).grid(
            row=2, column=1, sticky=tk.W
        )

        ttk.Label(
            frame, text="Memory Used / Total:", font=("Helvetica", 11, "bold")
        ).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(frame, textvariable=frame.mem_used).grid(
            row=3, column=1, sticky=tk.W
        )
        ttk.Label(frame, textvariable=frame.mem_total).grid(
            row=3, column=2, sticky=tk.W, padx=(10, 0)
        )

        ttk.Label(
            frame, text="Temperature:", font=("Helvetica", 11, "bold")
        ).grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(frame, textvariable=frame.temp).grid(
            row=4, column=1, sticky=tk.W
        )

        ttk.Label(
            frame, text="Power Draw:", font=("Helvetica", 11, "bold")
        ).grid(row=5, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(frame, textvariable=frame.power).grid(
            row=5, column=1, sticky=tk.W
        )

        return frame

    @staticmethod
    def _to_gb(value_mb: float) -> float:
        return value_mb / 1024.0

    def update_metrics(self) -> None:
        # On macOS we currently only display static GPU info from system_profiler.
        if self._system == "Darwin":
            return

        if GPUtil is None or not self.gpu_frames:
            return

        try:
            gpus = GPUtil.getGPUs()
            for gpu, frame in zip(gpus, self.gpu_frames):
                frame.name.set(gpu.name)
                frame.load.set(f"{gpu.load * 100:.1f}%")
                frame.mem_util.set(f"{gpu.memoryUtil * 100:.1f}%")
                frame.mem_used.set(f"{self._to_gb(gpu.memoryUsed):.2f} GB used")
                frame.mem_total.set(f"{self._to_gb(gpu.memoryTotal):.2f} GB total")
                if gpu.temperature is not None:
                    frame.temp.set(f"{gpu.temperature:.1f} °C")
                else:
                    frame.temp.set("N/A")
                if gpu.powerDraw is not None and gpu.powerLimit is not None:
                    frame.power.set(
                        f"{gpu.powerDraw:.1f} W / {gpu.powerLimit:.1f} W"
                    )
                else:
                    frame.power.set("N/A")
        except Exception as exc:
            print(f"Error updating GPU metrics: {exc}")


class StoragePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="10")

        self.disk_frames = []
        self.last_io = None
        self.last_time = None

        ttk.Label(self, text="Storage Information", font=("Helvetica", 16)).pack(
            anchor="w", pady=(0, 10)
        )

        self.io_label = ttk.Label(
            self,
            text="Read/Write Speeds: N/A",
            font=("Helvetica", 11),
            foreground="blue",
        )
        self.io_label.pack(anchor="w", pady=(0, 10))

        self.disks_container = ttk.Frame(self)
        self.disks_container.pack(fill="both", expand=True)

        self._build_disks()

    def _build_disks(self) -> None:
        for child in self.disks_container.winfo_children():
            child.destroy()
        self.disk_frames.clear()

        try:
            partitions = psutil.disk_partitions(all=False)
            if not partitions:
                ttk.Label(
                    self.disks_container,
                    text="No disk partitions detected.",
                    foreground="orange",
                ).pack(anchor="w")
                return

            for part in partitions:
                frame = ttk.LabelFrame(
                    self.disks_container, text=part.device, padding="10"
                )
                frame.pack(fill="x", expand=True, pady=(0, 8))

                frame.mountpoint = tk.StringVar(value=part.mountpoint)
                frame.fstype = tk.StringVar(value=part.fstype)
                frame.total = tk.StringVar(value="0 GB")
                frame.used = tk.StringVar(value="0 GB")
                frame.free = tk.StringVar(value="0 GB")
                frame.percent = tk.StringVar(value="0%")

                ttk.Label(
                    frame, text="Mount:", font=("Helvetica", 11, "bold")
                ).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
                ttk.Label(frame, textvariable=frame.mountpoint).grid(
                    row=0, column=1, sticky=tk.W
                )

                ttk.Label(
                    frame, text="File System:", font=("Helvetica", 11, "bold")
                ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
                ttk.Label(frame, textvariable=frame.fstype).grid(
                    row=1, column=1, sticky=tk.W
                )

                ttk.Label(
                    frame, text="Total:", font=("Helvetica", 11, "bold")
                ).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
                ttk.Label(frame, textvariable=frame.total).grid(
                    row=2, column=1, sticky=tk.W
                )

                ttk.Label(
                    frame, text="Used:", font=("Helvetica", 11, "bold")
                ).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
                ttk.Label(frame, textvariable=frame.used).grid(
                    row=3, column=1, sticky=tk.W
                )

                ttk.Label(
                    frame, text="Free:", font=("Helvetica", 11, "bold")
                ).grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
                ttk.Label(frame, textvariable=frame.free).grid(
                    row=4, column=1, sticky=tk.W
                )

                ttk.Label(
                    frame, text="Usage:", font=("Helvetica", 11, "bold")
                ).grid(row=5, column=0, sticky=tk.W, padx=(0, 10))
                ttk.Label(frame, textvariable=frame.percent).grid(
                    row=5, column=1, sticky=tk.W
                )

                self.disk_frames.append((part.device, frame))
        except Exception as exc:
            ttk.Label(
                self.disks_container,
                text=f"Error enumerating disks: {exc}",
                foreground="red",
            ).pack(anchor="w")

    @staticmethod
    def _to_gb(value_bytes: float) -> float:
        return value_bytes / (1024**3)

    def update_metrics(self) -> None:
        # Update per-disk usage
        try:
            for device, frame in self.disk_frames:
                try:
                    usage = psutil.disk_usage(frame.mountpoint.get())
                except Exception:
                    continue

                frame.total.set(f"{self._to_gb(usage.total):.2f} GB")
                frame.used.set(f"{self._to_gb(usage.used):.2f} GB")
                frame.free.set(f"{self._to_gb(usage.free):.2f} GB")
                frame.percent.set(f"{usage.percent:.1f}%")
        except Exception as exc:
            print(f"Error updating disk usage: {exc}")

        # Update global read/write speeds
        try:
            now = time.time()
            io_counters = psutil.disk_io_counters()
            if self.last_io is not None and self.last_time is not None:
                interval = now - self.last_time
                if interval > 0:
                    read_speed = (io_counters.read_bytes - self.last_io.read_bytes) / (
                        1024**2 * interval
                    )
                    write_speed = (
                        io_counters.write_bytes - self.last_io.write_bytes
                    ) / (1024**2 * interval)
                    self.io_label.config(
                        text=f"Read/Write Speeds: {read_speed:.2f} MB/s read, {write_speed:.2f} MB/s write"
                    )
            self.last_io = io_counters
            self.last_time = now
        except Exception as exc:
            print(f"Error updating disk IO: {exc}")


class SettingsPage(ttk.Frame):
    """
    Simple settings page to configure refresh interval.
    Changes apply globally for the app.
    """

    def __init__(self, parent, get_interval_callback, set_interval_callback):
        super().__init__(parent, padding="10")
        self.get_interval = get_interval_callback
        self.set_interval = set_interval_callback

        ttk.Label(self, text="Settings", font=("Helvetica", 16)).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        ttk.Label(
            self, text="Refresh Interval (ms):", font=("Helvetica", 12, "bold")
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))

        self.interval_var = tk.IntVar(value=self.get_interval())
        interval_spin = ttk.Spinbox(
            self,
            from_=250,
            to=5000,
            increment=250,
            textvariable=self.interval_var,
            width=10,
            command=self._on_change,
        )
        interval_spin.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(
            self,
            text="Lower values update more frequently but use more CPU.",
            wraplength=350,
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

    def _on_change(self) -> None:
        try:
            value = int(self.interval_var.get())
            value = max(250, min(5000, value))
            self.interval_var.set(value)
            self.set_interval(value)
        except Exception:
            pass


class HardwareMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hardware Monitoring Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        self.refresh_interval_ms = REFRESH_INTERVAL_MS

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.cpu_page = CPUPage(self.notebook)
        self.mem_page = MemoryPage(self.notebook)
        self.gpu_page = GPUPage(self.notebook)
        self.storage_page = StoragePage(self.notebook)
        self.settings_page = SettingsPage(
            self.notebook, self.get_refresh_interval, self.set_refresh_interval
        )

        self.notebook.add(self.cpu_page, text="CPU")
        self.notebook.add(self.mem_page, text="Memory")
        self.notebook.add(self.gpu_page, text="GPU")
        self.notebook.add(self.storage_page, text="Storage")
        self.notebook.add(self.settings_page, text="Settings")

        # Start periodic updates
        self._schedule_update()

    def get_refresh_interval(self) -> int:
        return self.refresh_interval_ms

    def set_refresh_interval(self, value: int) -> None:
        self.refresh_interval_ms = int(value)

    def _update_all(self) -> None:
        self.cpu_page.update_metrics()
        self.mem_page.update_metrics()
        self.gpu_page.update_metrics()
        self.storage_page.update_metrics()

    def _schedule_update(self) -> None:
        self._update_all()
        self.root.after(self.refresh_interval_ms, self._schedule_update)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        app = HardwareMonitorApp()
        app.run()
    except Exception as exc:
        print(f"An error starting app occurred: {exc}")
        import traceback

        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()


