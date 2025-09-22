from sqlmodel import Field, SQLModel, Relationship
from typing import List
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON

    
class TimeSectorsBase(BaseModel):
    time: str
    sectors: List[str] = []

class MaintenanceEventBase(BaseModel):
    week_number: int
    company: str
    day: str
    province: str
    maintenance: List[TimeSectorsBase] = []
    
class MaintenanceEvent(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    week_number: int
    company: str
    day: str
    province: str
    maintenance: List['TimeSectors'] = Relationship(back_populates = 'maintenance_event')
    
class TimeSectors(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    maintenance_event_id: int = Field(foreign_key = 'maintenanceevent.id')
    time: str
    sectors: List[str] = Field(sa_column = Column(JSON))
    maintenance_event: MaintenanceEvent = Relationship(back_populates = 'maintenance')