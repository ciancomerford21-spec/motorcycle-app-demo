from dataclasses import dataclass
from datetime import date

@dataclass
class MaintenanceItem:
    name: str
    interval_km: int
    last_service_date: date
    last_service_km: int

    @property
    def next_service_km(self) -> int:
        return self.next_service_km + self.interval_km

    def km_remaining(self, current_km) -> int:
        return self.next_service_km - current_km

    def is_due(self, current_km) -> bool:
        return current_km >= self.next_service_km

@dataclass
class ServiceRecord:
    item_name: str
    service_date: str
    mileage: int
