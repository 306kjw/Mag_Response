import pyvisa
import nidaqmx
import time
import csv
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

stop_flag = False  # Stop flag for measurement

def run_measurement(k2400_mode, k2400_value, vmin, vmax, vstep, k2400_addr, dmm1_addr, dmm2_addr, custom_range_start, custom_range_end, custom_vstep):
    global stop_flag
    stop_flag = False

    try:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voltage_xy_log_{timestamp_str}.csv"

        rm = pyvisa.ResourceManager()
        k2400 = rm.open_resource(k2400_addr)
        dmm1 = rm.open_resource(dmm1_addr)
        dmm2 = rm.open_resource(dmm2_addr)

        if k2400_mode == "voltage":
            k2400.write(":SOUR:FUNC VOLT")
            k2400.write(f":SOUR:VOLT {k2400_value}")
        else:
            k2400.write(":SOUR:FUNC CURR")
            k2400.write(f":SOUR:CURR {k2400_value}")
        k2400.write(":OUTP ON")

        dmm1.write("CONF:VOLT:DC AUTO")
        dmm2.write("CONF:VOLT:DC AUTO")

        daq_channel = "Dev1/ao0"

        coarse_points = np.arange(vmin, vmax + vstep / 2, vstep)
        fine_points = np.arange(custom_range_start, custom_range_end + custom_vstep / 2, custom_vstep)

        filtered_coarse = []
        for v in coarse_points:
            if not (custom_range_start <= v <= custom_range_end):
                filtered_coarse.append(round(v, 6))

        all_points = sorted(set(filtered_coarse + [round(v, 6) for v in fine_points]))
        voltage_sequence = all_points + list(reversed(all_points)) + [0.0]

        # === Initialize graph ===
        plt.ion()
        fig, ax = plt.subplots()
        try:
            fig.canvas.manager.window.wm_geometry("+2000+100")  # Move graph window
        except Exception as e:
            print("Failed to set graph window position:", e)

        line, = ax.plot([], [], 'o-', label='DMM2 vs DMM1')
        ax.set_xlabel("DMM1 Voltage (V)")
        ax.set_ylabel("DMM2 Voltage (V)")
        ax.set_title("")
        ax.grid(True)
        ax.legend()
        x_vals, y_vals = [], []

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time(s)", "DMM1_X(V)", "DMM2_Y(V)"])

            with nidaqmx.Task() as daq_task:
                daq_task.ao_channels.add_ao_voltage_chan(daq_channel)
                start_time = time.time()

                for i, v_out in enumerate(voltage_sequence):
                    if stop_flag:
                        print("Measurement stopped by user. Exiting.")
                        daq_task.write(0.0)
                        break

                    daq_task.write(v_out)
                    time.sleep(0.05)

                    t = time.time() - start_time
                    try:
                        v1 = float(dmm1.query("READ?"))
                        v2 = float(dmm2.query("READ?"))
                    except Exception as e:
                        print("Read error:", e)
                        v1, v2 = float('nan'), float('nan')

                    if i == 0 or i == len(voltage_sequence) - 1:
                        continue

                    writer.writerow([f"{t:.2f}", f"{v1:.6f}", f"{v2:.6f}"])
                    x_vals.append(v1)
                    y_vals.append(v2)

                    line.set_data(x_vals, y_vals)
                    ax.relim()
                    ax.autoscale_view()
                    plt.pause(0.01)

                try:
                    daq_task.write(0.0)
                except Exception as e:
                    print("Failed to output 0V to DAQ:", e)

        k2400.write(":OUTP OFF")
        k2400.close()
        dmm1.close()
        dmm2.close()
        rm.close()

        plt.pause(0.5)
        messagebox.showinfo("Complete", "Measurement is completed.")
        plt.ioff()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during execution: {e}")
        try:
            daq_task.write(0.0)
        except:
            pass
        try:
            k2400.write(":OUTP OFF")
        except:
            pass

# === GUI Setup ===
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

root = tk.Tk()
root.title("Voltage/Current Sweep Controller")

k_mode_var = tk.StringVar(value="voltage")

mode_frame = ttk.LabelFrame(root, text="Source Mode")
mode_frame.pack(padx=10, pady=5, fill='x')
ttk.Radiobutton(mode_frame, text="Voltage", variable=k_mode_var, value="voltage").pack(side='left', padx=5, pady=5)
ttk.Radiobutton(mode_frame, text="Current", variable=k_mode_var, value="current").pack(side='left', padx=5, pady=5)

addr_frame = ttk.LabelFrame(root, text="Instrument Addresses")
addr_frame.pack(padx=10, pady=5, fill='x')

addr_labels_defaults = [
    ("Sourcemeter Address:", "GPIB0::01::INSTR"),
    ("Multimeter 1 Address:", "GPIB0::02::INSTR"),
    ("Multimeter 2 Address:", "GPIB0::03::INSTR")
]

addr_entries = []
for label, default in addr_labels_defaults:
    frame = ttk.Frame(addr_frame)
    frame.pack(padx=5, pady=2, fill='x')
    ttk.Label(frame, text=label).pack(side='left')
    entry = ttk.Entry(frame)
    entry.insert(0, default)
    entry.pack(side='right', expand=True, fill='x')
    addr_entries.append(entry)

fields = [
    ("Source Value (V or A):", "1"),
    ("Coil Min Voltage (V):", "-10.0"),
    ("Coil Max Voltage (V):", "10.0"),
    ("Coil Voltage Step (V):", "0.5"),
    ("Fine Range Start (V):", "-1.0"),
    ("Fine Range End (V):", "1.0"),
    ("Fine Voltage Step (V):", "0.05")
]

entries = []
for label, default in fields:
    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=5, fill='x')
    ttk.Label(frame, text=label).pack(side='left')
    entry = ttk.Entry(frame)
    entry.insert(0, default)
    entry.pack(side='right', expand=True, fill='x')
    entries.append(entry)

def on_run():
    try:
        k_mode = k_mode_var.get()
        k_value = float(entries[0].get())
        vmin = float(entries[1].get())
        vmax = float(entries[2].get())
        vstep = float(entries[3].get())
        custom_start = float(entries[4].get())
        custom_end = float(entries[5].get())
        custom_step = float(entries[6].get())
        k2400_addr = addr_entries[0].get()
        dmm1_addr = addr_entries[1].get()
        dmm2_addr = addr_entries[2].get()
        run_measurement(k_mode, k_value, vmin, vmax, vstep, k2400_addr, dmm1_addr, dmm2_addr, custom_start, custom_end, custom_step)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

def on_stop():
    global stop_flag
    stop_flag = True

button_frame = ttk.Frame(root)
button_frame.pack(pady=(10, 10))

ttk.Button(button_frame, text="Start Measurement", command=on_run).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Stop Measurement", command=on_stop).grid(row=0, column=1, padx=5)

root.mainloop()
