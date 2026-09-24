import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import json
import os

from .dataclasses import DATA_FILE, MaintenanceItem, MotorcycleInfo, ServiceRecord

class Tracker:

    def __init__(self, root):

        self.root = root
        self.root.title("Motorcycle Maintenance Tracker")
        self.root.geometry("1280x720")
        self.root.minsize(750,500)

        self.motorcycle = MotorcycleInfo(make="Yamaha",
                                    model="R6", 
                                    year=2003,
                                    current_mileage=0
                                )

        self.maintenance = []
        self.history = []

        # Demo data
        self.maintenance.append(MaintenanceItem(
            "Engine Oil",
            6000,
            "2026-06-01",
            6000,
        ))

        # Demo data
        self.history.append(ServiceRecord(
            "Engine Oil",
            "2025-12-12",
            0
        ))

        self.load_data()
        self.create_widgets()
        self.refresh()

    def load_data(self):
        if not os.path.exists(
            DATA_FILE
        ):
            print("No file")
            return

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            motorcycle = data["motorcycle"]

            self.motorcycle.make = motorcycle["make"]
            self.motorcycle.model = motorcycle["model"]
            self.motorcycle.year = motorcycle["year"]
            self.motorcycle.current_mileage = motorcycle["current_mileage"]

            self.maintenance = [
                MaintenanceItem(**item)
                for item in data["maintenance"]
            ]

            self.history = [
                ServiceRecord(**record)
                for record in data["history"]
            ]

        except Exception as error:

            messagebox.showerror(
                "Load Error",
                f"Could not load saved data:\n{error}"
            )

    def create_widgets(self):
        pass

    def refresh(self):
        pass
