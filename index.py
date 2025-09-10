import psutil
import GPUtil
import tkinter as tk
from tkinter import ttk
import threading
import time
import platform
import subprocess




class CPUMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hardware Monitor - CPU")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        #variables for the labels

        self.cpu_usage = tk.StringVar(value="0%")
        self.cpu_frequency = tk.StringVar(value="0 MHz")
        self.cpu_temp = tk.StringVar(value="N/A")
        self.cpu_cores = tk.StringVar(value="0")
        self.cpu_threads = tk.StringVar(value="0")
        self.cpu_name = tk.StringVar(value="Unknown")

        self.core_usages= []

        self.setup_ui()
        self.get_static_info()
        self.start_monitoring()


    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        #title
        title_Label = ttk.Label(main_frame, text="CPU Information", font=("Helvetica", 16))
        title_Label.grid(row = 0, column=0, columnspan=2, pady=(0, 20))


        #CPU Name
        ttk.Label(main_frame, text="Processor:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx = (0, 10))
        ttk.Label(main_frame, textvariable=self.cpu_name, wraplength=300).grid(row=1, column=1, sticky=tk.W)

        #CPU cores & threads
        ttk.Label(main_frame, text="Physical Cores:", font=("Helvetica", 12, "bold")).grid(row=2, column=0, sticky=tk.W, padx = (0, 10))
        ttk.Label(main_frame, textvariable=self.cpu_cores).grid(row=2, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Logical Processors:", font=("Helvetica", 12, "bold")).grid(row=3, column=0, sticky=tk.W, padx = (0, 10))
        ttk.Label(main_frame, textvariable=self.cpu_threads).grid(row=3, column=1, sticky=tk.W)

        #seperator
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        #Real-time info
        ttk.Label(main_frame, text="Real-time Metrics", font=("Helvetica", 16)).grid(row=5, column=0, columnspan=2, pady=(0, 10))

        #Overall CPU usage
        ttk.Label(main_frame, text="Overall CPU Usage:", font=("Helvetica", 12, "bold")).grid(row=6, column=0, sticky=tk.W, padx = (0, 10))
        usage_label = ttk.Label(main_frame, textvariable=self.cpu_usage, font=("Helvetica", 12), foreground="blue")
        usage_label.grid(row=6, column=1, sticky=tk.W)


        #CPU Frequency
        ttk.Label(main_frame, text="Current Frequency:", font=("Helvetica", 12, "bold")).grid(row=7, column=0, sticky=tk.W, padx = (0, 10))
        ttk.Label(main_frame, textvariable=self.cpu_frequency, font=("Helvetica", 12)).grid(row=7, column=1, sticky=tk.W)

        #CPU Temperature
        ttk.Label(main_frame, text="Temperature:", font=("Helvetica", 12, "bold")).grid(row=8, column=0, sticky=tk.W, padx = (0, 10))
        ttk.Label(main_frame, textvariable=self.cpu_temp, font=("Helvetica", 12)).grid(row=8, column=1, sticky=tk.W)

        #Per-core usage
        self.core_frame = ttk.LabelFrame(main_frame, text="Per-Core Usage", padding = "10")
        self.core_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))

        #Progress bar for each core
        self.create_core_widgets()

        for i in range(10):
            main_frame.rowconfigure(i, weight=1 if i == 9 else 0)

    def create_core_widgets(self):
        cpu_count = psutil.cpu_count(logical=True)

        cols = min(4, cpu_count)
        rows = (cpu_count + cols - 1) // cols

        self.core_usages = []
        self.core_bars = []
        self.core_labels = []

        for i in range(cpu_count):
            row = i // cols
            col = i % cols

            core_var = tk.StringVar(value="0%")
            self.core_usages.append(core_var)

            #core label
            label = ttk.Label(self.core_frame, text=f"Core {i}:", font=("Helvetica", 9))
            label.grid(row=row*2, column=col, sticky=tk.W, padx=5, pady=2)
            self.core_labels.append(label)

            #progess bar
            progress = ttk.Progressbar(self.core_frame, length=100, mode='determinate')
            progress.grid(row=row*2+1, column=col, padx=5, pady=2, sticky=(tk.W, tk.E))
            self.core_bars.append(progress)


            self.core_frame.columnconfigure(col, weight=1)


    def get_static_info(self):
        try:
            if platform.system() == "Windows":
                import wmi
                c = wmi.WMI()
                for processor in c.Win32_Processor():
                    self.cpu_name.set(processor.Name.strip())
                    break
            elif platform.system() == "Darwin":
                try:
                    cpu_name = subprocess.check_output(
                        ["sysctl", "-n", "machdep.cpu.brand_string"]
                    ).strip().decode()
                    self.cpu_name.set(cpu_name)
                except Exception:
                    self.cpu_name.set("Unknown")
            else:
                self.cpu_name.set(platform.processor() or "Unknown")
        except:
            self.cpu_name.set("Unable to detect a processor")
            print("Error fetching CPU name")


        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)

        self.cpu_cores.set(str(physical_cores) if physical_cores else "N/A")
        self.cpu_threads.set(str(logical_cores) if logical_cores else "N/A")

    def get_cpu_temperature(self):
        try:
            if platform.system() == "Linux":
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    for temp in temps['coretemp']:
                        if 'Package' in temp.label or 'Core' in temp.label:
                            return f"{temp.current:.1f} °C"
                elif 'k10temp' in temps:
                    for temp in temps['k10temp']:
                        if 'Tctl' in temp.label or temp.label == '':
                            return f"{temp.current:.1f} °C"
            elif platform.system() == "Windows":
                #will return to windows later as it requires additional libraries
                pass
        except:
            pass
        return "N/A"


    def update_metrics(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(f"{cpu_percent:.1f}%")

            core_percents = psutil.cpu_percent(percpu=True, interval=None)
            for i, (percent, var, bar) in enumerate(zip(core_percents, self.core_usages, self.core_bars)):
                var.set(f"{percent:.1f}%")
                bar['value'] = percent

                self.core_labels[i].config(text=f"Core {i}: {percent:.1f}%")

            freq = psutil.cpu_freq()
            if freq:
                self.cpu_frequency.set(f"{freq.current:.1f} MHz")
            else:
                self.cpu_frequency.set("N/A")

            temp = self.get_cpu_temperature()
            self.cpu_temp.set(temp)
        except Exception as e:
            print(f"Error updating metrics: {e}")

        
    def monitoring_thread(self):
        while True:
            try:
                self.update_metrics()
                time.sleep(1)
            except:
                break
        
        
    def start_monitoring(self):
        monitor_thread = threading.Thread(target=self.monitoring_thread, daemon=True)
        monitor_thread.start()

    def run(self):
        self.root.mainloop()

def main():
        try:
            app = CPUMonitor()
            app.run()
        except Exception as e:
            print(f"An error starting app occurred: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")


if __name__ == "__main__":
    main()
                

            

