import json
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, simpledialog, ttk

from .dataclasses import (
    DATA_FILE,
    MaintenanceItem,
    MotorcycleInfo,
    ServiceRecord,
    asdict,
)


class Tracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Motorcycle Maintenance Tracker")
        self.root.geometry("1280x720")
        self.root.minsize(750, 500)

        self.motorcycle = MotorcycleInfo(
            make="Yamaha",
            model="R6",
            year=2003,
            current_mileage=0,
        )
        self.maintenance = []
        self.history = []

        self.load_data()
        self.create_widgets()
        self.refresh()

    def save_data(self):
        data = {
            "motorcycle": {
                "make": self.motorcycle.make,
                "model": self.motorcycle.model,
                "year": self.motorcycle.year,
                "current_mileage": self.motorcycle.current_mileage,
            },
            "maintenance": [
                {
                    **asdict(item),
                    "last_service_date": item.last_service_date.isoformat(),
                }
                for item in self.maintenance
            ],
            "history": [asdict(record) for record in self.history],
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_data(self):
        if not DATA_FILE.exists():
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            motorcycle = data["motorcycle"]
            self.motorcycle.make = motorcycle["make"]
            self.motorcycle.model = motorcycle["model"]
            self.motorcycle.year = motorcycle["year"]
            self.motorcycle.current_mileage = motorcycle.get(
                "current_mileage",
                motorcycle.get("current_km", self.motorcycle.current_mileage),
            )

            self.maintenance = [
                MaintenanceItem(
                    name=item["name"],
                    interval_km=item["interval_km"],
                    last_service_date=self._parse_date(item["last_service_date"]),
                    last_service_km=item["last_service_km"],
                )
                for item in data.get("maintenance", [])
            ]
            self.history = [
                ServiceRecord(**record) for record in data.get("history", [])
            ]
        except Exception as error:
            messagebox.showerror(
                "Load Error",
                f"Could not load saved data:\n{error}",
            )

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        return datetime.strptime(value, "%Y-%m-%d").date()

    def add_maintenance_item(self):
        name = simpledialog.askstring(
            "Maintenance Item",
            "Enter maintenance item name:",
        )
        if not name:
            return

        interval = simpledialog.askinteger(
            "Service Interval",
            "Enter service interval in km:",
            minvalue=1,
        )
        if not interval:
            return

        self.maintenance.append(
            MaintenanceItem(
                name=name,
                interval_km=interval,
                last_service_date=date.today(),
                last_service_km=self.motorcycle.current_mileage,
            )
        )
        self.save_data()
        self.refresh()

    def create_widgets(self):
        header = ttk.Frame(self.root, padding=15)
        header.pack(fill="x")

        self.title_label = ttk.Label(
            header,
            text="Motorcycle Maintenance Tracker",
            font=("Arial", 20, "bold"),
        )
        self.title_label.pack(side="left")

        self.bike_label = ttk.Label(
            header,
            text="",
            font=("Arial", 12),
        )
        self.bike_label.pack(side="right")

        mileage_frame = ttk.LabelFrame(
            self.root,
            text="Motorcycle",
            padding=15,
        )
        mileage_frame.pack(fill="x", padx=15, pady=5)

        self.mileage_label = ttk.Label(
            mileage_frame,
            text="",
            font=("Arial", 14, "bold"),
        )
        self.mileage_label.pack(side="left")

        ttk.Button(
            mileage_frame,
            text="Update Mileage",
            command=self.update_mileage,
        ).pack(side="right")

        maintenance_frame = ttk.LabelFrame(
            self.root,
            text="Maintenance",
            padding=10,
        )
        maintenance_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = (
            "name",
            "last_service",
            "next_service",
            "remaining",
            "status",
        )
        self.tree = ttk.Treeview(
            maintenance_frame,
            columns=columns,
            show="headings",
        )

        self.tree.heading("name", text="Maintenance")
        self.tree.heading("last_service", text="Last Service")
        self.tree.heading("next_service", text="Next Service")
        self.tree.heading("remaining", text="Remaining")
        self.tree.heading("status", text="Status")

        self.tree.column("name", width=180)
        self.tree.column("last_service", width=130)
        self.tree.column("next_service", width=130)
        self.tree.column("remaining", width=130)
        self.tree.column("status", width=120)
        self.tree.pack(fill="both", expand=True)

        button_frame = ttk.Frame(self.root, padding=15)
        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="Add Service",
            command=self.add_service,
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Service History",
            command=self.show_history,
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Add Maintenance Item",
            command=self.add_maintenance_item,
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Save",
            command=self.save_data,
        ).pack(side="right", padx=5)

    def refresh(self):
        self.bike_label.config(
            text=f"{self.motorcycle.year} "
            f"{self.motorcycle.make} {self.motorcycle.model}"
        )
        self.mileage_label.config(
            text=f"Current Mileage: {self.motorcycle.current_mileage:,} km"
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for maintenance in self.maintenance:
            remaining = maintenance.km_remaining(self.motorcycle.current_mileage)
            status = "SERVICE DUE" if remaining <= 0 else "OK"
            if remaining <= 0:
                remaining_text = f"{abs(remaining):,} km overdue"
            else:
                remaining_text = f"{remaining:,} km"

            self.tree.insert(
                "",
                "end",
                values=(
                    maintenance.name,
                    f"{maintenance.last_service_km:,} km",
                    f"{maintenance.next_service_km:,} km",
                    remaining_text,
                    status,
                ),
            )

    def update_mileage(self):
        new_mileage = simpledialog.askinteger(
            "Update Mileage",
            "Enter current motorcycle mileage:",
            initialvalue=self.motorcycle.current_mileage,
            minvalue=self.motorcycle.current_mileage,
        )
        if new_mileage is not None:
            self.motorcycle.current_mileage = new_mileage
            self.save_data()
            self.refresh()

    def add_service(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select a maintenance item first.",
            )
            return

        item_index = self.tree.index(selected[0])
        maintenance = self.maintenance[item_index]
        today = date.today()
        maintenance.last_service_date = today
        maintenance.last_service_km = self.motorcycle.current_mileage
        self.history.append(
            ServiceRecord(
                maintenance.name,
                today.isoformat(),
                self.motorcycle.current_mileage,
            )
        )
        self.save_data()
        self.refresh()
        messagebox.showinfo(
            "Service Recorded",
            f"{maintenance.name} serviced at "
            f"{self.motorcycle.current_mileage:,} km.",
        )

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Service History")
        history_window.geometry("600x400")

        tree = ttk.Treeview(
            history_window,
            columns=("item", "date", "mileage"),
            show="headings",
        )
        tree.heading("item", text="Service")
        tree.heading("date", text="Date")
        tree.heading("mileage", text="Mileage")
        tree.column("item", width=250)
        tree.column("date", width=150)
        tree.column("mileage", width=150)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for record in self.history:
            tree.insert(
                "",
                "end",
                values=(
                    record.item_name,
                    record.service_date,
                    f"{record.mileage:,} km",
                ),
            )
