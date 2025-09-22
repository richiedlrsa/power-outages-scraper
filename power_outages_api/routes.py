from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import Annotated, List
from power_outages_api import MaintenanceEvent, MaintenanceEventBase, engine
from sqlalchemy.orm import selectinload
from datetime import date
from main import run_scraper
from sqlalchemy.exc import ProgrammingError

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]

@app.post('/api/run-scraper')
def trigger_scraper():
    try:
        run_scraper()
        return {'status': 'sucess', 'message': 'Scraper ran successfully!'}
    except Exception as e:
        print(f'Error during scraping process: {e}')
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))

@app.get('/outages/', response_model = List[MaintenanceEventBase])
def outages(db: SessionDep, page: int | None = None, limit: int | None = None):
    try:
        statement = select(MaintenanceEvent). \
                    where(MaintenanceEvent.week_number == date.today().isocalendar()[1]). \
                    where(MaintenanceEvent.day.ilike(f'%{date.today().year}%')). \
                    order_by(MaintenanceEvent.province, MaintenanceEvent.day). \
                    options(selectinload(MaintenanceEvent.maintenance))
        outages = db.exec(statement).all()
    except ProgrammingError:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Database table does not exist.")
    
    if not outages:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Data not found.")
    
    if limit:
        if page:
            start = (page - 1)
            end = page * limit
            
            return outages[start:end]
        else:
            return outages[:10]
    else:
        return outages