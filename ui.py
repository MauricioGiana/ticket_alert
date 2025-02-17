import tkinter as tk
from tkinter import ttk
from check_tickets import get_report
import form_utils
from utils import get_locations

locations = get_locations()
location_names = [location["name"] for location in locations]
locations_id_map = {location["id"]: location['name'] for location in locations}
locations_name_map = {location["name"]: location["id"] for location in locations}

def clear_fields():
    from_select.set("")
    to_select.set("")
    from_date_entry.delete(0, tk.END)
    quantity_select.set("")

def schedule_consult():
    print("Consult scheduled!")

def make_consult(consults):
    try:
        report = get_report(consults)
        report_window = tk.Toplevel(root)
        report_window.title("Reporte")

        report_text = tk.Text(report_window, height=20, width=50)
        report_text.pack()

        for ticket_report in report:
            report_text.insert(tk.END, f"Origen: {ticket_report['origin']}\n")
            report_text.insert(tk.END, f"Destino: {ticket_report['destination']}\n")
            report_text.insert(tk.END, f"Rango: {ticket_report['date_range']}\n")
            report_text.insert(tk.END, f"Fechas disponibles:\n")
            for date in ticket_report['dates']:
                report_text.insert(tk.END, f"{date}\n")
            if not ticket_report['dates']:
                report_text.insert(tk.END, ' -- No hay -- \n')
            report_text.insert(tk.END, "\n")

        report_window.mainloop()
    except Exception as e:
        print(f"Error: {str(e)}")
        error_window = tk.Toplevel(root)
        error_window.title("Error Details")
        tk.Label(error_window, text=f"Error: {str(e)}", fg="red").pack(pady=10)

def make_current_consult():
    consult = [
        {
            "origin_id": locations_name_map[from_select.get()],
            "destination_id": locations_name_map[to_select.get()],
            "from_date": from_date_entry.get(),
            "to_date": to_date_entry.get(),
            "quantity": quantity_select.get()
        }
    ]    
    make_consult(consult)

def make_saved_consults():
    saved_consults = form_utils.get_saved_consults()
    make_consult(saved_consults)

def update_saved_consults():
    """Refresh the displayed list of saved consults."""
    for widget in saved_consults_frame.winfo_children():
        widget.destroy()
    
    for i, consult in enumerate(form_utils.get_saved_consults()):
        tk.Label(saved_consults_frame, text=f"{locations_id_map[consult['origin_id']]} -> {locations_id_map[consult['destination_id']]} |").grid(row=i, column=0, pady=2, sticky="w")
        tk.Label(saved_consults_frame, text=F"{consult['from_date']} a {consult['to_date']} |").grid(row=i, column=1, pady=2, sticky="w")
        tk.Label(saved_consults_frame, text=f"{consult['quantity']}").grid(row=i, column=2, pady=2, sticky="w")
        delete_button = tk.Button(saved_consults_frame, text=" X ", command=lambda idx=i: delete_consult(idx))
        delete_button.grid(row=i, column=3, padx=5, pady=2)

def save_consult():
    consult = {
        "origin_id": locations_name_map[from_select.get()],
        "destination_id": locations_name_map[to_select.get()],
        "from_date": from_date_entry.get(),
        "to_date": to_date_entry.get(),
        "quantity": quantity_select.get()
    }
    form_utils.save_consult(consult)
    update_saved_consults()

def delete_consult(index):
    form_utils.delete_consult(index)
    update_saved_consults()

def toggle_saved_consults():
    if saved_consults_frame.winfo_ismapped():
        saved_consults_frame.grid_forget()
    else:
        saved_consults_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        update_saved_consults()

def clear_saved_consults():
    form_utils.clear_consults('saved')
    update_saved_consults()

# Main window
root = tk.Tk()
root.title("Consulta tickets fácil :)")

# Button to toggle saved consults visibility
toggle_button = tk.Button(root, text="Consultas guardadas 👀", command=toggle_saved_consults)
toggle_button.grid(row=0, column=0, columnspan=2, pady=10)

saved_consults_frame = tk.Frame(root)
saved_consults_frame.grid_forget()

update_saved_consults()

# Divider
tk.Label(root, text="---").grid(row=2, column=0, columnspan=2, pady=10)

# Dropdowns for countries
tk.Label(root, text="Origen:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
from_select = ttk.Combobox(root, values=location_names)
from_select.grid(row=3, column=1, padx=5, pady=5)

tk.Label(root, text="Destino:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
to_select = ttk.Combobox(root, values=location_names)
to_select.grid(row=4, column=1, padx=5, pady=5)

# From date input
tk.Label(root, text="Buscar desde:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
from_date_entry = tk.Entry(root)
from_date_entry.grid(row=5, column=1, padx=5, pady=5)

# To date input
tk.Label(root, text="Buscar hasta:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
to_date_entry = tk.Entry(root)
to_date_entry.grid(row=6, column=1, padx=5, pady=5)

# Quantity dropdown
tk.Label(root, text="Cantidad de pasajes:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
quantity_select = ttk.Combobox(root, values=["uno", "dos"])
quantity_select.grid(row=7, column=1, padx=5, pady=5)

# Buttons
clear_button = tk.Button(root, text="Limpiar consultas", command=clear_saved_consults)
clear_button.grid(row=8, column=0, padx=5, pady=10, sticky="ew")

save_consult_button = tk.Button(root, text="Guardar consulta", command=save_consult)
save_consult_button.grid(row=8, column=1, padx=5, pady=10, sticky="ew")

view_consults_button = tk.Button(root, text="Reporte de consultas guardadas", command=make_saved_consults)
view_consults_button.grid(row=9, column=0, padx=5, pady=10, sticky="ew")

submit_button = tk.Button(root, text="Consultar", command=make_current_consult)
submit_button.grid(row=9, column=1, padx=5, pady=10, sticky="ew")

# Start the Tkinter event loop
root.mainloop()
