# Scheduled Power Outages Scraper
A script to scrape power outages in the Dominican Republic.

## Description 

Unexpected power outages are a huge painpoint in the Dominican Republic. This script allows users to obtain information from official government websites regarding power outages in their area, allowing them to prepare accordingly. This information includes the day, time, province, and sectors the power outage will occur in. 

## Requirements
* Python 3.8+
* pip (Package Installer for Python)
* Git

## Set up
1. **Clone the repository**:
```
git clone https://github.com/richiedlrsa/power-outages-scraper
cd swe_scraper/power_outages_api
```
2. Create and activate virtual environment (Recommended):

For macOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```

For Windows
```
python -m venv venv
.\venv\Scripts\activate
```

3. **Install required packages**:
```
pip install -r requirements.txt
```

4. Sign up for a Google Gemini account and obtain your API key
    * Set the key as an environment variable
    for macOS/Linux

    ```
    export GEMINI_API_KEY=<INSERT KEY HERE>
    ```

    for Windows

    ```
    set GEMINI_API_KEY=<INSERT KEY HERE>
    ```

    * The script will look for a key named 'GEMINI_API_KEY'. Please do not use a different name.

## How to use

1. **Populate the Database**

Run the ```main.py``` script to scrape the latest data from all providers and save it to the outages.db SQLite database.

```
python main.py
```

2. Run the API Server

Once the database is populated, start the FastAPI server using FastAPI

```
fastapi dev routes.py
```

The API will now be running on http://127.0.0.1:8000/

## API Endpoints

You can access the interactive API documentation at http://127.0.0.1:8000/docs

Get All Outages
* **URL:** /outages/
* **Method:** GET
* **Description:** Retrieves all scheduled maintenance events from the database for the current week.
* **Sample Response:**

```
[
    {
    'id': 1,
    'week': 39,
    'day': "lunes 22 de septiembre, 2025",
    'province': "Santo Domingo",
    'maintenance': [
        {
        'time': "9:00 AM - 1:00 PM",
        'sectors': [
            "Piantini",
            "Naco",
            "Bella Vista"
        ]
        }
    ]
    }
]
```