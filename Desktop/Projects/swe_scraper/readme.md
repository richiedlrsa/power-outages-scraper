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

    * The script will look for a key named 'GEMINI_API_KEY'. Please do not use a different name.

## How to use

To run a scraper, execute the corresponding Python file. The script will print the scheduled maintenance information to your terminal.

Examples

```
# get outages for edesur
python edesur.py

# get outages for edeeste
python edeeste.py

# get outages for edenorte
python edenorte.py
```

Sample output
```
[
    {
    'day': day_of_outage
    'province': affected_province
    'maintenance': [
        {
        'time': time_of_outage
        'sectors': [list_of_affected_sectors]
        }
    ]
    }
]
```