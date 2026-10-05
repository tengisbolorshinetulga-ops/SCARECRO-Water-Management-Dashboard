import requests 
import pandas as pd
from datetime import date, timedelta
from pymongo import MongoClient 
from dotenv import load_dotenv
import os

def main():
    # Load values from .env file if one exists
    #load_dotenv()
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    print(f"API KEY: {os.getenv('OPENET_API_KEY')}")
    print(f"MONGO: {os.getenv('MONGODB_URI')}")

    # Read Secret values from enviroment variables
    # This is safer than writing them directly in the code
    mongo_uri = os.getenv("MONGODB_URI")
    openet_api_key = os.getenv("OPENET_API_KEY")

    if not mongo_uri :
        raise ValueError("Missing MONGODB_URI in enviroment variable")
    if not openet_api_key :
        raise ValueError("Missing OPENET_API_KEY in enviroment variable")
    
    # Connect to MongoDB 
    client = MongoClient(mongo_uri)
    database = client["SCARECRO"]
    collection = database["ET_data"]

    # Calculate the dates automatically
    today = date.today()
    safe_end = today - timedelta(days=4)
    two_weeks_ago = today - timedelta(days=14)

    # OpenET authorazation header 
    headers = {"Authorization" : openet_api_key}

    # Store all location in same dictionary
    locations = {
        "SOAC Sandpoint" : {"coords" : [-116.5541, 48.3222], "model" : "Ensemble"},
        "Harbor Center" : {"coords" : [-116.7969, 47.6834], "model" : "SSEBop"},
        "Deary forest" : {"coords" : [-116.5562, 46.8801], "model" : "eeMETRIC"},
    }

    # go through each site by one time
    for location_name, info in locations.items() :
        print(f"\nfetching data for {location_name}...")

        # Build the request body for this site 
        data_request = { 
            "date_range" : [two_weeks_ago.isoformat(), safe_end.isoformat()],
            "interval" : "daily",
            "units" : "mm",
            "variable" : "ET",
            "reference_et" : "gridMET",
            "file_format" : "JSON",
            "model" : info["model"],
            "geometry" : info["coords"],
            
    }
        response = requests.post(
            headers = headers,
            json = data_request,
            url = "https://openet-api.org/raster/timeseries/point",
            timeout = 120,
        )
        print(response.status_code),
        print(response.text),
    
        # Stop early if request failed
        response.raise_for_status()

        # Convert the response into Python data
        data = response.json()

        # Show the data as a table so you can inspect it 
        df = pd.DataFrame(data)
        print(df.head())
        
        

        # Save each row into MongoDB
        for record in data:
            record["location"] = location_name
            record["model"] = info["model"]
            record["units"] = "mm"

            collection.update_one(
            {
                    "location" : record["location"],
                    "time" : record["time"],
                    "model" : record["model"],

        
                }, 
                {"$set":record},
                upsert=True,
            )

        print(f"Inserted or updated {len(data)} record for {location_name}")

if __name__ == "__main__":
    main()

