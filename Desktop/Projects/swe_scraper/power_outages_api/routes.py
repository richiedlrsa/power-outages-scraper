from fastapi import FastAPI, Depends
from sqlmodel import Session, select, create_engine
from typing import Annotated, List
from power_outages_api import MaintenanceEvent, TimeSectors, MaintenanceEventBase
from sqlalchemy.orm import selectinload, joinedload
from datetime import date

app = FastAPI()
engine = create_engine('sqlite:///outages.db', connect_args = {'check_same_thread': False})

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]

@app.get('/outages/', response_model = List[MaintenanceEventBase])
def outages(db: SessionDep):
    statement = select(MaintenanceEvent). \
                where(MaintenanceEvent.week_number == date.today().isocalendar()[1]). \
                where(MaintenanceEvent.day.ilike(f'%{date.today().year}%')). \
                options(selectinload(MaintenanceEvent.maintenance))
    outages = db.exec(statement).all()
    
    return outages