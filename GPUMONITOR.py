import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess
import shutil
import os






class GPUMonitor:
    def __init__(self, parent):
        self.parent = parent

        self.gpu_clock = tk.StringVar(value="0 MHz")
        self.gpu_fan = tk.StringVar(value="0%")
        self.gpu_name = tk.StringVar(value="Unknown")
        self.gpu_temp = tk.StringVar(value="N/A")

        self.setup_ui()
        self.get_static_info()
        self.start_monitoring()

    def setup_ui(self):
        frame = ttk.LabelFrame(self.parent, text="GPU Information", padding="10")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        #Gpu name
        ttk.Label(frame, text="GPU:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_name).grid(row=0, column=1, sticky=tk.W)

        #clock speed
        ttk.Label(frame, text="Clock Speed:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_clock).grid(row=1, column=1, sticky=tk.W)

        #fan speed
        ttk.Label(frame, text="Fan Speed:", font=("Helvetica", 12, "bold")).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.gpu_fan).grid(row=2, column=1, sticky=tk.W)

        frame.columnconfigure(1, weight=1)

    def get_nvidia_smi_path(self):
        if shutil.which("nvidia-smi"):
            return "nvidia-smi"
        alt_path = r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
        return alt_path if os.path.exists(alt_path) else None

    def get_static_info(self):
        smi_path = self.get_nvidia_smi_path()
        if not smi_path:
            self.gpu_name.set("nvidia-smi not found")
            return

        try:
            output = subprocess.check_output(
                [smi_path, "--query-gpu=name", "--format=csv,noheader"],
                text=True
            ).strip()
            self.gpu_name.set(output)
        except Exception as e:
            self.gpu_name.set("Unknown")
            print(f"Error fetching GPU name: {e}")

    def update_metrics(self):
        smi_path = self.get_nvidia_smi_path()
        if not smi_path:
            self.gpu_clock.set("N/A")
            self.gpu_fan.set("N/A")
            self.gpu_temp.set("N/A")
            return

        try:
            output = subprocess.check_output(
                [smi_path, "--query-gpu=clocks.gr,fan.speed,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                text=True
            ).strip()

            clock, fan, temp = output.split(", ")
            self.gpu_clock.set(f"{clock} MHz")
            self.gpu_fan.set(f"{fan}%")
            self.gpu_temp.set(f"{temp} °C")

        except Exception as e:
            print(f"Error updating GPU metrics: {e}")
            self.gpu_clock.set("N/A")
            self.gpu_fan.set("N/A")
            self.gpu_temp.set("N/A")

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


def main():
    try:
        root = tk.Tk()
        root.title("Hardware Monitor")
        root.geometry("700x600")
        root.resizable(True, True)

        # Use a Notebook or just a Frame
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # GPU Tab
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
