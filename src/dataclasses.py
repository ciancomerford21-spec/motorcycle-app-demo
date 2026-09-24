from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).with_name("motorcycle_data.json")

@dataclass
class MaintenanceItem:
    name: str
    interval_km: int
    last_service_date: date
    last_service_km: int

    @property
    def next_service_km(self) -> int:
        return self.last_service_km + self.interval_km

    def km_remaining(self, current_km) -> int:
        return self.next_service_km - current_km

    def is_due(self, current_km) -> bool:
        return current_km >= self.next_service_km

@dataclass
class ServiceRecord:
    item_name: str
    service_date: str
    mileage: int

@dataclass
class MotorcycleInfo:
    make: str
    model: str
    year: int
    current_mileage: int
