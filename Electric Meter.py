import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from plyer import notification
from collections import deque
from tkinter import PhotoImage
import serial
import serial.tools.list_ports

class Meter:
    #ya meter ka data sambhal rhi ha 
    def __init__(self, meter_id, building_name, meter_type):
        self.meter_id = meter_id
        self.building_name = building_name
        self.meter_type = meter_type
        self.previous_reading = 0.0
        self.current_reading = 0.0
        self.bill_history = deque(maxlen=5)
        self.is_running = False
        self.thread = None
        self.notification_sent = False
        self.serial_connection = None
        self.connected = False
        
    def connect_to_arduino(self):
        #controller ka code ha ya
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                # Try common baud rates
                for baud in [9600, 115200, 57600, 38400]:
                    try:
                        self.serial_connection = serial.Serial(port.device, baud, timeout=1)
                        print(f"Connected to {port.device} at {baud} baud")
                        self.connected = True
                        return True
                    except:
                        continue
            except:
                continue
        print("Could not find Arduino")
        return False
        
    def start_simulation(self):
        #controller sa reading la k program ma dala ga
        if not self.is_running:
            if not self.connected:
                if not self.connect_to_arduino():
                    messagebox.showerror("Error", "Could not connect to Arduino")
                    return False
            
            self.is_running = True
            self.thread = threading.Thread(target=self.update_reading, daemon=True)
            self.thread.start()
            return True
        return True
            
    def stop_simulation(self):
        #meter reading ko stop kr deta ha jb b connection hata do ya bnd kr do
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.serial_connection and self.connected:
            self.serial_connection.close()
            self.connected = False
            
    def update_reading(self):
        #controller sa value la k formula ma dalta ha or 150 par pa notify krta ha
        while self.is_running and self.connected:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    try:
                        # Convert to float and accumulate as units (kWh)
                        # Assuming Arduino sends current in Amperes
                        current = float(line)
                        
                        # Convert current to power (Watts) then to energy (kWh)
                        # Assuming standard household voltage (adjust as needed)
                        voltage = 230.0  # Standard voltage in many countries
                        power = current * voltage  # Watts
                        energy = power / 1000.0 / 3600.0  # kWh per second
                        
                        # Accumulate the energy (simulating an energy meter)
                        self.current_reading += energy
                        self.current_reading = round(self.current_reading, 4)
                        
                        # Check for high usage notification
                        if self.current_reading >= 150 and not self.notification_sent:
                            self.send_usage_notification()
                            self.notification_sent = True
                            
                    except ValueError:
                        print(f"Invalid data received: {line}")
                        
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                self.connected = False
                self.is_running = False
                break
                
            time.sleep(0.1)  # Small delay to prevent CPU overuse
            
    def send_usage_notification(self):
        #Send desktop notification for high usage
        notification.notify(
            title=f"⚡ High Usage Alert - {self.meter_id}",
            message=f"Electricity usage at {self.building_name} exceeded 150 units!",
            timeout=10
        )
        
    def calculate_bill(self):
        #Current bill Calculate krta ha based on usage
        units_used = max(self.current_reading - self.previous_reading, 0)
        rates = {"🏠 Residential": 10.7, "🏢 Commercial": 13.5, "🏭 Industrial": 25.5}
        rate = rates.get(self.meter_type, 10.7)
        bill = round(units_used * rate, 2)
        
        self.bill_history.append({
            "previous": self.previous_reading,
            "current": self.current_reading,
            "units": units_used,
            "rate": rate,
            "bill": bill
        })
        
        self.previous_reading = self.current_reading
        return {"units_used": units_used, "rate": rate, "bill": bill}

class SmartMeterApp:
    def __init__(self, root):
        #App ka structure
        self.root = root
        
        # Set application icon (must be in same directory)
        self.set_application_icon()
        
        # Window configuration
        self.root.title("⚡ Smart Meter Billing System")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        self.root.config(bg="#f0f8ff")
        
        # Initialize meter management
        self.meters = {}
        self.current_meter_id = None
        self.next_meter_num = 1
        self.popup = None
        
        # Create UI components
        self.create_widgets()
        
        # Start background processes
        self.animate_title()
        self.auto_calculate_bill_loop()
        self.update_displayed_reading()
        self.update_connection_status()
        
        # Handle window resize
        self.root.bind("<Configure>", self.on_window_resize)

    def set_application_icon(self):
        #Set icon for both window and taskbar/dock
        try:
            # First try Windows .ico format (best for taskbar)
            self.root.iconbitmap(default='smartmeter.ico')
            self.root.iconbitmap('smartmeter.ico')
        except:
            try:
                # Fallback to PNG for cross-platform
                icon = PhotoImage(file='smartmeter.png')
                # These 2 lines make it work in taskbar/dock
                self.root.iconphoto(True, icon)
                self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
            except Exception as e:
                print(f"Icon not loaded: {e}")  # Optional error message

    def create_widgets(self):
        #Create all GUI components
        # Title bar
        self.title_label = tk.Label(
            self.root, text="⚡ Smart Meter Billing System",
            font=("Segoe UI", 26, "bold"), bg="#0077b6", fg="white", pady=20
        )
        self.title_label.pack(fill="x", pady=(0, 10))
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#caf0f8", bd=3, relief="ridge")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Meter management section
        self.create_meter_management_frame(main_frame)
        
        # Meter data display
        self.create_meter_data_frame(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
        
        # Footer
        self.create_footer()
        
        # Disable buttons until meter is selected
        self.toggle_buttons(False)

    def create_meter_management_frame(self, parent):
        #Create meter control panel
        frame = tk.LabelFrame(
            parent, text="Meter Management", 
            font=("Segoe UI", 14, "bold"), bg="#ade8f4", fg="#03045e", padx=20, pady=10
        )
        frame.pack(fill="x", padx=30, pady=10)
        
        # Building name entry
        tk.Label(frame, text="🏢 Building Name:", font=("Segoe UI", 12), bg="#ade8f4"
                ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.building_entry = tk.Entry(frame, font=("Segoe UI", 12), width=25)
        self.building_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Meter type selection
        tk.Label(frame, text="📟 Meter Type:", font=("Segoe UI", 12), bg="#ade8f4"
                ).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.new_meter_type = ttk.Combobox(
            frame, values=["🏠 Residential", "🏢 Commercial", "🏭 Industrial"], 
            state="readonly", font=("Segoe UI", 12), width=20
        )
        self.new_meter_type.grid(row=0, column=3, padx=5, pady=5)
        self.new_meter_type.set("🏠 Residential")
        
        # Add meter button
        self.add_meter_btn = tk.Button(
            frame, text="➕ Add New Meter",
            font=("Segoe UI", 12), bg="#2a9d8f", fg="white",
            command=self.add_new_meter
        )
        self.add_meter_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Meter selection dropdown
        tk.Label(frame, text="🔌 Select Meter:", font=("Segoe UI", 12), bg="#ade8f4"
                ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.meter_selector = ttk.Combobox(
            frame, state="readonly", font=("Segoe UI", 12), width=30
        )
        self.meter_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        self.meter_selector.bind("<<ComboboxSelected>>", self.select_meter)
        
        # Meter info display
        self.meter_info_label = tk.Label(
            frame, text="No meter selected", 
            font=("Segoe UI", 11), bg="#ade8f4", fg="#023e8a"
        )
        self.meter_info_label.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky="w")

    def create_meter_data_frame(self, parent):
        #Create meter data display area
        frame = tk.LabelFrame(
            parent, text="Meter Data", 
            font=("Segoe UI", 14, "bold"), bg="#bde0fe", fg="#03045e", padx=20, pady=10
        )
        frame.pack(fill="x", padx=30, pady=10)
        
        # Connection status
        self.connection_status_label = tk.Label(
            frame, text="Status: ❌ Arduino not connected", 
            font=("Segoe UI", 10), bg="#bde0fe", fg="red"
        )
        self.connection_status_label.grid(row=0, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        
        # Meter type info
        self.meter_type_label = tk.Label(
            frame, text="Meter Type: Not selected", 
            font=("Segoe UI", 12), bg="#bde0fe"
        )
        self.meter_type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Info button
        self.meter_type_info_btn = tk.Button(
            frame, text="ℹ️ Info", 
            font=("Segoe UI", 10), bg="#219ebc", fg="white",
            command=self.show_meter_info
        )
        self.meter_type_info_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Create reading displays
        self.create_labeled_entry(frame, "⬅️ Previous Reading:", 2, 0)
        self.create_labeled_entry(frame, "➡️ Current Reading:", 2, 2)

    def create_action_buttons(self, parent):
        #Create control buttons
        frame = tk.Frame(parent, bg="#caf0f8")
        frame.pack(pady=15)
        
        # Calculate Bill button
        self.calc_button = tk.Button(
            frame, text="💰 Calculate Bill",
            font=("Segoe UI", 14, "bold"), bg="#2a9d8f", fg="white", 
            padx=20, pady=8, command=self.calculate_bill
        )
        self.calc_button.grid(row=0, column=0, padx=15)
        
        # Show Bill button
        self.show_button = tk.Button(
            frame, text="📄 Show Bill",
            font=("Segoe UI", 14), bg="#219ebc", fg="white", 
            padx=20, pady=8, command=self.show_last_bill
        )
        self.show_button.grid(row=0, column=1, padx=15)
        
        # Clear button
        self.clear_button = tk.Button(
            frame, text="🧹 Clear",
            font=("Segoe UI", 14), bg="#ffb703", fg="black", 
            padx=20, pady=8, command=self.clear_fields
        )
        self.clear_button.grid(row=0, column=2, padx=15)
        
        # History button
        self.history_button = tk.Button(
            frame, text="🕓 Bill History",
            font=("Segoe UI", 14), bg="#6a4c93", fg="white", 
            padx=20, pady=8, command=self.show_bill_history
        )
        self.history_button.grid(row=0, column=3, padx=15)

    def create_footer(self):
        #Create copyright footer
        self.footer_label = tk.Label(
            self.root, text="© 2025 Maddy Co.", font=("Segoe UI", 11),
            bg="#0077b6", fg="white", pady=8
        )
        self.footer_label.pack(fill="x", side="bottom")

    def create_labeled_entry(self, parent, label_text, row, column):
        #Helper to create labeled entry fields
        tk.Label(parent, text=label_text, font=("Segoe UI", 12), bg=parent["bg"]
               ).grid(row=row, column=column, padx=5, pady=5, sticky="e")
        
        frame = tk.Frame(parent, bg="white", bd=2, relief="sunken")
        frame.grid(row=row, column=column+1, padx=5, pady=5, sticky="w")
        
        entry = tk.Entry(frame, font=("Segoe UI", 12), bd=0, width=15, state="readonly")
        entry.pack(padx=5, pady=5)
        
        if "Previous" in label_text:
            self.previous_entry = entry
        else:
            self.current_entry = entry

    def update_connection_status(self):
        #Update UI to show Arduino connection status
        if hasattr(self, 'connection_status_label'):
            if self.current_meter_id and self.meters[self.current_meter_id].connected:
                self.connection_status_label.config(text="Status: ✅ Connected to Arduino", fg="green")
            else:
                self.connection_status_label.config(text="Status: ❌ Arduino not connected", fg="red")
        self.root.after(1000, self.update_connection_status)

    def add_new_meter(self):
        #Add a new meter to the system
        building_name = self.building_entry.get().strip()
        meter_type = self.new_meter_type.get()
        
        if not building_name:
            messagebox.showerror("Error", "Please enter a building name")
            return
            
        meter_id = f"MTR{self.next_meter_num:03d}"
        self.next_meter_num += 1
        
        new_meter = Meter(meter_id, building_name, meter_type)
        if not new_meter.start_simulation():
            return
            
        self.meters[meter_id] = new_meter
        
        self.update_meter_selector()
        self.meter_selector.set(f"{meter_id} - {building_name}")
        self.select_meter(None)
        self.building_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"New meter added: {meter_id}")

    def update_meter_selector(self):
        #Update the meter dropdown list
        meter_list = [f"{mid} - {meter.building_name}" for mid, meter in self.meters.items()]
        self.meter_selector["values"] = meter_list

    def select_meter(self, event):
       #Handle meter selection from dropdown
        selection = self.meter_selector.get()
        if not selection:
            return
            
        meter_id = selection.split(" - ")[0]
        
        if meter_id in self.meters:
            self.current_meter_id = meter_id
            meter = self.meters[meter_id]
            
            self.meter_type_label.config(text=f"Meter Type: {meter.meter_type}")
            
            self.previous_entry.config(state="normal")
            self.previous_entry.delete(0, tk.END)
            self.previous_entry.insert(0, f"{meter.previous_reading:.2f}")
            self.previous_entry.config(state="readonly")
            
            self.current_entry.config(state="normal")
            self.current_entry.delete(0, tk.END)
            self.current_entry.insert(0, f"{meter.current_reading:.2f}")
            self.current_entry.config(state="readonly")
            
            self.meter_info_label.config(
                text=f"ID: {meter.meter_id} | Building: {meter.building_name}"
            )
            
            self.toggle_buttons(True)

    def toggle_buttons(self, enabled):
        #Enable/disable action buttons
        state = "normal" if enabled else "disabled"
        if hasattr(self, 'calc_button') and self.calc_button:
            self.calc_button.config(state=state)
        if hasattr(self, 'show_button') and self.show_button:
            self.show_button.config(state=state)
        if hasattr(self, 'clear_button') and self.clear_button:
            self.clear_button.config(state=state)
        if hasattr(self, 'history_button') and self.history_button:
            self.history_button.config(state=state)
        if hasattr(self, 'meter_type_info_btn') and self.meter_type_info_btn:
            self.meter_type_info_btn.config(state=state)

    def show_meter_info(self):
        #Show information about the current meter type
        if not self.current_meter_id:
            return
            
        meter = self.meters[self.current_meter_id]
        info = {
            "🏠 Residential": "Rate: Rs. 10.7/unit (homes)",
            "🏢 Commercial": "Rate: Rs. 13.5/unit (shops, offices)",
            "🏭 Industrial": "Rate: Rs. 25.5/unit (factories)"
        }.get(meter.meter_type, "Unknown meter type")
        
        messagebox.showinfo("Meter Info", info)

    def calculate_bill(self):
        #Calculate and display the current bill
        if not self.current_meter_id:
            messagebox.showerror("Error", "No meter selected")
            return
            
        meter = self.meters[self.current_meter_id]
        bill_data = meter.calculate_bill()
        
        self.previous_entry.config(state="normal")
        self.previous_entry.delete(0, tk.END)
        self.previous_entry.insert(0, f"{meter.previous_reading:.2f}")
        self.previous_entry.config(state="readonly")
        
        messagebox.showinfo(
            "🔌 Electricity Bill",
            f"Units Used: {bill_data['units_used']:.2f}\n"
            f"Rate: Rs. {bill_data['rate']}/unit\n"
            f"Total Bill: Rs. {bill_data['bill']:.2f}"
        )

    def show_last_bill(self):
        #Display the most recent bill in a popup
        if not self.current_meter_id:
            messagebox.showerror("Error", "No meter selected")
            return
            
        meter = self.meters[self.current_meter_id]
        
        if not meter.bill_history:
            messagebox.showinfo("Info", "No billing history for this meter")
            return
            
        last_bill = meter.bill_history[-1]
        message = (
            f"Previous: {last_bill['previous']:.2f}\n"
            f"Current: {last_bill['current']:.2f}\n"
            f"Units: {last_bill['units']:.2f}\n"
            f"Rate: Rs. {last_bill['rate']}/unit\n"
            f"Bill: Rs. {last_bill['bill']:.2f}"
        )
        self.show_bill_popup(message)

    def show_bill_history(self):
        #Display complete billing history
        if not self.current_meter_id:
            messagebox.showerror("Error", "No meter selected")
            return
            
        meter = self.meters[self.current_meter_id]
        
        if not meter.bill_history:
            messagebox.showinfo("Bill History", "No history available for this meter.")
            return
            
        history_text = f"📜 Bill History for {meter.meter_id} - {meter.building_name}:\n\n"
        for idx, bill in enumerate(reversed(meter.bill_history), start=1):
            history_text += (
                f"Bill {idx}:\n"
                f"Previous: {bill['previous']:.2f}, Current: {bill['current']:.2f},\n"
                f"Units: {bill['units']:.2f}, Rate: Rs.{bill['rate']}/unit,\n"
                f"Total: Rs.{bill['bill']:.2f}\n\n"
            )
            
        messagebox.showinfo("📊 Bill History", history_text.strip())

    def clear_fields(self):
        #Reset the display fields
        if self.current_meter_id:
            meter = self.meters[self.current_meter_id]
            self.previous_entry.config(state="normal")
            self.previous_entry.delete(0, tk.END)
            self.previous_entry.insert(0, f"{meter.previous_reading:.2f}")
            self.previous_entry.config(state="readonly")
            
            self.current_entry.config(state="normal")
            self.current_entry.delete(0, tk.END)
            self.current_entry.insert(0, f"{meter.current_reading:.2f}")
            self.current_entry.config(state="readonly")

    def show_bill_popup(self, text):
        #Show a sliding bill notification
        if self.popup:
            self.popup.destroy()
            
        self.popup = tk.Toplevel(self.root)
        self.popup.overrideredirect(True)
        self.popup.configure(bg="#2ecc71")
        
        label = tk.Label(
            self.popup, text=text,
            font=("Segoe UI", 12, "bold"), bg="#2ecc71", fg="white",
            justify="left", wraplength=280
        )
        label.pack(padx=20, pady=20)
        
        self.popup.update_idletasks()
        
        width = label.winfo_reqwidth() + 40
        height = label.winfo_reqheight() + 40
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width
        y_target = self.root.winfo_y() + 250
        x_target = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        
        self.popup.geometry(f"{width}x{height}+{x}+{y_target}")
        
        def slide():
            current_x = self.popup.winfo_x()
            if current_x > x_target:
                current_x -= 20
                self.popup.geometry(f"{width}x{height}+{current_x}+{y_target}")
                self.root.after(10, slide)
            else:
                self.popup.geometry(f"{width}x{height}+{x_target}+{y_target}")
                self.root.after(3000, self.popup.destroy)
                
        slide()

    def update_displayed_reading(self):
        #Continuously update the current reading display
        if self.current_meter_id:
            meter = self.meters[self.current_meter_id]
            self.current_entry.config(state="normal")
            self.current_entry.delete(0, tk.END)
            self.current_entry.insert(0, f"{meter.current_reading:.2f}")
            self.current_entry.config(state="readonly")
        self.root.after(500, self.update_displayed_reading)

    def auto_calculate_bill_loop(self):
        #Auto-calculate bill every hour (simulated)
        if self.current_meter_id:
            self.calculate_bill()
        self.root.after(3600000, self.auto_calculate_bill_loop)

    def animate_title(self):
        #Animate the title bar color
        current = "#0077b6" if self.title_label["bg"] == "#00b4d8" else "#00b4d8"
        self.title_label.config(bg=current)
        self.root.after(300, self.animate_title)

    def on_window_resize(self, event):
        #Handle window resize events
        if event.widget == self.root:
            if self.root.state() == "zoomed":
                self.title_label.pack_configure(pady=(10, 20))
            else:
                self.title_label.pack_configure(pady=(0, 10))

    def on_close(self):
       #Clean up resources when closing
        for meter in self.meters.values():
            meter.stop_simulation()
        self.root.destroy()

def main():
    #Main application entry pointS
    root = tk.Tk()
    app = SmartMeterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()