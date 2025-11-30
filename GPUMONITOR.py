import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess
import shutil
import os
import platform

class GPUMonitor:
    def __init__(self, parent):
        self.parent = parent

        self.gpu_clock = tk.StringVar(value="0 MHz")
        self.gpu_fan = tk.StringVar(value="0%")
        self.gpu_name = tk.StringVar(value="Unknown")
        self.gpu_temp = tk.StringVar(value="N/A")

        self.os_type = platform.system().lower()
        self.is_nvidia = False
        self.is_amd = False
        self.is_apple = False

        self.setup_ui()
        self.detect_gpu_vendor()
        self.get_static_info()
        self.start_monitoring()

    def setup_ui(self):
        frame = ttk.LabelFrame(self.parent, text="GPU Information", padding="10")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(frame, text="GPU:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_name).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(frame, text="Clock Speed:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_clock).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(frame, text="Fan Speed:", font=("Helvetica", 12, "bold")).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_fan).grid(row=2, column=1, sticky=tk.W)

        ttk.Label(frame, text="Temperature:", font=("Helvetica", 12, "bold")).grid(row=3, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_temp).grid(row=3, column=1, sticky=tk.W)

        frame.columnconfigure(1, weight=1)

    #detect gpu
    def detect_gpu_vendor(self):
        # mac uses Apple M-series GPUs
        if self.os_type == "darwin":
            self.is_apple = True
            return

        # Linux / Windows detection
        try:
            if shutil.which("nvidia-smi"):
                self.is_nvidia = True
                return
        except:
            pass

        # AMD detection
        # Linux: rocm-smi, amdgpu-ls
        if shutil.which("rocm-smi"):
            self.is_amd = True
            return

        if shutil.which("amdgpu-ls"):
            self.is_amd = True
            return

     #display static stats
    def get_static_info(self):
        if self.is_nvidia:
            self.get_static_info_nvidia()
        elif self.is_amd:
            self.get_static_info_amd()
        elif self.is_apple:
            self.get_static_info_apple()
        else:
            self.gpu_name.set("GPU not detected")

    def get_static_info_nvidia(self):
        try:
            output = subprocess.check_output([
                "nvidia-smi", "--query-gpu=name", "--format=csv,noheader"
            ], text=True).strip()
            self.gpu_name.set(output)
        except:
            self.gpu_name.set("NVIDIA GPU (Unknown)")

    def get_static_info_amd(self):
        try:
            output = subprocess.check_output(["rocm-smi", "--showproductname"], text=True)
            for line in output.splitlines():
                if "Card series" in line:
                    self.gpu_name.set(line.split(":")[1].strip())
                    return
        except:
            self.gpu_name.set("AMD GPU (Unknown)")

    def get_static_info_apple(self):
        try:
            output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True)
            for line in output.splitlines():
                if "Chipset Model:" in line:
                    self.gpu_name.set(line.split(":")[1].strip())
                    return
        except:
            self.gpu_name.set("Apple GPU")

     
    def update_metrics(self):
        if self.is_nvidia:
            self.update_metrics_nvidia()
        elif self.is_amd:
            self.update_metrics_amd()
        elif self.is_apple:
            self.update_metrics_apple()
        else:
            self.gpu_clock.set("N/A")
            self.gpu_fan.set("N/A")
            self.gpu_temp.set("N/A")

    def update_metrics_nvidia(self):
        try:
            output = subprocess.check_output([
                "nvidia-smi",
                "--query-gpu=clocks.gr,fan.speed,temperature.gpu",
                "--format=csv,noheader,nounits"
            ], text=True).strip()

            clock, fan, temp = output.split(", ")
            self.gpu_clock.set(f"{clock} MHz")
            self.gpu_fan.set(f"{fan}%")
            self.gpu_temp.set(f"{temp} °C")
        except:
            self.gpu_clock.set("N/A")
            self.gpu_fan.set("N/A")
            self.gpu_temp.set("N/A")

    def update_metrics_amd(self):
        try:
            output = subprocess.check_output(["rocm-smi"], text=True)

            clock = "N/A"
            fan = "N/A"
            temp = "N/A"

            for line in output.splitlines():
                if "GPU Clock" in line:
                    clock = line.split()[3]
                if "Fan Level" in line:
                    fan = line.split()[3]
                if "Temperature" in line and "(Sensor 0)" in line:
                    temp = line.split()[2]

            self.gpu_clock.set(f"{clock} MHz")
            self.gpu_fan.set(f"{fan}%")
            self.gpu_temp.set(f"{temp} °C")

        except:
            self.gpu_clock.set("N/A")
            self.gpu_fan.set("N/A")
            self.gpu_temp.set("N/A")

    def update_metrics_apple(self):
        try:
             
            output = subprocess.check_output(["powermetrics", "--show-gpu"], text=True)

            clock = "N/A"
            temp = "N/A"

            for line in output.splitlines():
                if "GPU Performance" in line:
                    clock = line.split()[-1]
                if "Temperature" in line:
                    temp = line.split()[-2]

            self.gpu_clock.set(clock)
            self.gpu_fan.set("N/A")
            self.gpu_temp.set(f"{temp} °C")

        except:
            self.gpu_clock.set("N/A")
            self.gpu_fan.set("N/A")
            self.gpu_temp.set("N/A")

    # monitoring 
    def monitoring_thread(self):
        while True:
            try:
                self.update_metrics()
                time.sleep(1)
            except:
                break

    def start_monitoring(self):
        thread = threading.Thread(target=self.monitoring_thread, daemon=True)
        thread.start()

#  main
def main():
    try:
        root = tk.Tk()
        root.title("Hardware Monitor")
        root.geometry("700x600")
        root.resizable(True, True)

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        gpu_frame = ttk.Frame(notebook)
        notebook.add(gpu_frame, text="GPU")

        gpu_monitor = GPUMonitor(gpu_frame)

        root.mainloop()

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
