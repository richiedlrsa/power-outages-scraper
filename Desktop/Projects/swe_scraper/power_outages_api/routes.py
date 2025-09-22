from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, create_engine
from typing import Annotated, List
from power_outages_api import MaintenanceEvent, MaintenanceEventBase
from sqlalchemy.orm import selectinload
from datetime import date
import os

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

engine = create_engine(os.getenv("DATABASE_URL"), connect_args = {'check_same_thread': False})

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]

@app.post('/api/run-scraper')
def trigger_scraper(secret: str):
    CRON_SECRET = os.getenv("CRON_SECRET")
    if not CRON_SECRET or secret != CRON_SECRET:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid secret.")
    
    try:
        run_scraper()
        return {'status': 'sucess', 'message': 'Scraper ran successfully!'}
    except Exception as e:
        print(f'Error during scraping process: {e}')
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))

@app.get('/outages/', response_model = List[MaintenanceEventBase])
def outages(db: SessionDep, page: int | None = None, limit: int | None = None):
    statement = select(MaintenanceEvent). \
                where(MaintenanceEvent.week_number == date.today().isocalendar()[1]). \
                where(MaintenanceEvent.day.ilike(f'%{date.today().year}%')). \
                order_by(MaintenanceEvent.province, MaintenanceEvent.day). \
                options(selectinload(MaintenanceEvent.maintenance))
    outages = db.exec(statement).all()
    
    if not outages:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Data not found.")
    
    if limit:
        if page:
            start = (page - 1) * limit
            end = page * limit
            
            return outages[start:end]
        else:
            return outages[:10]
    else:
        return outages