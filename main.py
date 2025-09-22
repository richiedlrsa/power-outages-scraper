import asyncio
from power_outages_api import Edeeste, Edesur, Edenorte, MaintenanceEvent, TimeSectors, engine, ModelError
from sqlmodel import SQLModel, Session, delete
from datetime import date
from sqlalchemy.exc import ProgrammingError

async def get_outages(company):
    '''
    company: Edeeste, Edesur, or Edenorte class
    Fetches the data for the corresponding company and adds it to the database
    returns a co-routine
    '''
    while True:
        print(f'Fetching data for {company.__name__}...')
        try:
            outages = await asyncio.to_thread(company)
        except ModelError:
            # ModelError is a server-side error. Keep trying until successful.
            print(f'Error fetching data from {company.__name__}. Retrying in 30 minutes.')
            await asyncio.sleep(1800)
        except Exception as e:
            print(f'Error fetching data from {company.__name__}:', e)
            break
        else:
            print(f'Creating models for {company.__name__}...')
            await asyncio.to_thread(create_models, outages.data)
            print(f'Models for {company.__name__} created successfully!')
            break

async def main() -> None:
    '''
    Runs the async function get_outages() with the valid companies concurrently
    '''
    coros = [get_outages(company) for company in (Edeeste, Edesur, Edenorte)]
    
    await asyncio.gather(*coros)

def create_db() -> None:
    '''
    Creates the database
    '''
    SQLModel.metadata.create_all(engine)

        
def create_models(outages) -> None:
    '''
    outages: list of outages for the corresponding company
    creates table objects and adds them to the database
    '''
    
    with Session(engine) as session:
        
        # we delete the data from the current week to update it with fresh, updated data
        
        # first ensure that we have updated data for the company before deleting it
        
        companies_to_delete = [company for company in ('Edeeste', 'Edesur', 'Edenorte') if any(company in outage.values() for outage in outages)]
        try:
            session.exec(delete(MaintenanceEvent). \
                where(MaintenanceEvent.week_number == date.today().isocalendar()[1],
                MaintenanceEvent.company.in_(companies_to_delete)))
        except ProgrammingError:
            print('Skipping deletion. Table does not exist.')
    
        for outage in outages:
            outage_obj = MaintenanceEvent(week_number = outage['week_number'], company = outage['company'], day = outage['day'], province = outage['province'])
            for maintenance in outage['maintenance']:
                maintenance_obj = TimeSectors(time = maintenance['time'], sectors = maintenance['sectors'])

                outage_obj.maintenance.append(maintenance_obj)
            
            session.add(outage_obj)
            
        session.commit()
        
if __name__ == '__main__':
    create_db()
    asyncio.run(main())
    print("Scraping process finished.")